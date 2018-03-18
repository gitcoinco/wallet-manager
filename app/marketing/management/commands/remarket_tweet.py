# -*- coding: utf-8 -*-
#!/usr/bin/env python3
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
from django.core.management.base import BaseCommand

from dashboard.models import Bounty
from dashboard.notifications import maybe_market_to_twitter


class Command(BaseCommand):

    help = 'sends bounties quotes to twitter'

    def handle(self, *args, **options):
        return  # per 2018/01/22 convo with vivek / kevin, these tweets have low engagement
        # we are going to test manually promoting these tweets for a week and come back to revisit this
        bounties = Bounty.objects.filter(
            current_bounty=True,
            network='mainnet',
            idx_status='open')
        if bounties.count() < 3:
            print('count is only {}. exiting'.format(bounties.count()))
            return
        bounty = bounties.order_by('?').first()
        print(bounty)
        did_tweet = maybe_market_to_twitter(bounty, 'remarket_bounty')
        print(did_tweet)
