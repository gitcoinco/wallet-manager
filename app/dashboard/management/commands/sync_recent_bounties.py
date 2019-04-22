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


from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'syncs all bounties with geth'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)

    def handle(self, *args, **options):
        # config
        network = options['network']
        call_command('sync_geth', network, -200, 0)
