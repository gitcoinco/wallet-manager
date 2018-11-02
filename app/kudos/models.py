# -*- coding: utf-8 -*-
"""Define models.

Copyright (C) 2018 Gitcoin Core

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
from io import BytesIO

from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

import environ
import pyvips
from dashboard.models import SendCryptoAsset
from economy.models import SuperModel
from eth_utils import to_checksum_address
from pyvips.error import Error as VipsError

logger = logging.getLogger(__name__)


class Token(SuperModel):
    """Model representing a Kudos ERC721 token on the blockchain.

    The model attempts to match the actual blockchain data as much as possible, without being duplicative.

    Attributes:
        artist (str): The artist that created the kudos image.
        background_color (str): 6 digit hex code background color.  See Open Sea docs for details.
        cloned_from_id (int): Orignal Kudos that this one was cloned from.
        contract (FK): Foreing key to the Contract model.
        description (str): Description of the kudos.
        external_url (str): External URL pointer to image asset.  See Open Sea docs for details.
        image (str): Image file name.
        name (str): Kudos name.
        num_clones_allowed (int): How many clones are allowed to be made.
        num_clones_available (int): How many clones the Kudos has left.
        num_clones_in_wild (int): How many clones there are in the wild.
        owner_address (str): ETH address of the owner.  Pulled from the `ownerOf` contract function.
        platform (str): Where the Kudos originated from.
        price_finney (int): Price to clone the Kudos in finney.
        rarity (str): Rarity metric, defined in kudos.utils.py
        tags (str): Comma delimited tags.  TODO:  change to array
        token_id (int): the token_id on the blockchain.
        txid (str): The ethereum transaction id that generated this kudos.

    """

    # Kudos Struct (also in contract)
    price_finney = models.IntegerField()
    num_clones_allowed = models.IntegerField(null=True, blank=True)
    num_clones_in_wild = models.IntegerField(null=True, blank=True)
    cloned_from_id = models.IntegerField()
    popularity = models.IntegerField(default=0)
    popularity_week = models.IntegerField(default=0)
    popularity_month = models.IntegerField(default=0)
    popularity_quarter = models.IntegerField(default=0)

    # Kudos metadata from tokenURI (also in contract)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=510)
    image = models.CharField(max_length=255, null=True)
    rarity = models.CharField(max_length=255, null=True)
    tags = models.CharField(max_length=255, null=True)
    artist = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    external_url = models.CharField(max_length=255, null=True)
    background_color = models.CharField(max_length=255, null=True)

    # Extra fields added to database (not on blockchain)
    owner_address = models.CharField(max_length=255)
    txid = models.CharField(max_length=255, null=True, blank=True)
    token_id = models.IntegerField()
    contract = models.ForeignKey(
        'kudos.Contract', related_name='kudos_contract', on_delete=models.SET_NULL, null=True
    )
    hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.owner_address:
            self.owner_address = to_checksum_address(self.owner_address)

        super().save(*args, **kwargs)

    @property
    def price_in_eth(self):
        """Convert price from finney to eth.

        Returns:
            float or int:  price in eth.

        """
        return self.price_finney / 1000

    @property
    def shortened_address(self):
        """Shorten ethereum address to only the first and last 4 digits.

        Returns:
            str: shortened address.

        """
        return self.owner_address[:6] + '...' + self.owner_address[38:]

    @property
    def capitalized_name(self):
        """Capitalize name

        Returns:
            str: Capitalized name.

        """
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def num_clones_available(self):
        """Calculate the number of clones available for a kudos.

        Returns:
            int: Number of clones available.

        """
        r = self.num_clones_allowed - self.num_clones_in_wild
        if r < 0:
            r = 0
        return r

    @property
    def humanized_name(self):
        """Turn snake_case into Snake Case.

        Returns:
            str: The humanized name.

        """
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def tags_as_array(self):
        return [tag.strip() for tag in self.tags.split(',')]

    @property
    def owners(self):
        from dashboard.models import Profile
        related_kudos = Token.objects.select_related('contract').filter(
            name=self.name,
            contract__network=settings.KUDOS_NETWORK,
        )
        related_kudos_transfers = KudosTransfer.objects.filter(kudos_token_cloned_from__in=related_kudos).exclude(txid='')
        related_profiles_pks = related_kudos_transfers.values_list('recipient_profile_id', flat=True)
        related_profiles = Profile.objects.filter(pk__in=related_profiles_pks).distinct()
        return related_profiles

    @property
    def num_clones_available_counting_indirect_send(self):
        return self.num_gen0_clones_allowed - self.num_clones_in_wild_counting_indirect_send

    @property
    def num_clones_in_wild_counting_indirect_send(self):
        num_total_sends_we_know_about = len(self.owners)
        if num_total_sends_we_know_about > self.num_clones_in_wild:
            return num_total_sends_we_know_about
        return self.num_clones_in_wild

    def humanize(self):
        self.owner_address = self.shortened_address
        self.name = self.capitalized_name
        self.num_clones_available = self.get_num_clones_available()
        return self

    @property
    def gen(self):
        if self.pk == self.cloned_from_id:
            return 0
        if not self.cloned_from_id:
            return 0
        return Token.objects.get(pk=self.cloned_from_id).gen + 1

    def __str__(self):
        """Return the string representation of a model."""
        return f"{self.contract.network} Gen {self.gen} Kudos Token: {self.humanized_name}"

    @property
    def as_img(self):
        """Convert the provided buffer to another format.

        Args:
            obj (File): The File/ContentFile object.

        Exceptions:
            Exception: Cowardly catch blanket exceptions here, log it, and return None.

        Returns:
            BytesIO: The BytesIO stream containing the converted File data.
            None: If there is an exception, the method returns None.

        """
        root = environ.Path(__file__) - 2  # Set the base directory to two levels.
        file_path = root('assets') + '/' + self.image
        with open(file_path, 'rb') as f:
            obj = File(f)
            try:
                obj_data = obj.read()
                if obj_data:
                    image = pyvips.Image.new_from_file(obj.name)
                    return BytesIO(image.write_to_buffer(f'.png'))
            except VipsError:
                pass
            except Exception as e:
                logger.error(e)
        return None

    @property
    def img_url(self):
        return f'{settings.BASE_URL}dynamic/kudos/{self.pk}/{slugify(self.name)}'

    @property
    def url(self):
        return f'/kudos/{self.pk}/{slugify(self.name)}'


class KudosTransfer(SendCryptoAsset):
    """Model that represents a request to clone a Kudos.

    Typically this gets created when using the "kudos send" functionality.
    The model is inherited from the SendCryptoAsset model, which is also used by Tips.

    Attributes:
        from_address (str): Eth address of the person that is sending the kudos.
        kudos_token (kudos.Token): Foreign key to the kudos_token that was cloned.
            This is filled in after the kudos has been cloned.
        kudos_token_cloned_from (kudos.Token): Foreign key to the kudos_token that will be cloned and sent.
        recipient_profile (dashboard.Profile): Foreign key to the profile of the person that is being sent the kudos.
        sender_profile (dashboard.Profile): Foreign key to the profile of the person that is sending the kudos.

    """

    # kudos_token_cloned_from is a reference to the original Kudos Token that is being cloned.
    kudos_token_cloned_from = models.ForeignKey(
        'kudos.Token', related_name='kudos_token_cloned_from', on_delete=models.SET_NULL, null=True
    )
    # kudos_token is a reference to the new Kudos Token that is soon to be minted
    kudos_token = models.OneToOneField(
        'kudos.Token', related_name='kudos_transfer', on_delete=models.SET_NULL, null=True, blank=True
    )

    recipient_profile = models.ForeignKey(
        'dashboard.Profile', related_name='received_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='sent_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    trust_url = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.from_address:
            self.from_address = to_checksum_address(self.from_address)
        if self.receive_address:
            self.receive_address = to_checksum_address(self.receive_address)

        super().save(*args, **kwargs)

    @property
    def receive_url(self):
        """URL used for indirect send.  Deprecated in favor of receive_url_for_recipient

        Returns:
            str: URL for recipient.

        """
        return self.receive_url_for_recipient

    @property
    def receive_url_for_recipient(self):
        """URL used for indirect send.  Deprecated in favor of receive_url_for_recipient

        Returns:
            str: URL for recipient.

        """
        try:
            key = self.metadata['reference_hash_for_receipient']
            return f"{settings.BASE_URL}kudos/receive/v3/{key}/{self.txid}/{self.network}"
        except KeyError as e:
            logger.error(e)
            return ''

    def __str__(self):
        """Return the string representation of a model."""
        status = 'funded' if self.txid else 'not funded'
        if self.receive_txid:
            status = 'received'
        return f"({status}) transfer of {self.kudos_token_cloned_from} from {self.sender_profile} to {self.username} on {self.network}"


@receiver(post_save, sender=KudosTransfer, dispatch_uid="psave_kt")
def psave_kt(sender, instance, **kwargs):
    token = instance.kudos_token_cloned_from
    if token:
        all_transfers = KudosTransfer.objects.filter(kudos_token_cloned_from=token).exclude(txid='')
        token.popularity = all_transfers.count()
        token.popularity_week = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=7))).count()
        token.popularity_month = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=30))).count()
        token.popularity_quarter = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=90))).count()
        token.save()


class Contract(SuperModel):

    address = models.CharField(max_length=255, unique=True)
    is_latest = models.BooleanField(default=False)
    network = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.address:
            self.address = to_checksum_address(self.address)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the string representation of a model."""
        return f"{self.address} / {self.network} / {self.is_latest}"



class Wallet(SuperModel):
    """DEPRECATED.  Kudos Address where the tokens are stored.

    Currently not used.  Instead we are using preferred_payout_address for now.

    Attributes:
        address (TYPE): Description
        profile (TYPE): Description

    """

    address = models.CharField(max_length=255, unique=True)
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='kudos_wallets', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        """Return the string representation of a model."""
        return f"Wallet: {self.address} Profile: {self.profile}"
