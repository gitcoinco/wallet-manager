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
from marketing.models import Stat, EmailSubscriber


def get_stat(key):
    return Stat.objects.filter(key=key).order_by('-created_on').first().val


def should_suppress_email(email):
    queryset = EmailSubscriber.objects.filter(email=email)
    if queryset.exists():
        return queryset.first().preferences.get('level', '') == 'nothing'
    return False


def get_or_save_email_subscriber(email, source):
    queryset = EmailSubscriber.objects.filter(email=email)
    if not queryset.exists():
        es = EmailSubscriber.objects.create(
            email=email,
            source=source,
            )
        es.set_priv()
        es.save()
        return es.priv
    else:
        return queryset.first().priv
