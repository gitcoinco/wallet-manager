# -*- coding: utf-8 -*-
"""Define the Grant models.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

import pytz
import requests
from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel, Token
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from grants.utils import get_upload_filename, is_grant_team_member
from townsquare.models import Favorite
from web3 import Web3

logger = logging.getLogger(__name__)


class GrantQuerySet(models.QuerySet):
    """Define the Grant default queryset and manager."""

    def active(self):
        """Filter results down to active grants only."""
        return self.filter(active=True)

    def inactive(self):
        """Filter results down to inactive grants only."""
        return self.filter(active=False)

    def keyword(self, keyword):
        """Filter results to all Grant objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, description, and reference URL by.

        Returns:
            dashboard.models.GrantQuerySet: The QuerySet of grants filtered by keyword.

        """
        if not keyword:
            return self
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(reference_url__icontains=keyword)
        )


class GrantCategory(SuperModel):

    category = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        help_text=_('Grant Category'),
    )

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"{self.category}"


class GrantType(SuperModel):

    name = models.CharField(unique=True, max_length=15, help_text="Grant Type")
    label = models.CharField(max_length=25, null=True, help_text="Display Name")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Is Grant Type currently active")
    categories  = models.ManyToManyField(
        GrantCategory,
        help_text="Grant Categories associated with Grant Type"
    )

    def __str__(self):
        """Return the string representation."""
        return f"{self.name}"

    @property
    def clrs(self):
        return GrantCLR.objects.filter(grant_filters__grant_type=str(self.pk))

    @property
    def active_clrs(self):
        return GrantCLR.objects.filter(is_active=True, grant_filters__grant_type=str(self.pk))

    @property
    def active_clrs_sum(self):
        return sum(self.active_clrs.values_list('total_pot', flat=True))


class GrantCLR(SuperModel):
    round_num = models.CharField(max_length=15, help_text="CLR Round Number")
    is_active = models.BooleanField(default=False, db_index=True, help_text="Is CLR Round currently active")
    start_date = models.DateTimeField(help_text="CLR Round Start Date")
    end_date = models.DateTimeField(help_text="CLR Round Start Date")
    grant_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grants allowed in this CLR round"
    )
    subscription_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grant Subscription to be allowed in this CLR round"
    )
    collection_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grant Collections to be allowed in this CLR round"
    )
    verified_threshold = models.DecimalField(help_text="Verfied CLR Threshold",
        default=25.0,
        decimal_places=2,
        max_digits=5
    )
    unverified_threshold = models.DecimalField(help_text="Unverified CLR Threshold",
        default=5.0,
        decimal_places=2,
        max_digits=5
    )
    total_pot = models.DecimalField(help_text="CLR Pot",
        default=0,
        decimal_places=2,
        max_digits=10
    )
    contribution_multiplier = models.DecimalField(
        help_text="A contribution multipler to be applied to each contribution",
        default=1.0,
        decimal_places=4,
        max_digits=10,
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        max_length=500,
        help_text=_('The Grant CLR round image'),
    )

    def __str__(self):
        return f"{self.round_num}"

    @property
    def grants(self):
        return Grant.objects.filter(**self.grant_filters).filter(is_clr_eligible=True)


class Grant(SuperModel):
    """Define the structure of a Grant."""

    class Meta:
        """Define the metadata for Grant."""

        ordering = ['-created_on']


    active = models.BooleanField(default=True, help_text=_('Whether or not the Grant is active.'))
    grant_type = models.ForeignKey(GrantType, on_delete=models.CASCADE, null=True, help_text="Grant Type")
    title = models.CharField(default='', max_length=255, help_text=_('The title of the Grant.'))
    slug = AutoSlugField(populate_from='title')
    description = models.TextField(default='', blank=True, help_text=_('The description of the Grant.'))
    description_rich = models.TextField(default='', blank=True, help_text=_('HTML rich description.'))
    reference_url = models.URLField(blank=True, help_text=_('The associated reference URL of the Grant.'))
    github_project_url = models.URLField(blank=True, null=True, help_text=_('Grant Github Project URL'))
    is_clr_eligible = models.BooleanField(default=True, help_text="Is grant eligible for CLR")
    link_to_new_grant = models.ForeignKey(
        'grants.Grant',
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('Link to new grant if migrated')
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        max_length=500,
        help_text=_('The Grant logo image.'),
    )
    logo_svg = models.FileField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('The Grant logo SVG.'),
    )
    # TODO-GRANTS: rename to eth_payout_address
    admin_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The wallet address where subscription funds will be sent.'),
    )
    zcash_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The zcash wallet address where subscription funds will be sent.'),
    )
    # TODO-GRANTS: remove
    contract_owner_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address that owns the subscription contract and is able to call endContract()'),
    )
    amount_received_in_round = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The amount received in DAI this round.'),
    )
    monthly_amount_subscribed = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The monthly subscribed to by contributors USDT/DAI.'),
    )
    amount_received = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The total amount received for the Grant in USDT/DAI.'),
    )
    # TODO-GRANTS: remove
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Grant.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='',
        help_text=_('The token symbol to be used with the Grant.'),
    )
    # TODO-GRANTS: remove
    contract_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The contract address of the Grant.'),
    )
    # TODO-GRANTS: remove
    deploy_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for contract deployment.'),
    )
    # TODO-GRANTS: remove
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for endContract.'),
        blank=True,
    )
    contract_version = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=3,
        help_text=_('The contract version the Grant.'),
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        help_text=_('The Grant metadata. Includes creation and last synced block numbers.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Grant contract resides.'),
        db_index=True
    )
    required_gas_price = models.DecimalField(
        default='0',
        decimal_places=0,
        max_digits=50,
        help_text=_('The required gas price for the Grant.'),
    )
    admin_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_admin',
        on_delete=models.CASCADE,
        help_text=_('The Grant administrator\'s profile.'),
        null=True,
    )
    team_members = models.ManyToManyField(
        'dashboard.Profile',
        related_name='grant_teams',
        help_text=_('The team members contributing to this Grant.'),
    )
    image_css = models.CharField(default='', blank=True, max_length=255, help_text=_('additional CSS to attach to the grant-banner img.'))
    amount_received_with_phantom_funds = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=20,
        help_text=_('The fundingamount across all rounds with phantom funding'),
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    clr_prediction_curve = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ), blank=True, default=list, help_text=_('5 point curve to predict CLR donations.'))
    # TODO: REMOVE
    backup_clr_prediction_curve = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ), blank=True, default=list, help_text=_('backup 5 point curve to predict CLR donations - used to store a secondary backup of the clr prediction curve, in the case a new identity mechanism is used'))
    activeSubscriptions = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    hidden = models.BooleanField(default=False, help_text=_('Hide the grant from the /grants page?'), db_index=True)
    weighted_shuffle = models.PositiveIntegerField(blank=True, null=True)
    contribution_count = models.PositiveIntegerField(blank=True, default=0)
    contributor_count = models.PositiveIntegerField(blank=True, default=0)
    # TODO-GRANTS: remove
    positive_round_contributor_count = models.PositiveIntegerField(blank=True, default=0)
    # TODO-GRANTS: remove
    negative_round_contributor_count = models.PositiveIntegerField(blank=True, default=0)

    defer_clr_to = models.ForeignKey(
        'grants.Grant',
        related_name='defered_clr_from',
        on_delete=models.CASCADE,
        help_text=_('The Grant that this grant defers it CLR contributions to (if any).'),
        null=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    last_clr_calc_date = models.DateTimeField(
        help_text=_('The last clr calculation date'),
        null=True,
        blank=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    next_clr_calc_date = models.DateTimeField(
        help_text=_('The last clr calculation date'),
        null=True,
        blank=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    last_update = models.DateTimeField(
        help_text=_('The last grant admin update date'),
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(GrantCategory, blank=True)
    twitter_handle_1 = models.CharField(default='', max_length=255, help_text=_('Grants twitter handle'), blank=True)
    twitter_handle_2 = models.CharField(default='', max_length=255, help_text=_('Grants twitter handle'), blank=True)
    twitter_handle_1_follower_count = models.PositiveIntegerField(blank=True, default=0)
    twitter_handle_2_follower_count = models.PositiveIntegerField(blank=True, default=0)
    sybil_score = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The Grants Sybil Score'),
    )

    funding_info = models.CharField(default='', blank=True, null=True, max_length=255, help_text=_('Is this grant VC funded?'))

    weighted_risk_score = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The Grants Weighted Risk Score'),
    )

    in_active_clrs = models.ManyToManyField(
        GrantCLR,
        help_text="Active Grants CLR Round"
    )
    is_clr_active = models.BooleanField(default=False, help_text=_('CLR Round active or not? (auto computed)'))
    clr_round_num = models.CharField(default='', max_length=255, help_text=_('the CLR round number thats active'), blank=True)

    twitter_verified = models.BooleanField(default=False, help_text='The owner grant has verified the twitter account')
    twitter_verified_by = models.ForeignKey('dashboard.Profile', null=True, blank=True, on_delete=models.SET_NULL, help_text='Team member who verified this grant')
    twitter_verified_at = models.DateTimeField(blank=True, null=True, help_text='At what time and date what verified this grant')

    # Grant Query Set used as manager.
    objects = GrantQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, active: {self.active}, title: {self.title}, type: {self.grant_type}"

    def calc_clr_round(self):
        clr_round = None

        # create_grant_active_clr_mapping
        clr_rounds = GrantCLR.objects.filter(is_active=True)
        for this_clr_round in clr_rounds:
            if self in this_clr_round.grants:
                self.in_active_clrs.add(this_clr_round)
            else:
                self.in_active_clrs.remove(this_clr_round)

        # create_grant_clr_cache
        if self.in_active_clrs.count() > 0 and self.is_clr_eligible:
            clr_round = self.in_active_clrs.first()

        if clr_round:
            self.is_clr_active = True
            self.clr_round_num = clr_round.round_num
        else:
            self.is_clr_active = False
            self.clr_round_num = ''

    @property
    def tenants(self):
        """returns list of chains the grant can recieve contributions in"""
        tenants = []
        # TODO: rename to eth_payout_address
        if self.admin_address and self.admin_address != '0x0':
            tenants.append('ETH')
        if self.zcash_payout_address and self.zcash_payout_address != '0x0':
            tenants.append('ZCASH')

        return tenants


    def updateActiveSubscriptions(self):
        """updates the active subscriptions list"""
        handles = []
        for handle in Subscription.objects.filter(grant=self, active=True, is_postive_vote=True).distinct('contributor_profile').values_list('contributor_profile__handle', flat=True):
            handles.append(handle)
        self.activeSubscriptions = handles

    @property
    def safe_next_clr_calc_date(self):
        if self.next_clr_calc_date and self.next_clr_calc_date < timezone.now():
            return timezone.now() + timezone.timedelta(minutes=5)
        return self.next_clr_calc_date

    @property
    def recurring_funding_supported(self):
        return self.contract_version < 2

    @property
    def related_grants(self):
        pkg = self.metadata.get('related', [])
        pks = [ele[0] for ele in pkg]
        rg = Grant.objects.filter(pk__in=pks)
        return_me = []
        for ele in pkg:
            grant = rg.get(pk=ele[0])
            return_me.append([grant, ele[1]])
        return return_me


    @property
    def configured_to_receieve_funding(self):
        if self.contract_version == 2:
            return True
        return self.contract_address != '0x0'

    @property
    def clr_match_estimate_this_round(self):
        try:
            return self.clr_prediction_curve[0][1]
        except:
            return 0

    @property
    def contributions(self):
        pks = []
        for subscription in self.subscriptions.all():
            pks += list(subscription.subscription_contribution.values_list('pk', flat=True))
        return Contribution.objects.filter(pk__in=pks)


    @property
    def negative_voting_enabled(self):
        return False

    def is_on_team(self, profile):
        if profile.pk == self.admin_profile.pk:
            return True
        if profile.grant_teams.filter(pk=self.pk).exists():
            return True
        return False

    @property
    def org_name(self):
        from git.utils import org_name
        try:
            return org_name(self.reference_url)
        except Exception:
            return None

    @property
    def get_contribution_count(self):
        num = 0
        for sub in self.subscriptions.filter(is_postive_vote=True):
            for contrib in sub.subscription_contribution.filter(success=True):
                num += 1
        for pf in self.phantom_funding.all():
            num+=1
        return num

    @property
    def contributors(self):
        return_me = []
        for sub in self.subscriptions.filter(is_postive_vote=True):
            for contrib in sub.subscription_contribution.filter(success=True):
                return_me.append(contrib.subscription.contributor_profile)
        for pf in self.phantom_funding.all():
            return_me.append(pf.profile)
        return return_me

    def get_contributor_count(self, since=None, is_postive_vote=True):
        if not since:
            since = timezone.datetime(1990, 1, 1)
        contributors = []
        for sub in self.subscriptions.filter(is_postive_vote=is_postive_vote):
            for contrib in sub.subscription_contribution.filter(success=True, created_on__gt=since):
                contributors.append(contrib.subscription.contributor_profile.handle)
        if is_postive_vote:
            for pf in self.phantom_funding.filter(created_on__gt=since).all():
                contributors.append(pf.profile.handle)
        return len(set(contributors))


    @property
    def org_profile(self):
        from dashboard.models import Profile
        profiles = Profile.objects.filter(handle=self.org_name.lower())
        if profiles.count():
            return profiles.first()
        return None

    @property
    def history_by_month(self):
        import math
        # gets the history of contributions to this grant month over month so they can be shown o grant details
        # returns [["", "Subscription Billing",  "New Subscriptions", "One-Time Contributions", "CLR Matching Funds"], ["December 2017", 5534, 2011, 0, 0], ["January 2018", 10396, 0 , 0, 0 ], ... for each monnth in which this grant has contribution history];
        CLR_PAYOUT_HANDLES = ['vs77bb', 'gitcoinbot', 'notscottmoore', 'owocki']
        month_to_contribution_numbers = {}
        subs = self.subscriptions.all().prefetch_related('subscription_contribution')
        for sub in subs:
            contribs = [sc for sc in sub.subscription_contribution.all() if sc.success]
            for contrib in contribs:
                #add all contributions
                year = contrib.created_on.strftime("%Y")
                quarter = math.ceil(int(contrib.created_on.strftime("%m"))/3.)
                key = f"{year}/Q{quarter}"
                subkey = 'One-Time'
                if contrib.subscription.contributor_profile.handle in CLR_PAYOUT_HANDLES:
                    subkey = 'CLR'
                if key not in month_to_contribution_numbers.keys():
                    month_to_contribution_numbers[key] = {"One-Time": 0, "Recurring-Recurring": 0, "New-Recurring": 0, 'CLR': 0}
                if contrib.subscription.amount_per_period_usdt:
                    month_to_contribution_numbers[key][subkey] += float(contrib.subscription.amount_per_period_usdt)

        # sort and return
        return_me = [["", "Contributions", "CLR Matching Funds"]]
        for key, val in (sorted(month_to_contribution_numbers.items(), key=lambda kv:(kv[0]))):
            return_me.append([key, val['One-Time'], val['CLR']])
        return return_me

    @property
    def history_by_month_max(self):
        max_amount = 0
        for ele in self.history_by_month:
            if type(ele[1]) is float:
                max_amount = max(max_amount, ele[1]+ele[2])
        return max_amount

    def get_amount_received_with_phantom_funds(self):
        return float(self.amount_received) + float(sum([ele.value for ele in self.phantom_funding.all()]))

    @property
    def abi(self):
        """Return grants abi."""
        if self.contract_version == 0:
            from grants.abi import abi_v0
            return abi_v0
        elif self.contract_version == 1:
            from grants.abi import abi_v1
            return abi_v1

    @property
    def url(self):
        """Return grants url."""
        from django.urls import reverse
        slug = self.slug if self.slug else "-"
        return reverse('grants:details', kwargs={'grant_id': self.pk, 'grant_slug': slug})

    def get_absolute_url(self):
        return self.url

    @property
    def contract(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        web3 = get_web3(self.network)
        grant_contract = web3.eth.contract(Web3.toChecksumAddress(self.contract_address), abi=self.abi)
        return grant_contract

    def cart_payload(self, build_absolute_uri):
        return {
            'grant_id': str(self.id),
            'grant_slug': self.slug,
            'grant_url': self.url,
            'grant_title': self.title,
            'grant_contract_version': self.contract_version,
            'grant_contract_address': self.contract_address,
            'grant_token_symbol': self.token_symbol,
            'grant_admin_address': self.admin_address,
            'grant_token_address': self.token_address,
            'grant_logo': self.logo.url if self.logo and self.logo.url else build_absolute_uri(static(f'v2/images/grants/logos/{self.id % 3}.png')),
            'grant_clr_prediction_curve': self.clr_prediction_curve,
            'grant_image_css': self.image_css,
            'is_clr_eligible': self.is_clr_eligible,
            'tenants': self.tenants,
            'zcash_payout_address': self.zcash_payout_address,
        }

    def repr(self, user, build_absolute_uri):
        return {
                'id': self.id,
                'logo_url': self.logo.url if self.logo and self.logo.url else build_absolute_uri(static(f'v2/images/grants/logos/{self.id % 3}.png')),
                'details_url': reverse('grants:details', args=(self.id, self.slug)),
                'title': self.title,
                'description': self.description,
                'last_update': self.last_update,
                'last_update_natural': naturaltime(self.last_update),
                'sybil_score': self.sybil_score,
                'weighted_risk_score': self.weighted_risk_score,
                'is_clr_active': self.is_clr_active,
                'clr_round_num': self.clr_round_num,
                'admin_profile': {
                    'url': self.admin_profile.url,
                    'handle': self.admin_profile.handle,
                    'avatar_url': self.admin_profile.avatar_url
                },
                'favorite': self.favorite(user) if user.is_authenticated else False,
                'is_on_team': is_grant_team_member(self, user.profile) if user.is_authenticated else False,
                'clr_prediction_curve': self.clr_prediction_curve,
                'last_clr_calc_date':  naturaltime(self.last_clr_calc_date) if self.last_clr_calc_date else None,
                'safe_next_clr_calc_date': naturaltime(self.safe_next_clr_calc_date) if self.safe_next_clr_calc_date else None,
                'amount_received_in_round': self.amount_received_in_round,
                'positive_round_contributor_count': self.positive_round_contributor_count,
                'monthly_amount_subscribed': self.monthly_amount_subscribed,
                'is_clr_eligible': self.is_clr_eligible,
                'slug': self.slug,
                'url': self.url,
                'contract_version': self.contract_version,
                'contract_address': self.contract_address,
                'token_symbol': self.token_symbol,
                'admin_address': self.admin_address,
                'zcash_payout_address': self.zcash_payout_address,
                'token_address': self.token_address,
                'image_css': self.image_css,
                'verified': self.twitter_verified,
                'tenants': self.tenants,
            }

    def favorite(self, user):
        return Favorite.objects.filter(user=user, grant=self).exists()

    def save(self, update=True, *args, **kwargs):
        """Override the Grant save to optionally handle modified_on logic."""
        if self.modified_on < (timezone.now() - timezone.timedelta(minutes=15)):
            from grants.tasks import update_grant_metadata
            update_grant_metadata.delay(self.pk)

        from economy.models import get_time
        if update:
            self.modified_on = get_time()

        return super(Grant, self).save(*args, **kwargs)


class SubscriptionQuerySet(models.QuerySet):
    """Define the Subscription default queryset and manager."""

    pass


class Subscription(SuperModel):
    """Define the structure of a subscription agreement."""

    TENANT = [
        ('ETH', 'ETH'),
        ('ZCASH', 'ZCASH')
    ]

    active = models.BooleanField(default=True, db_index=True, help_text=_('Whether or not the Subscription is active.'))
    error = models.BooleanField(default=False, help_text=_('Whether or not the Subscription is erroring out.'))
    subminer_comments = models.TextField(default='', blank=True, help_text=_('Comments left by the subminer.'))
    comments = models.TextField(default='', blank=True, help_text=_('Comments left by subscriber.'))

    split_tx_id = models.CharField(
        default='',
        max_length=255,
        help_text=_('The tx id of the split transfer'),
        blank=True,
    )
    is_postive_vote = models.BooleanField(default=True, db_index=True, help_text=_('Whether this is positive or negative vote'))
    split_tx_confirmed = models.BooleanField(default=False, help_text=_('Whether or not the split tx succeeded.'))

    subscription_hash = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s Subscription hash.'),
        blank=True,
    )
    contributor_signature = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s signature.'),
        blank=True,
        )
    contributor_address = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s wallet address of the Subscription.'),
    )
    amount_per_period = models.DecimalField(
        default=1,
        decimal_places=18,
        max_digits=64,
        help_text=_('The promised contribution amount per period.'),
    )
    real_period_seconds = models.DecimalField(
        default=2592000,
        decimal_places=0,
        max_digits=50,
        help_text=_('The real payout frequency of the Subscription in seconds.'),
    )
    # TODO: REMOVE
    frequency_unit = models.CharField(
        max_length=255,
        default='',
        help_text=_('The text version of frequency units e.g. days, months'),
    )
    # TODO: REMOVE
    frequency = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=50,
        help_text=_('The real payout frequency of the Subscription in seconds.'),
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Subscription.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token symbol to be used with the Subscription.'),
    )
    gas_price = models.DecimalField(
        default=1,
        decimal_places=18,
        max_digits=50,
        help_text=_('The required gas price for the Subscription.'),
    )
    # TODO: REMOVE
    new_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    # TODO: REMOVE
    end_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    # TODO: REMOVE
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for cancelSubscription.'),
    )
    # TODO: REMOVE
    num_tx_approved = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The number of transactions approved for the Subscription.'),
    )
    # TODO: REMOVE
    num_tx_processed = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The number of transactoins processed by the subminer for the Subscription.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Subscription resides.'),
    )
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='subscriptions',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Grant.'),
    )
    contributor_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_contributor',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The Subscription contributor\'s Profile.'),
    )
    # TODO: REMOVE
    last_contribution_date = models.DateTimeField(
        help_text=_('The last contribution date'),
        default=timezone.datetime(1990, 1, 1),
    )
    # TODO: REMOVE
    next_contribution_date = models.DateTimeField(
        help_text=_('The next contribution date'),
        default=timezone.datetime(1990, 1, 1),
    )
    amount_per_period_usdt = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        help_text=_('The amount per contribution period in USDT'),
    )
    tenant = models.CharField(max_length=10, null=True, blank=True, default="ETH", choices=TENANT, help_text="specific tenant in which contribution is made")

    @property
    def negative(self):
        return self.is_postive_vote == False

    @property
    def status(self):
        """Return grants status, current or past due."""
        if self.next_contribution_date < timezone.now():
            return "PAST DUE"
        return "CURRENT"

    @property
    def amount_per_period_minus_gas_price(self):
        amount = float(self.amount_per_period) - float(self.amount_per_period_to_gitcoin)
        return amount

    @property
    def amount_per_period_to_gitcoin(self):
        from dashboard.tokens import addr_to_token
        token = addr_to_token(self.token_address, self.network)

        # gas prices no longer take this amount times 10**18 decimals
        import pytz
        if self.created_on > timezone.datetime(2020, 6, 16, 15, 0).replace(tzinfo=pytz.utc):
            return self.gas_price

        try:
            decimals = token.get('decimals', 0)
            return (float(self.gas_price) / 10 ** decimals)
        except:
            return 0


    def __str__(self):
        """Return the string representation of a Subscription."""
        from django.contrib.humanize.templatetags.humanize import naturaltime

        return f"id: {self.pk}; {round(self.amount_per_period,1)} {self.token_symbol} (${round(self.amount_per_period_usdt)}) {int(self.num_tx_approved)} times, created {naturaltime(self.created_on)} by {self.contributor_profile}"

    def get_nonce(self, address):
        return self.grant.contract.functions.extraNonce(address).call() + 1

    def get_debug_info(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        from dashboard.abi import erc20_abi
        from dashboard.tokens import addr_to_token
        try:
            web3 = get_web3(self.network)
            if not self.token_address:
                return "This subscription has no token_address"
            token_contract = web3.eth.contract(Web3.toChecksumAddress(self.token_address), abi=erc20_abi)
            balance = token_contract.functions.balanceOf(Web3.toChecksumAddress(self.contributor_address)).call()
            allowance = token_contract.functions.allowance(Web3.toChecksumAddress(self.contributor_address), Web3.toChecksumAddress(self.grant.contract_address)).call()
            gasPrice = self.gas_price
            is_active = self.get_is_active_from_web3()
            token = addr_to_token(self.token_address, self.network)
            next_valid_timestamp = self.get_next_valid_timestamp()
            decimals = token.get('decimals', 0)
            balance = balance / 10 ** decimals
            allowance = allowance / 10 ** decimals
            error_reason = "unknown"
            if not is_active:
                error_reason = 'not_active'
            if timezone.now().timestamp() < next_valid_timestamp:
                error_reason = 'before_next_valid_timestamp'
            if (float(balance) + float(gasPrice)) < float(self.amount_per_period):
                error_reason = "insufficient_balance"
            if allowance < self.amount_per_period:
                error_reason = "insufficient_allowance"

            debug_info = f"""
error_reason: {error_reason}
==============================
is_active: {is_active}
decimals: {decimals}
balance: {balance}
allowance: {allowance}
amount_per_period: {self.amount_per_period}
next_valid_timestamp: {next_valid_timestamp}
"""
        except Exception as e:
            return str(e)
        return debug_info

    def get_next_valid_timestamp(self):
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.nextValidTimestamp(_hash).call()

    def get_is_ready_to_be_processed_from_db(self):
        """Return true if subscription is ready to be processed according to the DB."""
        if not self.subscription_contribution.exists():
            return True
        return self.next_contribution_date < timezone.now() and self.num_tx_processed < self.num_tx_approved

    def get_are_we_past_next_valid_timestamp(self):
        return timezone.now().timestamp() > self.get_next_valid_timestamp()

    def get_is_subscription_ready_from_web3(self):
        """Return true if subscription is ready to be processed according to web3."""
        args = self.get_subscription_hash_arguments()
        return self.grant.contract.functions.isSubscriptionReady(
            args['from'],
            args['to'],
            args['tokenAddress'],
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            args['signature'],
        ).call()

    def get_check_success_web3(self):
        """Check the return value of the previous function. Returns true if the previous function."""
        return self.grant.contract.functions.checkSuccess().call()

    def _do_helper_via_web3(self, fn, minutes_to_confirm_within=1):
        """Call the specified function fn"""
        from dashboard.utils import get_web3
        args = self.get_subscription_hash_arguments()
        tx = fn(
            args['from'],
            args['to'],
            args['tokenAddress'],
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            args['signature'],
        ).buildTransaction(
            self.helper_tx_dict(minutes_to_confirm_within)
        )
        web3 = get_web3(self.grant.network)
        signed_txn = web3.eth.account.signTransaction(tx, private_key=settings.GRANTS_PRIVATE_KEY)
        return web3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def do_cancel_subscription_via_web3(self, minutes_to_confirm_within=1):
        """.Cancels the subscripion on the blockchain"""
        return self._do_helper_via_web3(
            self.grant.contract.functions.cancelSubscription,
            minutes_to_confirm_within=minutes_to_confirm_within
        )

    def do_execute_subscription_via_web3(self, minutes_to_confirm_within=1):
        """.Executes the subscription on the blockchain"""
        return self._do_helper_via_web3(
            self.grant.contract.functions.executeSubscription,
            minutes_to_confirm_within=minutes_to_confirm_within
        )

    def helper_tx_dict(self, minutes_to_confirm_within=1):
        """returns a dict like this: {'to': '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'from': web3.eth.coinbase, 'value': 12345}"""
        from dashboard.utils import get_nonce
        return {
            'from': settings.GRANTS_OWNER_ACCOUNT,
            'nonce': get_nonce(self.grant.network, settings.GRANTS_OWNER_ACCOUNT, True),
            'value': 0,
            'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(minutes_to_confirm_within) * 10**9),
            'gas': 204066,
        }

    def get_is_active_from_web3(self):
        """Return true if subscription is active according to web3."""
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.isSubscriptionActive(_hash, 10).call()

    def get_subscription_signer_from_web3(self):
        """Return subscription signer."""
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.getSubscriptionSigner(_hash, self.contributor_signature).call()

    def get_subscription_hash_arguments(self):
        """Get the grant subscription hash from web3.

        Attributes:
            from (str): Subscription.contributor_address
            to (str): Grant.admin_address
            tokenAddress (str): Subscription.token_address
            tokenAmount (float): Subscription.amount_per_period
            periodSeconds (int): real_period_seconds in the Subscription model
            gasPrice (float): Subscription.gas_price
            nonce (int): The nonce is stored in the Contribution model. its created / managed by sync_geth
            signature (str): Subscription.contributor_signature

        Returns:
            str: The Subscription hash.

        """
        from dashboard.tokens import addr_to_token

        subs = self
        grant = subs.grant

        _from = subs.contributor_address
        to = grant.admin_address
        if grant.token_address != '0x0000000000000000000000000000000000000000':
            tokenAddress = grant.token_address
        else:
            tokenAddress = subs.token_address

        tokenAmount = subs.amount_per_period
        periodSeconds = subs.real_period_seconds
        gasPrice = subs.gas_price
        nonce = subs.get_nonce(_from)
        signature = subs.contributor_signature

        # TODO - figure out the number of decimals
        token = addr_to_token(tokenAddress, subs.grant.network)
        decimals = token.get('decimals', 0)

        return {
            'from': Web3.toChecksumAddress(_from),
            'to': Web3.toChecksumAddress(to),
            'tokenAddress': Web3.toChecksumAddress(tokenAddress),
            'tokenAmount': int(tokenAmount * 10**decimals),
            'periodSeconds': int(periodSeconds),
            'gasPrice': int(gasPrice),
            'nonce': int(nonce),
            'signature': signature,
        }

    def get_hash_from_web3(self):
        """Returns the grants subscription hash (has to get it from web3)."""
        args = self.get_subscription_hash_arguments()
        return self.grant.contract.functions.getSubscriptionHash(
            Web3.toChecksumAddress(args['from']),
            Web3.toChecksumAddress(args['to']),
            Web3.toChecksumAddress(args['tokenAddress']),
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            ).call()

    def get_converted_amount(self, ignore_gitcoin_fee=False, only_gitcoin_fee=False):
        if ignore_gitcoin_fee:
            amount = self.amount_per_period
        elif only_gitcoin_fee:
            amount = self.amount_per_period_to_gitcoin
        else:
            amount = self.amount_per_period_minus_gas_price

        try:
            if self.token_symbol == "ETH" or self.token_symbol == "WETH":
                return Decimal(float(amount) * float(eth_usd_conv_rate()))
            else:
                value_token_to_eth = Decimal(convert_amount(
                    amount,
                    self.token_symbol,
                    "ETH")
                )

            value_eth_to_usdt = Decimal(eth_usd_conv_rate())
            value_usdt = value_token_to_eth * value_eth_to_usdt
            return value_usdt

        except ConversionRateNotFoundError as e:
            try:
                return Decimal(convert_amount(
                    amount,
                    self.token_symbol,
                    "USDT"))
            except ConversionRateNotFoundError as no_conversion_e:
                logger.info(no_conversion_e)
                return None

    def get_converted_monthly_amount(self, ignore_gitcoin_fee=False):
        converted_amount = self.get_converted_amount(ignore_gitcoin_fee=ignore_gitcoin_fee) or 0

        total_sub_seconds = Decimal(self.real_period_seconds) * Decimal(self.num_tx_approved)

        if total_sub_seconds < 2592000:
            result = Decimal(converted_amount * Decimal(self.num_tx_approved))
        elif total_sub_seconds >= 2592000:
            result = Decimal(converted_amount * (Decimal(2592000) / Decimal(self.real_period_seconds)))

        return result

    def save_split_tx_to_contribution(self):
        sc = self.subscription_contribution.first()
        sc.split_tx_id = self.split_tx_id
        sc.split_tx_confirmed = self.split_tx_confirmed
        sc.save()

    def successful_contribution(self, tx_id):
        """Create a contribution object."""
        self.last_contribution_date = timezone.now()
        self.next_contribution_date = timezone.now() + timedelta(0, int(self.real_period_seconds))
        self.num_tx_processed += 1
        contribution_kwargs = {
            'tx_id': tx_id,
            'subscription': self,
            'split_tx_id': self.split_tx_id,
            'split_tx_confirmed': self.split_tx_confirmed
        }
        contribution = Contribution.objects.create(**contribution_kwargs)
        grant = self.grant

        value_usdt = self.get_converted_amount(False)
        if value_usdt:
            self.amount_per_period_usdt = value_usdt
            grant.amount_received += Decimal(value_usdt)

        if self.num_tx_processed == self.num_tx_approved and value_usdt:
            grant.monthly_amount_subscribed -= self.get_converted_monthly_amount()
            self.active = False

        self.save()
        grant.updateActiveSubscriptions()
        grant.save()

        if grant.pk == 86:
            # KO 9/28/2020 - per community feedback, contributions that are auto-matched should not count towards
            # CLR matching, as it gives gitcoin an unfair advantage
            is_automatic = bool(contribution.subscription.amount_per_period == contribution.subscription.gas_price)
            from dashboard.models import Profile
            contribution.profile_for_clr = Profile.objects.get(handle='gitcoinbot')
            contribution.match = False
            contribution.save()

        return contribution


    def create_contribution(self, tx_id, is_successful_contribution=True):
        from marketing.mails import successful_contribution
        from grants.tasks import update_grant_metadata

        now = timezone.now()
        self.last_contribution_date = now
        self.next_contribution_date = now

        self.num_tx_processed += 1

        contribution = Contribution()

        contribution.success = False
        contribution.tx_cleared = False
        contribution.subscription = self
        contribution.split_tx_id = self.split_tx_id
        contribution.split_tx_confirmed = self.split_tx_confirmed

        if tx_id:
            contribution.tx_id = tx_id

        contribution.save()
        grant = self.grant

        value_usdt = self.get_converted_amount(False)
        if value_usdt:
            self.amount_per_period_usdt = value_usdt
            grant.amount_received += Decimal(value_usdt)

        if self.num_tx_processed == self.num_tx_approved and value_usdt:
            grant.monthly_amount_subscribed -= self.get_converted_monthly_amount()
            self.active = False

        self.save()
        grant.updateActiveSubscriptions()
        grant.save()
        if is_successful_contribution:
            successful_contribution(self.grant, self, contribution)

        update_grant_metadata.delay(self.pk)
        return contribution



class DonationQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass



class Flag(SuperModel):

    grant = models.ForeignKey(
        'grants.Grant',
        related_name='flags',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grantflags',
        on_delete=models.SET_NULL,
        help_text=_("The flagger's profile."),
        null=True,
    )
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    processed = models.BooleanField(default=False, help_text=_('Was it processed?'))
    comments_admin = models.TextField(default='', blank=True, help_text=_('The comments of an admin.'))
    tweet = models.URLField(blank=True, help_text=_('The associated reference URL of the Grant.'))

    def post_flag(self):
        from dashboard.models import Activity, Profile
        from townsquare.models import Comment
        profile = Profile.objects.filter(handle='gitcoinbot').first()
        activity = Activity.objects.create(profile=profile, activity_type='flagged_grant', grant=self.grant)
        comment = Comment.objects.create(
            profile=profile,
            activity=activity,
            comment=f"Comment from anonymous user: {self.comments}")



    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, processed: {self.processed}, comments: {self.comments} "


class Donation(SuperModel):
    """Define the structure of an optional donation. These donations are
       additional funds sent to Gitcoin as part of contributing or subscribing
       to a grant."""

    from_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The sender's address."),
    )
    to_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The destination address."),
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The donator's profile."),
        null=True,
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Grant.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='',
        help_text=_("The donation token's symbol."),
    )
    token_amount = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        help_text=_('The donation amount in tokens.'),
    )
    token_amount_usdt = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The donation amount converted to USDT/DAI at the moment of donation.'),
    )
    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Subscription resides.'),
    )
    donation_percentage = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=5,
        help_text=_('The additional percentage selected when the donation is made'),
    )
    subscription = models.ForeignKey(
        'grants.subscription',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The recurring subscription that this donation originated from."),
        null=True,
    )
    contribution = models.ForeignKey(
        'grants.contribution',
        related_name='donation',
        on_delete=models.SET_NULL,
        help_text=_("The contribution that this donation was a part of."),
        null=True,
    )


    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return f"id: {self.pk}; from:{profile.handle}; {tx_id} => ${token_amount_usdt}; {naturaltime(self.created_on)}"


class ContributionQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    CHECKOUT_TYPES = [
        ('eth_std', 'eth_std'),
        ('eth_zksync_deposit', 'eth_zksync_deposit'),
        ('eth_zksync_batch_deposit', 'eth_zksync_batch_deposit'),
        ('eth_zksync_pure', 'eth_zksync_pure'),
        ('zcash_std', 'zcash_std')
    ]

    success = models.BooleanField(default=True, help_text=_('Whether or not success.'))
    tx_cleared = models.BooleanField(default=False, help_text=_('Whether or not tx cleared.'))
    tx_override = models.BooleanField(default=False, help_text=_('Whether or not the tx success and tx_cleared have been manually overridden. If this setting is True, update_tx_status will not change this object.'))

    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
        blank=True,
    )
    split_tx_id = models.CharField(
        default='',
        max_length=255,
        help_text=_('The tx id of the split transfer'),
        blank=True,
    )
    split_tx_confirmed = models.BooleanField(default=False, help_text=_('Whether or not the split tx succeeded.'))
    subscription = models.ForeignKey(
        'grants.Subscription',
        related_name='subscription_contribution',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Subscription.'),
    )
    normalized_data = JSONField(
        default=dict,
        blank=True,
        help_text=_('the normalized grant data; for easy consumption on read'),
    )
    match = models.BooleanField(default=True, help_text=_('Whether or not this contribution should be matched.'))


    originated_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The origination address of the funds used in this txn'),
    )
    validator_passed = models.BooleanField(default=False, help_text=_('Whether or not the backend validator passed.'))
    validator_comment = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The why or why not validator passed'),
    )

    profile_for_clr = models.ForeignKey(
        'dashboard.Profile',
        related_name='clr_pledges',
        on_delete=models.CASCADE,
        help_text=_('The profile to attribute this contribution to..'),
        null=True,
        blank=True,
    )
    checkout_type = models.CharField(
        max_length=30,
        null=True,
        help_text=_('The checkout method used while making the contribution'),
        blank=True,
        choices=CHECKOUT_TYPES
    )
    anonymous = models.BooleanField(default=False, help_text=_('Whether users can view the profile for this project or not'))

    def get_absolute_url(self):
        return self.subscription.grant.url + '?tab=transactions'

    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        txid_shortened = self.tx_id[0:10] + "..."
        return f"${round(self.subscription.amount_per_period_usdt)}, txids: {self.tx_id}, {self.split_tx_id}, id: {self.pk}, Success:{self.success}, tx_cleared:{self.tx_cleared} - created {naturaltime(self.created_on)} "

    @property
    def is_first_in_sequence(self):
        """returns true only IFF a contribution is the first in a sequence of subscriptions."""
        other_contributions_after_this_one = Contribution.objects.filter(subscription=self.subscription, created_on__lt=self.created_on)
        return not other_contributions_after_this_one.exists()

    def identity_identifier(self, mechanism):
        """Returns the anti sybil identity identiifer for this grant, according to mechanism."""
        if mechanism == 'originated_address':
            return self.originated_address
        else:
            return self.subscription.contributor_profile.id

    def update_tx_status(self):
        """Updates tx status."""
        try:
            from economy.tx import grants_transaction_validator_v2
            from dashboard.utils import get_tx_status
            from economy.tx import getReplacedTX
            if self.tx_override:
                return

            # handle replace of tx_id
            if self.tx_id:
                tx_status, _ = get_tx_status(self.tx_id, self.subscription.network, self.created_on)
                if tx_status in ['pending', 'dropped', 'unknown', '']:
                    new_tx = getReplacedTX(self.tx_id)
                    if new_tx:
                        self.tx_id = new_tx
                    else:
                        print('TODO: do stuff related to long running pending txns')
                    return

            # We use the transaction hashes of this object to help identify zkSync checkouts. This
            # works as follows:
            #
            #   self.split_tx_id holds one of:
            #     Case 1: The tx hash of an L1 transaction to the BulkCheckout contract for an
            #             ordinary checkout
            #     Case 2: The tx hash of an L1 transaction that deposits funds into zkSync. This
            #             occurs when a user did not have existing funds in zkSync
            #     Case 3: The address of the Gitcoin zkSync wallet that executed the donations. This
            #             occurs when a user already had funds in zkSync
            #
            # Case 1 has already been handled by everything above. For Case 2, we mark a
            # contribution as cleared once both of the below conditions are met:
            #   1. The L1 deposit transaction has been confirmed, and
            #   2. The L2 transfers have been completed
            #
            # For case 3, we mark a contribution as cleared once the L2 transfers are completed.

            # Prepare web3 provider
            network = self.subscription.network
            PROVIDER = "wss://" + network + ".infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
            w3 = Web3(Web3.WebsocketProvider(PROVIDER))

            # Get case number
            is_split_tx_id_address = len(self.split_tx_id) == 42 and self.split_tx_id[0:2] == '0x'
            if is_split_tx_id_address:
                case_number = 3

            else:
                # Figure out if we are in Case 1 or Case 2
                # handle replace of split_tx_id
                if not self.split_tx_id:
                    return

                split_tx_status, _ = get_tx_status(self.split_tx_id, self.subscription.network, self.created_on)
                if split_tx_status in ['pending', 'dropped', 'unknown', '']:
                    new_tx = getReplacedTX(self.split_tx_id)
                    if new_tx:
                        self.split_tx_id = new_tx
                    else:
                        print('TODO: do stuff related to long running pending txns')
                    return

                # Get recipient of L1 transfer
                receipt = w3.eth.getTransactionReceipt(self.split_tx_id)
                recipient_L1 = receipt.to.lower()

                # Determine if this is Case 1 (BulkCheckout) or Case 2 (deposit into zkSync)
                zksync_mainnet_addr = '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF'
                zksync_rinkeby_addr = '0x82F67958A5474e40E1485742d648C0b0686b6e5D'
                zksync_contract_addr = zksync_rinkeby_addr if network == 'rinkeby' else zksync_mainnet_addr
                batch_zksync_deposit_contract_addr = '0x9D37F793E5eD4EbD66d62D505684CD9f756504F6'.lower()
                zkSync_recipients = [zksync_contract_addr.lower(), batch_zksync_deposit_contract_addr.lower()]
                case_number = 2 if recipient_L1 in zkSync_recipients else 1

            # If case 1, proceed as normal
            if case_number == 1:
                # actually validate token transfers
                try:
                    response = grants_transaction_validator_v2(self, w3)
                    if len(response['originator']):
                        self.originated_address = response['originator'][0]
                    self.validator_passed = response['validation']['passed']
                    self.validator_comment = response['validation']['comment']
                    self.tx_cleared = response['tx_cleared']
                    self.split_tx_confirmed = response['split_tx_confirmed']
                    self.success = self.validator_passed
                except Exception as e:
                    if 'Expecting value' in str(e):
                        self.validator_passed = True
                        self.validator_comment = 'temporary stopgap success, alethio API failed/re-running'
                        self.tx_cleared = True
                        self.split_tx_confirmed = True
                        self.success = self.validator_passed
                    else:
                        raise e


            elif case_number == 2:
                self.validator_comment = 'zkSync with L1 deposit'
                self.originated_address = self.subscription.contributor_address

                # Make sure L1 tx succeeded
                if receipt.status == 0:
                    print('okkkk')
                    self.tx_cleared = True
                    self.success = False
                    self.validator_passed = True
                    self.split_tx_confirmed = True
                    self.validator_comment = f"{self.validator_comment}. L1 transaction failed (receipt.status == 0)"
                    print("TODO: do stuff related to failed contribs, like emails (failed tx)")
                    return

                # If Case 2, we get the address of the gitcoin zkSync account from events
                zksync_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockVerification","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"totalBlocksVerified","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"totalBlocksCommitted","type":"uint32"}],"name":"BlocksRevert","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"DepositCommit","type":"event"},{"anonymous":false,"inputs":[],"name":"ExodusMode","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint32","name":"nonce","type":"uint32"},{"indexed":false,"internalType":"bytes","name":"fact","type":"bytes"}],"name":"FactAuth","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"FullExitCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint64","name":"serialId","type":"uint64"},{"indexed":false,"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"indexed":false,"internalType":"bytes","name":"pubData","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"name":"NewPriorityRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":true,"internalType":"address","name":"owner","type":"address"}],"name":"OnchainDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"OnchainWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsAdd","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsComplete","type":"event"},{"constant":true,"inputs":[],"name":"EMPTY_STRING_KECCAK","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"authFacts","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes22","name":"","type":"bytes22"}],"name":"balancesToWithdraw","outputs":[{"internalType":"uint128","name":"balanceToWithdraw","type":"uint128"},{"internalType":"uint8","name":"gasReserveValue","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"blocks","outputs":[{"internalType":"uint32","name":"committedAtBlock","type":"uint32"},{"internalType":"uint64","name":"priorityOperations","type":"uint64"},{"internalType":"uint32","name":"chunks","type":"uint32"},{"internalType":"bytes32","name":"withdrawalsDataHash","type":"bytes32"},{"internalType":"bytes32","name":"commitment","type":"bytes32"},{"internalType":"bytes32","name":"stateRoot","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint64","name":"_n","type":"uint64"}],"name":"cancelOutstandingDepositsForExodusMode","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint32","name":"_feeAccount","type":"uint32"},{"internalType":"bytes32[]","name":"_newBlockInfo","type":"bytes32[]"},{"internalType":"bytes","name":"_publicData","type":"bytes"},{"internalType":"bytes","name":"_ethWitness","type":"bytes"},{"internalType":"uint32[]","name":"_ethWitnessSizes","type":"uint32[]"}],"name":"commitBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_n","type":"uint32"}],"name":"completeWithdrawals","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint104","name":"_amount","type":"uint104"},{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositETH","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"uint16","name":"_tokenId","type":"uint16"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"}],"name":"exit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"},{"internalType":"uint16","name":"","type":"uint16"}],"name":"exited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"exodusMode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPendingWithdrawalIndex","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPriorityRequestId","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"address","name":"_token","type":"address"}],"name":"fullExit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"uint16","name":"_tokenId","type":"uint16"}],"name":"getBalanceToWithdraw","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"getNoticePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"initializationParameters","type":"bytes"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"isReadyForUpgrade","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"numberOfPendingWithdrawals","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"pendingWithdrawals","outputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint16","name":"tokenId","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"priorityRequests","outputs":[{"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"internalType":"bytes","name":"pubData","type":"bytes"},{"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_maxBlocksToRevert","type":"uint32"}],"name":"revertBlocks","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"_pubkey_hash","type":"bytes"},{"internalType":"uint32","name":"_nonce","type":"uint32"}],"name":"setAuthPubkeyHash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksCommitted","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksVerified","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalCommittedPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalOpenPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"triggerExodusIfNeeded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"upgradeParameters","type":"bytes"}],"name":"upgrade","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeCanceled","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeFinishes","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeNoticePeriodStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActivationTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"upgradePreparationStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"},{"internalType":"bytes","name":"_withdrawalsData","type":"bytes"}],"name":"verifyBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint128","name":"_maxAmount","type":"uint128"}],"name":"withdrawERC20Guarded","outputs":[{"internalType":"uint128","name":"withdrawnAmount","type":"uint128"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawETH","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
                zksync_contract = w3.eth.contract(address=zksync_contract_addr, abi=zksync_abi)
                parsed_logs = zksync_contract.events.OnchainDeposit().processReceipt(receipt)
                if len(parsed_logs) == 0:
                    self.tx_cleared = True
                    self.success = False
                    self.validator_passed = True
                    self.split_tx_confirmed = True
                    self.validator_comment = f"{self.validator_comment}. No event logs found"
                    print("TODO: do stuff related to failed contribs, like emails (no event logs found)")
                    return

                # Event logs found, continue
                gitcoin_zksync_addr = parsed_logs[0]['args']['owner']
                self.validator_passed = True
                self.split_tx_confirmed = True

            elif case_number == 3:
                # If Case 3, the split_tx_id field hold the address
                gitcoin_zksync_addr = self.split_tx_id
                self.originated_address = self.subscription.contributor_address
                self.validator_passed = True
                self.validator_comment = 'zkSync only'
                self.split_tx_confirmed = True

            # Validate zkSync transfers now
            if case_number == 2 or case_number == 3:
                # Now we look for successful L2 transfers from gitcoin_zksync_addr to the
                # grant's admin address with the expected token and transfer amount.

                # Get last 100 executed zkSync transfers for that address
                #   - TODO support users with more than 100 transfers (i.e. more than 100 grant
                #      donations). This can be done with the pagination from the zkSync API
                #   - TODO this fails if a user makes the exact same donation twice, as the second
                #     will already be marked as completed because of the first. For this failure
                #     mode to occur the (1) recipient, (2) token used, and (3) amount donated must
                #     all be indentical
                base_url = 'https://rinkeby-api.zksync.io/api/v0.1' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1'
                r = requests.get(f"{base_url}/account/{gitcoin_zksync_addr}/history/older_than")
                r.raise_for_status()
                transactions = r.json() # array of zkSync transactions

                # Define expected properties of the transfer
                expected_recipient = self.normalized_data['admin_address']
                expected_token = self.normalized_data['token_symbol']

                token = Token.objects.filter(network=network, symbol=expected_token, approved=True).first().to_dict
                decimals = token['decimals']
                expected_transfer_amount = Decimal(
                    self.subscription.amount_per_period_minus_gas_price * 10 ** decimals
                )
                transfer_tolerance = 0.05 # use a 5% tolerance
                expected_amount_min = expected_transfer_amount * (Decimal(1 - transfer_tolerance))
                expected_amount_max = expected_transfer_amount * (Decimal(1 + transfer_tolerance))

                # Look through zkSync transfers to find one with the expected amounts
                is_correct_recipient = False
                is_correct_token = False
                is_correct_amount = False

                number_of_transfers = 0
                number_of_deposits = 0

                for transaction in transactions:
                    if transaction['tx']['type'] == "Deposit":
                        number_of_deposits += 1
                        continue

                    if transaction['tx']['type'] != "Transfer":
                        continue

                    number_of_transfers += 1

                    is_correct_recipient = transaction['tx']['to'].lower() == expected_recipient.lower()
                    is_correct_token = transaction['tx']['token'] == expected_token

                    transfer_amount = Decimal(transaction['tx']['amount'])
                    is_correct_amount = transfer_amount > expected_amount_min and transfer_amount < expected_amount_max

                    if is_correct_recipient and is_correct_token and is_correct_amount:
                        self.tx_cleared = True
                        self.success = transaction['success']
                        self.validator_comment = f"{self.validator_comment}. Success"
                        break

                if not is_correct_recipient or not is_correct_token or not is_correct_amount:
                    # Transaction was not found, let's find out why
                    if len(transactions) == 0:
                        # No activity was found for user
                        self.validator_comment = f"{self.validator_comment}. User has not interacted with zkSync"
                    elif number_of_deposits > 0 and number_of_transfers == 0:
                        # User deposited funds, but did not send their donation transactions. This
                        # occurs if the user closes the page after sending their deposit transaction
                        # and before zkSync transfers are sent
                        self.validator_comment = f"{self.validator_comment}. Found deposit but no transfer. User likely closed page before transfers were sent and should revisit cart to complete checkout. User may not be aware so send them email reminders"

                    elif len(transactions) > 100:
                        # See the TODO above for more info -- the validator current is likely to
                        # miss some transfers if the user has over 100 transactions in zkSync
                        self.validator_comment = f"{self.validator_comment}. User has over 100 transactions on zkSync, so transaction may exist but not have been found. Update validator to use pagination on zkSync API to resolve this"

                    else:
                        # Could not find expected transfer, so try list specifics about why. We
                        # Ascannot find exactly what went wrong because: We cycle through a list of
                        # transactions. Some may have correct recipient and token but wrong amount.
                        # Others may have correct token and amount but wrong recipient. In such a
                        # case we cannot distinguish exactly what the cause was for not finding the
                        # desired transasction.
                        self.validator_comment = f"{self.validator_comment}. Transaction not found, unknown reason"

            if self.success:
                print("TODO: do stuff related to successful contribs, like emails")
            else:
                print("TODO: do stuff related to failed contribs, like emails")
        except Exception as e:
            self.validator_passed = False
            self.validator_comment = str(e)
            print(f"Exception: {self.validator_comment}")
            self.tx_cleared = False
            self.split_tx_confirmed = False
            self.success = False


@receiver(post_save, sender=Contribution, dispatch_uid="psave_contrib")
def psave_contrib(sender, instance, **kwargs):

    from django.contrib.contenttypes.models import ContentType
    from dashboard.models import Earning
    if instance.subscription and not instance.subscription.negative:
        try:
            Earning.objects.update_or_create(
                source_type=ContentType.objects.get(app_label='grants', model='contribution'),
                source_id=instance.pk,
                defaults={
                    "created_on":instance.created_on,
                    "from_profile":instance.subscription.contributor_profile,
                    "org_profile":instance.subscription.grant.org_profile,
                    "to_profile":instance.subscription.grant.admin_profile,
                    "value_usd":instance.subscription.get_converted_amount(False),
                    "url":instance.subscription.grant.url,
                    "network":instance.subscription.grant.network,
                    "txid":instance.subscription.split_tx_id,
                    "token_name":instance.subscription.token_symbol,
                    "token_value":instance.subscription.amount_per_period,
                }
            )
        except:
            pass

@receiver(pre_save, sender=Contribution, dispatch_uid="presave_contrib")
def presave_contrib(sender, instance, **kwargs):

    if not instance.profile_for_clr:
        if instance.subscription:
            instance.profile_for_clr = instance.subscription.contributor_profile

    ele = instance
    sub = ele.subscription
    grant = sub.grant
    instance.normalized_data = {
        'id': grant.id,
        'logo': grant.logo.url if grant.logo else None,
        'url': grant.url,
        'title': grant.title,
        'amount_per_period_minus_gas_price': float(instance.subscription.amount_per_period_minus_gas_price),
        'amount_per_period_to_gitcoin': float(instance.subscription.amount_per_period_to_gitcoin),
        'created_on': ele.created_on.strftime('%Y-%m-%d'),
        'frequency': int(sub.frequency),
        'frequency_unit': sub.frequency_unit,
        'num_tx_approved': int(sub.num_tx_approved),
        'token_symbol': sub.token_symbol,
        'amount_per_period_usdt': float(sub.amount_per_period_usdt),
        'amount_per_period': float(sub.amount_per_period),
        'admin_address': grant.admin_address,
        'tx_id': ele.tx_id,
    }


def next_month():
    """Get the next month time."""
    return localtime(timezone.now() + timedelta(days=30))


class CLRMatch(SuperModel):
    """Define the structure of a CLR Match amount."""

    round_number = models.PositiveIntegerField(blank=True, null=True)
    amount = models.FloatField()
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='clr_matches',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )
    has_passed_kyc = models.BooleanField(default=False, help_text=_('Has this grant gone through KYC?'))
    ready_for_test_payout = models.BooleanField(default=False, help_text=_('Ready for test payout or not'))
    test_payout_tx = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('The test payout txid'),
    )
    test_payout_tx_date = models.DateTimeField(null=True, blank=True)
    test_payout_contribution = models.ForeignKey(
        'grants.Contribution',
        related_name='test_clr_match_payouts',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Contribution for the test payout')
    )

    ready_for_payout = models.BooleanField(default=False, help_text=_('Ready for regular payout or not'))
    payout_tx = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('The test payout txid'),
    )
    payout_tx_date = models.DateTimeField(null=True, blank=True)
    payout_contribution = models.ForeignKey(
        'grants.Contribution',
        related_name='clr_match_payouts',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Contribution for the payout')
    )
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))


    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, grant: {self.grant.pk}, round: {self.round_number}, amount: {self.amount}"



class MatchPledge(SuperModel):
    """Define the structure of a MatchingPledge."""

    PLEDGE_TYPES = [
        ('tech', 'tech'),
        ('media', 'media'),
        ('health', 'health'),
        ('change', 'change')
    ]

    active = models.BooleanField(default=False, help_text=_('Whether or not the MatchingPledge is active.'))
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='matchPledges',
        on_delete=models.CASCADE,
        help_text=_('The MatchingPledgers profile.'),
        null=True,
    )
    amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The matching pledge amount in DAI.'),
    )
    pledge_type = models.CharField(max_length=15, null=True, blank=True, choices=PLEDGE_TYPES, help_text=_('CLR pledge type'))
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    end_date = models.DateTimeField(null=False, default=next_month)
    data = JSONField(null=True, blank=True)
    clr_round_num = models.ForeignKey(
        'grants.GrantCLR',
        on_delete=models.CASCADE,
        help_text=_('Pledge CLR Round.'),
        null=True,
        blank=True
    )

    @property
    def data_json(self):
        import json
        return json.loads(self.data)

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.profile} <> {self.amount} DAI"

class PhantomFunding(SuperModel):
    """Define the structure of a PhantomFunding object.

    For Grants, we have a fund we’re contributing on their behalf.  just having a quick button they can push saves all the hassle of (1) asking them their wallet, (2) sending them the DAI (3) contributing it.

    """

    round_number = models.PositiveIntegerField(blank=True, null=True)
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated grant being Phantom Funding.'),
    )

    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated profile doing the Phantom Funding.'),
    )

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.round_number}; {self.profile} <> {self.grant}"

    def competing_phantum_funds(self):
        return PhantomFunding.objects.filter(profile=self.profile, round_number=self.round_number)

    @property
    def value(self):
        return 5/(self.competing_phantum_funds().count())

    def to_mock_contribution(self):
        context = self.to_standard_dict()
        context['subscription'] = {
            'contributor_profile': self.profile,
            'amount_per_period': self.value,
            'token_symbol': 'DAI',
        }
        context['tx_cleared'] = True
        context['success'] = True
        return context


class CartActivity(SuperModel):
    ACTIONS = (
        ('ADD_ITEM', 'Add item to cart'),
        ('REMOVE_ITEM', 'Remove item to cart'),
        ('CLEAR_CART', 'Clear cart')
    )
    grant = models.ForeignKey(Grant, null=True, on_delete=models.CASCADE, related_name='cart_actions',
                              help_text=_('Related Grant Activity '))
    profile = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE, related_name='cart_activity',
                                help_text=_('User Cart Activity'))
    action = models.CharField(max_length=20, choices=ACTIONS, help_text=_('Type of activity'))
    metadata = JSONField(default=dict, blank=True, help_text=_('Related data to the action'))
    bulk = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.action} {self.grant.id if self.grant else "bulk"} from the cart {self.profile.handle}'


class CollectionsQuerySet(models.QuerySet):
    """Handle the manager queryset for Collections."""

    def visible(self):
        """Filter results down to visible collections only."""
        return self.filter(hidden=False)

    def keyword(self, keyword):
        if not keyword:
            return self
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(profile__handle__icontains=keyword)
        )


class GrantCollection(SuperModel):
    grants = models.ManyToManyField(blank=True, to=Grant, help_text=_('References to grants related to this collection'))
    profile = models.ForeignKey('dashboard.Profile', help_text=_('Owner of the collection'), related_name='curator', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text=_('Name of the collection'))
    description = models.TextField(default='', blank=True, help_text=_('The description of the collection'))
    cover = models.ImageField(upload_to=get_upload_filename, null=True,blank=True, max_length=500, help_text=_('Collection image'))
    hidden = models.BooleanField(default=False, help_text=_('Hide the collection'), db_index=True)
    cache = JSONField(default=dict, blank=True, help_text=_('Easy access to grant info'),)
    featured = models.BooleanField(default=False, help_text=_('Show grant as featured'))
    objects = CollectionsQuerySet.as_manager()
    curators = models.ManyToManyField(blank=True, to='dashboard.Profile', help_text=_('List of allowed curators'))

    def generate_cache(self):
        grants = self.grants.all()

        cache = {
            'count': grants.count(),
            'grants': [{
                'id': grant.id,
                'logo': grant.logo.url if grant.logo and grant.logo.url else f'v2/images/grants/logos/{self.id % 3}.png',
            } for grant in grants]
        }

        self.cache = cache
        self.save()

    def to_json_dict(self):
        curators = [{
            'url': curator.url,
            'handle': curator.handle,
            'avatar_url': curator.avatar_url
        } for curator in self.curators.all()]

        owner = {
            'url': self.profile.url,
            'handle': self.profile.handle,
            'avatar_url': self.profile.avatar_url
        }
        return {
            'id': self.id,
            'owner': owner,
            'title': self.title,
            'description': self.description,
            'cover': self.cover.url if self.cover else '',
            'count': self.cache['count'],
            'grants': self.cache['grants'],
            'curators': curators + [owner]
        }

class GrantStat(SuperModel):
    SNAPSHOT_TYPES = [
        ('total', 'total'),
        ('increment', 'increment')
    ]

    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='stats',
                              help_text=_('Grant to add stats for this grant'))
    data = JSONField(default=dict, blank=True, help_text=_('Stats for this Grant'))
    snapshot_type = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        help_text=_('Snapshot Type'),
        db_index=True,
        choices=SNAPSHOT_TYPES,
    )

    def __str__(self):
        return f'{self.snapshot_type} {self.created_on} for {self.grant.title}'
