'''
    Copyright (C) 2019 Gitcoin Core

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

from marketing.mails import notify_deadbeat_quest


class Command(BaseCommand):

    help = 'finds (and migrates) quests whose reward is out of redemptions'

    def add_arguments(self, parser):
        parser.add_argument(
            'kudos_id',
            type=int,
            help="what kudos to migrate to"
        )

    def handle(self, *args, **options):
        from quests.models import Quest
        from kudos.models import Token
        kudos_id = options['kudos_id']
        kudos = Token.objects.get(pk=kudos_id)

        for quest in Quest.objects.filter(visible=True):
            if quest.kudos_reward:
                is_dead = quest.kudos_reward.num_clones_available_counting_indirect_send <= 0
                is_dead = is_dead or quest.kudos_reward.owner_address.lower() != "0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F".lower()
                if is_dead:
                    print(f"migrating {quest.pk}")
                    quest.kudos_reward = kudos
                    quest.save()
