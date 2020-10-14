# -*- coding: utf-8 -*-
"""Define the PToken template tags.

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
from django import template
from django.conf import settings

from dashboard.models import Profile

register = template.Library()


@register.simple_tag
def ptoken_balance(ptoken, profile):
    return ptoken.cached_balances[str(profile.id)]
