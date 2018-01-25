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

from datetime import datetime

from django.db.models import Q

import django_filters.rest_framework
from rest_framework import routers, serializers, viewsets

from .models import Bounty


# Serializers define the API representation.
class BountySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bounty
        fields = ("url", "created_on", "modified_on", "title", "web3_created", "value_in_token",
                  "token_name", "token_address", "bounty_type", "project_length",
                  "experience_level", "github_url", "github_comments", "github_repository",
                  "bounty_owner_address", "bounty_owner_email",
                  "bounty_owner_github_username", "claimeee_address", "claimee_email",
                  "claimee_github_username", "is_open", "expires_date", "raw_data", "metadata",
                  "claimee_metadata", "current_bounty", 'value_in_eth', 'value_in_usdt', 'status',
                  'now', 'avatar_url', 'value_true', 'issue_description', 'network', 'org_name',
                  'pk', 'issue_description_text')


# ViewSets define the view behavior.
class BountyViewSet(viewsets.ModelViewSet):

    queryset = Bounty.objects.all().order_by('-web3_created')
    serializer_class = BountySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Bounty.objects.filter(current_bounty=True).order_by('-web3_created')

        # filtering
        for key in ['raw_data', 'experience_level', 'project_length', 'bounty_type', 'bounty_owner_address',
                    'idx_status', 'network']:
            if key in self.request.GET.keys():
                # special hack just for looking up bounties posted by a certain person
                request_key = key if key != 'bounty_owner_address' else 'coinbase'
                val = self.request.GET.get(request_key)

                vals = val.strip().split(',')
                _queryset = queryset.none()
                for val in vals:
                    if val.strip():
                        args = {}
                        args['{}__icontains'.format(key)] = val.strip()
                        _queryset = _queryset | queryset.filter(**args)
                queryset = _queryset

        # filter by PK
        if 'pk__gt' in self.request.GET.keys():
            queryset = queryset.filter(pk__gt=self.request.GET.get('pk__gt'))

        # filter by is open or not
        if 'is_open' in self.request.GET.keys():
            queryset = queryset.filter(is_open=self.request.GET.get('is_open') == 'True')
            queryset = queryset.filter(expires_date__gt=datetime.now())

        # filter by urls
        if 'github_url' in self.request.GET.keys():
            urls = self.request.GET.get('github_url').split(',')
            queryset = queryset.filter(github_url__in=urls)

        # filter by github repository
        if 'github_repository' in self.request.GET.keys():
            repositories = self.request.GET.get('github_repository').lower().split(',')
            q = Q()
            for repository in repositories:
                q |= Q(github_url__icontains = repository)
            queryset = queryset.filter(q)

        # order
        order_by = self.request.GET.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'bounties', BountyViewSet)
