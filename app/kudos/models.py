# -*- coding: utf-8 -*-
'''
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

'''
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import models

from dashboard.models import SendCryptoAsset
from economy.models import SuperModel
from eth_utils import to_checksum_address

logger = logging.getLogger(__name__)


class Token(SuperModel):
    # Kudos specific fields -- lines up with Kudos contract

    # Kudos Struct
    price_finney = models.IntegerField()
    num_clones_allowed = models.IntegerField(null=True, blank=True)
    num_clones_in_wild = models.IntegerField(null=True, blank=True)
    cloned_from_id = models.IntegerField()

    # Kudos metadata from tokenURI
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

    def save(self, *args, **kwargs):
        if self.owner_address:
            self.owner_address = to_checksum_address(self.owner_address)

        super().save(*args, **kwargs)

    @property
    def price_in_eth(self):
        return self.price_finney / 1000

    @property
    def shortened_address(self):
        return self.owner_address[:6] + '...' + self.owner_address[38:]

    @property
    def capitalized_name(self):
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def num_clones_available(self):
        r = self.num_clones_allowed - self.num_clones_in_wild
        if r < 0:
            r = 0
        return r

    @property
    def humanized_name(self):
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    def humanize(self):
        self.owner_address = self.shortened_address
        self.name = self.capitalized_name
        self.num_clones_available = self.get_num_clones_available()
        return self

    def __str__(self):
        """Return the string representation of a model."""
        return f"Kudos Token: {self.humanized_name}"


class KudosTransfer(SendCryptoAsset):
    # kudos_token_cloned_from is a reference to the original Kudos Token that is being cloned.
    kudos_token_cloned_from = models.ForeignKey(Token, related_name='kudos_token_cloned_from', on_delete=models.SET_NULL, null=True)
    # kudos_token is a reference to the new Kudos Token that is soon to be minted
    kudos_token = models.OneToOneField(Token, related_name='kudos_transfer', on_delete=models.SET_NULL, null=True)

    recipient_profile = models.ForeignKey(
        'dashboard.Profile', related_name='received_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='sent_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.from_address:
            self.from_address = to_checksum_address(self.from_address)
        if self.receive_address:
            self.receive_address = to_checksum_address(self.receive_address)

        super().save(*args, **kwargs)

    @property
    def receive_url(self):
        return self.receive_url_for_recipient

    @property
    def receive_url_for_recipient(self):
        if self.web3_type != 'v3':
            raise Exception

        try:
            key = self.metadata['reference_hash_for_receipient']
            return f"{settings.BASE_URL}kudos/receive/v3/{key}/{self.txid}/{self.network}"
        except KeyError:
            return None

    def __str__(self):
        status = 'funded' if self.txid else 'not funded'

        """Return the string representation of a model."""
        return f"({status}) transfer of {self.kudos_token_cloned_from} from {self.sender_profile} to {self.recipient_profile} on {self.network}"


class Wallet(SuperModel):

    """Kudos Address where the tokens are stored.

    Currently not used.  Instead we are using preferred_payout_address for now.

    Attributes:
        address (TYPE): Description
        profile (TYPE): Description
    """

    address = models.CharField(max_length=255, unique=True)
    profile = models.ForeignKey('dashboard.Profile', related_name='kudos_wallets', on_delete=models.SET_NULL, null=True)

    # def save(self, *args, **kwargs):
    #     self.address = to_checksum_address(self.address)
    #     super().save(*args, **kwargs)

    def __str__(self):
        """Return the string representation of a model."""
        return f"Wallet: {self.address} Profile: {self.profile}"
