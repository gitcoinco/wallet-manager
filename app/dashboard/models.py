'''
    Copyright (C) 2017 Gitcoin Core

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

'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.utils import timezone

import requests
from dashboard.tokens import addr_to_token
from economy.models import SuperModel
from economy.utils import convert_amount
from rest_framework import serializers

from .signals import m2m_changed_interested


class Bounty(SuperModel):
    """Define the structure of a Bounty.

    Attributes:
        BOUNTY_TYPES (list of tuples): The valid bounty types.
        EXPERIENCE_LEVELS (list of tuples): The valid experience levels.
        PROJECT_LENGTHS (list of tuples): The possible project lengths.

    """

    class Meta:
        """Define metadata associated with Bounty."""

        verbose_name_plural = 'Bounties'

    BOUNTY_TYPES = [
        ('Bug', 'Bug'),
        ('Security', 'Security'),
        ('Feature', 'Feature'),
        ('Unknown', 'Unknown'),
    ]
    EXPERIENCE_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Unknown', 'Unknown'),
    ]
    PROJECT_LENGTHS = [
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Unknown', 'Unknown'),
    ]
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField()
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    github_url = models.URLField()
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, null=True)
    bounty_owner_github_username = models.CharField(max_length=255, null=True)
    claimeee_address = models.CharField(max_length=50)
    claimee_email = models.CharField(max_length=255, null=True)
    claimee_github_username = models.CharField(max_length=255, null=True)
    is_open = models.BooleanField()
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default={})
    claimee_metadata = JSONField(default={})
    current_bounty = models.BooleanField(default=False)  # whether this bounty is the most current revision one or not
    _val_usd_db = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    contract_address = models.CharField(max_length=50, default='')
    network = models.CharField(max_length=255, null=True)
    idx_experience_level = models.IntegerField(default=0, db_index=True)
    idx_project_length = models.IntegerField(default=0, db_index=True)
    idx_status = models.CharField(max_length=50, default='')
    avatar_url = models.CharField(max_length=255, default='')
    issue_description = models.TextField(default='')
    interested = models.ManyToManyField('dashboard.Interest')
    interested_comment = models.IntegerField(null=True)

    def __str__(self):
        return "{}{} {} {} {}".format("(CURRENT) " if self.current_bounty else "", self.title, self.value_in_token,
                                      self.token_name, self.web3_created)

    def get_absolute_url(self):
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)

    def get_relative_url(self, preceding_slash=True):
        return "{}funding/details?url={}".format('/' if preceding_slash else '', self.github_url)

    def get_natural_value(self):
        token = addr_to_token(self.token_address)
        if not token:
            return 0
        decimals = token.get('decimals', 0)
        return float(self.value_in_token) / 10**decimals

    @property
    def url(self):
        return self.get_relative_url()

    @property
    def title_or_desc(self):
        """Return the title of the issue."""
        if not self.title:
            title = self.fetch_issue_item('title') or self.github_url
            return title
        return self.title

    @property
    def issue_description_text(self):
        import re
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        return tag_re.sub('', self.issue_description).strip()

    @property
    def org_name(self):
        try:
            from app.github import org_name
            _org_name = org_name(self.github_url)
            return _org_name
        except:
            return None

    def is_hunter(self, handle):
        target = self.claimee_github_username
        if not handle or not target:
            return False
        handle = handle.lower().replace('@', '')
        target = target.lower().replace('@', '')

        return handle == target

    # TODO: DRY
    def is_funder(self, handle):
        target = self.bounty_owner_github_username
        if not handle or not target:
            return False
        handle = handle.lower().replace('@', '')
        target = target.lower().replace('@', '')

        return handle == target


    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def get_avatar_url(self):
        try:
            from app.github import get_user
            response = get_user(self.org_name)
            return response['avatar_url']
        except Exception as e:
            print(e)
            return 'https://avatars0.githubusercontent.com/u/31359507?v=4'

    @property
    def local_avatar_url(self):
        return "https://gitcoin.co/funding/avatar?repo={}&v=3".format(self.github_url)

    @property
    def keywords(self):
        try:
            return self.metadata.get('issueKeywords', False)
        except:
            return False

    @property
    def now(self):
        return timezone.now()

    @property
    def status(self):
        try:
            if not self.is_open:
                if timezone.now() > self.expires_date and self.claimeee_address == '0x0000000000000000000000000000000000000000':
                    return 'expired'
                return 'fulfilled'
            if self.claimeee_address == '0x0000000000000000000000000000000000000000':
                return 'open'
            if self.claimeee_address != '0x0000000000000000000000000000000000000000':
                return 'claimed'
            return 'unknown'
        except:
            return 'unknown'

    @property
    def value_true(self):
        return self.get_natural_value()

    @property
    def value_in_eth(self):
        if self.token_name == 'ETH':
            return self.value_in_token
        try:
            return convert_amount(self.value_in_token, self.token_name, 'ETH')
        except:
            return None

    @property
    def value_in_usdt(self):
        decimals = 10**18
        if self.token_name == 'USDT':
            return self.value_in_token
        try:
            return round(float(convert_amount(self.value_in_eth, 'ETH', 'USDT')) / decimals, 2)
        except:
            return None

    @property
    def desc(self):
        return "{} {} {} {}".format(naturaltime(self.web3_created), self.idx_project_length, self.bounty_type,
                                    self.experience_level)

    @property
    def turnaround_time(self):
        return (self.created_on - self.web3_created).total_seconds()

    def get_github_api_url(self):
        """Get the Github API URL associated with the bounty."""
        from urlparse import urlparse
        if self.github_url.lower()[:19] != 'https://github.com/':
            return
        url_path = urlparse(self.github_url).path
        return 'https://api.github.com/repos/' + url_path

    def fetch_issue_item(self, item_type='body'):
        """Fetch the item type of an issue.

        Args:
            type (str): The github API response body item to be fetched.

        Returns:
            str: The item content.

        """
        issue_description = requests.get(
            self.get_github_api_url(),
            auth=(settings.GIT_API_USER, settings.GITHUB_API_TOKEN))
        if issue_description.status == 200:
            item = issue_description.json()[item_type]
            if item_type == 'body':
                self.issue_description = item
            elif item_type == 'title':
                self.title = item
        else:
            return None


class BountySyncRequest(SuperModel):

    github_url = models.URLField()
    processed = models.BooleanField()


class Subscription(SuperModel):

    email = models.EmailField(max_length=255)
    raw_data = models.TextField()
    ip = models.CharField(max_length=50)

    def __str__(self):
        return "{} {}".format(self.email, (self.created_on))


class Tip(SuperModel):

    emails = JSONField()
    url = models.CharField(max_length=255, default='')
    tokenName = models.CharField(max_length=255)
    tokenAddress = models.CharField(max_length=255)
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments_priv = models.TextField(default='')
    comments_public = models.TextField(default='')
    ip = models.CharField(max_length=50)
    expires_date = models.DateTimeField()
    github_url = models.URLField(null=True)
    from_name = models.CharField(max_length=255, default='')
    from_email = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=255, default='')
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='')
    received_on = models.DateTimeField(null=True)

    def __str__(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        return "({}) - {} {} {} {} to {},  created: {}, expires: {}".format(
               self.network, "RECEIVED" if self.receive_txid else "", "ORPHAN" if len(self.emails) == 0 else "", self.amount, self.tokenName, self.username, naturalday(self.created_on), naturalday(self.expires_date))


    #TODO: DRY
    def get_natural_value(self):
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals']
        return float(self.amount) / 10**decimals

    #TODO: DRY
    @property
    def value_in_eth(self):
        if self.tokenName == 'ETH':
            return self.amount
        try:
            return convert_amount(self.amount, self.tokenName, 'ETH')
        except:
            return None

    # TODO: DRY
    @property
    def value_in_usdt(self):
        decimals = 1
        if self.tokenName == 'USDT':
            return self.amount
        try:
            return round(float(convert_amount(self.value_in_eth, 'ETH', 'USDT')) / decimals, 2)
        except:
            return None


@receiver(pre_save, sender=Bounty, dispatch_uid="normalize_usernames")
def normalize_usernames(sender, instance, **kwargs):

    if instance.claimee_github_username:
        instance.claimee_github_username = instance.claimee_github_username.replace("@", '')
    if instance.bounty_owner_github_username:
        instance.bounty_owner_github_username = instance.bounty_owner_github_username.replace("@", '')


# method for updating
@receiver(pre_save, sender=Bounty, dispatch_uid="psave_bounty")
def psave_bounty(sender, instance, **kwargs):
    idx_experience_level = {
        'Unknown': 1,
        'Beginner': 2,
        'Intermediate': 3,
        'Advanced': 4,
    }

    idx_project_length = {
        'Unknown': 1,
        'Hours': 2,
        'Days': 3,
        'Weeks': 4,
        'Months': 5,
    }

    instance.idx_status = instance.status
    instance._val_usd_db = instance.value_in_usdt if instance.value_in_usdt else 0
    instance.idx_experience_level = idx_experience_level.get(instance.experience_level, 0)
    instance.idx_project_length = idx_project_length.get(instance.project_length, 0)


class Interest(models.Model):
    """Define relationship for profiles expressing interest on a bounty."""

    profile = models.ForeignKey('dashboard.Profile', related_name='interested')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        """Define the string representation of an interested profile."""
        return self.profile.handle


class Profile(SuperModel):
    """Define the structure of the user profile."""

    data = JSONField()
    handle = models.CharField(max_length=255, db_index=True)
    last_sync_date = models.DateTimeField(null=True)
    email = models.CharField(max_length=255, blank=True, db_index=True)
    github_access_token = models.CharField(max_length=255, blank=True, db_index=True)

    _sample_data = '''
        {
          "public_repos": 9,
          "site_admin": false,
          "updated_at": "2017-10-09T22:55:57Z",
          "gravatar_id": "",
          "hireable": null,
          "id": 30044474,
          "followers_url": "https:\/\/api.github.com\/users\/gitcoinco\/followers",
          "following_url": "https:\/\/api.github.com\/users\/gitcoinco\/following{\/other_user}",
          "blog": "https:\/\/gitcoin.co",
          "followers": 0,
          "location": "Boulder, CO",
          "type": "Organization",
          "email": "founders@gitcoin.co",
          "bio": "Push Open Source Forward.",
          "gists_url": "https:\/\/api.github.com\/users\/gitcoinco\/gists{\/gist_id}",
          "company": null,
          "events_url": "https:\/\/api.github.com\/users\/gitcoinco\/events{\/privacy}",
          "html_url": "https:\/\/github.com\/gitcoinco",
          "subscriptions_url": "https:\/\/api.github.com\/users\/gitcoinco\/subscriptions",
          "received_events_url": "https:\/\/api.github.com\/users\/gitcoinco\/received_events",
          "starred_url": "https:\/\/api.github.com\/users\/gitcoinco\/starred{\/owner}{\/repo}",
          "public_gists": 0,
          "name": "Gitcoin Core",
          "organizations_url": "https:\/\/api.github.com\/users\/gitcoinco\/orgs",
          "url": "https:\/\/api.github.com\/users\/gitcoinco",
          "created_at": "2017-07-10T10:50:51Z",
          "avatar_url": "https:\/\/avatars1.githubusercontent.com\/u\/30044474?v=4",
          "repos_url": "https:\/\/api.github.com\/users\/gitcoinco\/repos",
          "following": 0,
          "login": "gitcoinco"
        }
    '''
    repos_data = JSONField(default={})

    _sample_data = '''
    [
      {
        "issues_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues{\/number}",
        "deployments_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/deployments",
        "has_wiki": true,
        "forks_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/forks",
        "mirror_url": null,
        "issue_events_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues\/events{\/number}",
        "stargazers_count": 1,
        "subscription_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/subscription",
        "merges_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/merges",
        "has_pages": false,
        "updated_at": "2017-09-25T11:39:03Z",
        "private": false,
        "pulls_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/pulls{\/number}",
        "issue_comment_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues\/comments{\/number}",
        "full_name": "gitcoinco\/chrome_ext",
        "owner": {
          "following_url": "https:\/\/api.github.com\/users\/gitcoinco\/following{\/other_user}",
          "events_url": "https:\/\/api.github.com\/users\/gitcoinco\/events{\/privacy}",
          "organizations_url": "https:\/\/api.github.com\/users\/gitcoinco\/orgs",
          "url": "https:\/\/api.github.com\/users\/gitcoinco",
          "gists_url": "https:\/\/api.github.com\/users\/gitcoinco\/gists{\/gist_id}",
          "html_url": "https:\/\/github.com\/gitcoinco",
          "subscriptions_url": "https:\/\/api.github.com\/users\/gitcoinco\/subscriptions",
          "avatar_url": "https:\/\/avatars1.githubusercontent.com\/u\/30044474?v=4",
          "repos_url": "https:\/\/api.github.com\/users\/gitcoinco\/repos",
          "received_events_url": "https:\/\/api.github.com\/users\/gitcoinco\/received_events",
          "gravatar_id": "",
          "starred_url": "https:\/\/api.github.com\/users\/gitcoinco\/starred{\/owner}{\/repo}",
          "site_admin": false,
          "login": "gitcoinco",
          "type": "Organization",
          "id": 30044474,
          "followers_url": "https:\/\/api.github.com\/users\/gitcoinco\/followers"
        },
        ...
    ]
    '''

    @property
    def is_org(self):
        return self.data['type'] == 'Organization'

    @property
    def bounties(self):
        bounties = Bounty.objects.filter(github_url__istartswith=self.github_url, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(claimee_github_username__iexact=self.handle, current_bounty=True) | Bounty.objects.filter(claimee_github_username__iexact="@" + self.handle, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(bounty_owner_github_username__iexact=self.handle, current_bounty=True) | Bounty.objects.filter(bounty_owner_github_username__iexact="@" + self.handle, current_bounty=True)
        return bounties.order_by('-web3_created')

    @property
    def tips(self):
        return Tip.objects.filter(github_url__startswith=self.github_url).order_by('-id')

    @property
    def authors(self):
        auto_include_contributors_with_count_gt = 40
        limit_to_num = 10

        _return = []

        for repo in sorted(self.repos_data, key=lambda repo: repo.get('contributions', -1), reverse=True):
            for c in repo.get('contributors', []):
                if type(c) == dict and c.get('contributions', 0) > auto_include_contributors_with_count_gt:
                    _return.append(c['login'])

        include_gitcoin_users = len(_return) < limit_to_num
        if include_gitcoin_users:
            for b in self.bounties:
                vals = [b.bounty_owner_github_username, b.claimee_github_username]
                for val in vals:
                    if val:
                        _return.append(val.replace('@', ''))
            for t in self.tips:
                vals = [t.username]
                for val in vals:
                    if val:
                        _return.append(val.replace('@', ''))
        _return = list(set(_return))
        _return.sort()
        return _return[:limit_to_num]

    @property
    def stats(self):
        bounties = self.bounties
        loyalty_rate = 0
        claimees = []
        total_funded = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_funder(self.handle)])
        total_claimed = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_hunter(self.handle)])
        print(total_funded, total_claimed)
        role = 'newbie'
        if total_funded > total_claimed:
            role = 'funder'
        elif total_funded < total_claimed:
            role = 'coder'

        for b in bounties:
            if b.claimeee_address in claimees:
                loyalty_rate += 1
            claimees.append(b.claimeee_address)
        success_rate = 0
        if bounties.count() > 0:
            numer = bounties.filter(idx_status__in=['fulfilled', 'claimed']).count()
            denom = bounties.exclude(idx_status__in=['open']).count()
            success_rate = int(round(numer * 1.0 / denom, 2) * 100) if denom != 0 else 'N/A'
        if success_rate == 0:
            success_rate = 'N/A'
            loyalty_rate = 'N/A'
        else:
            success_rate = "{}%".format(success_rate)
            loyalty_rate = "{}x".format(loyalty_rate)
        if role == 'newbie':
            return [
                (role, 'Status'),
                (bounties.count(), 'Total Funded Issues'),
                (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        elif role == 'coder':
            return [
                (role, 'Primary Role'),
                (bounties.count(), 'Total Funded Issues'),
                (success_rate, 'Success Rate'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        else: #funder
            return [
                (role, 'Primary Role'),
                (bounties.count(), 'Total Funded Issues'),
                (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
                (success_rate, 'Success Rate'),
            ]

    @property
    def github_url(self):
        return "https://github.com/{}".format(self.handle)

    @property
    def local_avatar_url(self):
        return "https://gitcoin.co/funding/avatar?repo={}&v=3".format(self.github_url)

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def __str__(self):
        return self.handle

    def get_relative_url(self, preceding_slash=True):
        return "{}profile/{}".format('/' if preceding_slash else '', self.handle)

    def get_absolute_url(self):
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)


class ProfileSerializer(serializers.BaseSerializer):
    """Handle serializing the Profile object."""

    class Meta:
        model = Profile
        fields = ('email', 'handle', 'github_access_token')
        extra_kwargs = {'github_access_token': {'write_only': True}}

    def to_representation(self, obj):
        return {
            'handle': obj.handle,
            'email': obj.email,
            'github_url': obj.github_url,
            'local_avatar_url': obj.local_avatar_url,
            'url': obj.get_relative_url()
        }


@receiver(pre_save, sender=Tip, dispatch_uid="normalize_tip_usernames")
def normalize_tip_usernames(sender, instance, **kwargs):

    if instance.username:
        instance.username = instance.username.replace("@", '')


m2m_changed.connect(m2m_changed_interested, sender=Bounty.interested.through)
