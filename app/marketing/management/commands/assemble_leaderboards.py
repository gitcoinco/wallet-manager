# -*- coding: utf-8 -*-
"""Define the management command to assemble leaderboard rankings.

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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Profile, Tip
from marketing.models import LeaderboardRank

IGNORE_PAYERS = []
IGNORE_EARNERS = ['owocki']  # sometimes owocki pays to himself. what a jerk!

days_back = 7
if settings.DEBUG:
    days_back = 30
weekly_cutoff = timezone.now() - timezone.timedelta(days=days_back)
monthly_cutoff = timezone.now() - timezone.timedelta(days=30)
quarterly_cutoff = timezone.now() - timezone.timedelta(days=90)
yearly_cutoff = timezone.now() - timezone.timedelta(days=365)


def default_ranks():
    """Generate a dictionary of nested dictionaries defining default ranks.

    Returns:
        dict: A nested dictionary mapping of all default ranks with empty dicts.

    """
    times = ['all', 'weekly', 'quarterly', 'yearly', 'monthly']
    breakdowns = ['fulfilled', 'all', 'payers', 'earners', 'orgs', 'keywords', 'tokens']
    return_dict = {}
    for time in times:
        for bd in breakdowns:
            key = f'{time}_{bd}'
            return_dict[key] = {}

    return return_dict

ranks = default_ranks()
counts = default_ranks()


def add_element(key, username, amount):
    username = username.replace('@', '')
    if not username or username == "None":
        return
    if username not in ranks[key].keys():
        ranks[key][username] = 0
    if username not in counts[key].keys():
        counts[key][username] = 0
    ranks[key][username] += round(float(amount), 2)
    counts[key][username] += 1


def sum_bounty_helper(b, breakdown, username, val_usd):
    fulfiller_usernames = list(b.fulfillments.filter(accepted=True).values_list('fulfiller_github_username', flat=True))
    add_element(f'{breakdown}_fulfilled', username, val_usd)
    if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
        add_element(f'{breakdown}_payers', username, val_usd)
    if username == b.org_name and username not in IGNORE_PAYERS:
        add_element(f'{breakdown}_orgs', username, val_usd)
    if username in fulfiller_usernames and username not in IGNORE_EARNERS:
        add_element(f'{breakdown}_earners', username, val_usd)
    if b.token_name == username:
        add_element(f'{breakdown}_tokens', username, val_usd)
    if username in b.keywords_list:
        add_element(f'{breakdown}_keywords', username, val_usd)


def sum_bounties(b, usernames):
    val_usd = b._val_usd_db
    for username in usernames:
        if b.idx_status == 'done':
            breakdown = 'all'
            sum_bounty_helper(b, breakdown, username, val_usd)
            ###############################
            if b.created_on > weekly_cutoff:
                breakdown = 'weekly'
                sum_bounty_helper(b, breakdown, username, val_usd)
            if b.created_on > monthly_cutoff:
                breakdown = 'monthly'
                sum_bounty_helper(b, breakdown, username, val_usd)
            if b.created_on > quarterly_cutoff:
                breakdown = 'quarterly'
                sum_bounty_helper(b, breakdown, username, val_usd)
            if b.created_on > yearly_cutoff:
                breakdown = 'yearly'
                sum_bounty_helper(b, breakdown, username, val_usd)

        add_element('all_all', username, b._val_usd_db)
        if b.created_on > weekly_cutoff:
            add_element('weekly_all', username, b._val_usd_db)
        if b.created_on > monthly_cutoff:
            add_element('monthly_all', username, b._val_usd_db)
        if b.created_on > yearly_cutoff:
            add_element('yearly_all', username, b._val_usd_db)


def sum_tip_helper(t, breakdown, username, val_usd):
    add_element(f'{breakdown}_all', username, val_usd)
    add_element(f'{breakdown}_fulfilled', username, val_usd)
    if t.username == username or breakdown == 'all':
        add_element(f'{breakdown}_earners', username, val_usd)
    if t.from_username == username:
        add_element(f'{breakdown}_payers', username, val_usd)
    if t.org_name == username:
        add_element(f'{breakdown}_orgs', username, val_usd)
    if t.tokenName == username:
        add_element(f'{breakdown}_tokens', username, val_usd)


def sum_tips(t, usernames):
    val_usd = t.value_in_usdt_now
    for username in usernames:
        breakdown = 'all'
        sum_tip_helper(t, breakdown, username, val_usd)
        #####################################
        if t.created_on > weekly_cutoff:
            breakdown = 'weekly'
            sum_tip_helper(t, breakdown, username, val_usd)
        if t.created_on > monthly_cutoff:
            breakdown = 'monthly'
            sum_tip_helper(t, breakdown, username, val_usd)
        if t.created_on > quarterly_cutoff:
            breakdown = 'quarterly'
            sum_tip_helper(t, breakdown, username, val_usd)
        if t.created_on > yearly_cutoff:
            breakdown = 'yearly'
            sum_tip_helper(t, breakdown, username, val_usd)


def should_suppress_leaderboard(handle):
    if not handle:
        return True
    profiles = Profile.objects.filter(handle__iexact=handle)
    if profiles.exists():
        profile = profiles.first()
        if profile.suppress_leaderboard or profile.hide_profile:
            return True
    return False


class Command(BaseCommand):

    help = 'creates leaderboard objects'

    def handle(self, *args, **options):
        # get bounties
        bounties = Bounty.objects.current().filter(network='mainnet')

        # iterate
        for b in bounties:
            if not b._val_usd_db:
                continue

            usernames = []
            if not should_suppress_leaderboard(b.bounty_owner_github_username):
                usernames.append(b.bounty_owner_github_username)
                if b.org_name:
                    usernames.append(b.org_name)
            for fulfiller in b.fulfillments.filter(accepted=True):
                if not should_suppress_leaderboard(fulfiller.fulfiller_github_username):
                    usernames.append(fulfiller.fulfiller_github_username)
            for keyword in b.keywords_list:
                usernames.append(keyword)

            usernames.append(b.token_name)

            sum_bounties(b, usernames)

        # tips
        tips = Tip.objects.exclude(txid='')

        for t in tips:
            if not t.value_in_usdt_now:
                continue
            usernames = []
            if not should_suppress_leaderboard(t.username):
                usernames.append(t.username)
            if not should_suppress_leaderboard(t.from_username):
                usernames.append(t.from_username)
            if not should_suppress_leaderboard(t.org_name):
                usernames.append(t.org_name)
            if not should_suppress_leaderboard(t.tokenName):
                usernames.append(t.tokenName)

            sum_tips(t, usernames)

        # set old LR as inactive
        for lr in LeaderboardRank.objects.filter(active=True):
            lr.active = False
            lr.save()

        # save new LR in DB
        for key, rankings in ranks.items():
            rank = 1
            for username, amount in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
                count = counts[key][username]
                LeaderboardRank.objects.create(
                    github_username=username,
                    leaderboard=key,
                    amount=amount,
                    count=count,
                    active=True,
                    rank=rank,
                )
                rank += 1
                print(key, username, amount, count, rank)
