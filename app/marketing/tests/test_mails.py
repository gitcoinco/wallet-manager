# -*- coding: utf-8 -*-
"""Handle marketing mail related tests.

Copyright (C) 2021 Gitcoin Core

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
from unittest.mock import patch

from django.utils import timezone

from dashboard.models import Profile
from marketing.mails import setup_lang
from test_plus.test import TestCase


class MarketingMailsTest(TestCase):
    """Define tests for marketing mails."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.email = 'user1@gitcoin.co'
        self.user = self.make_user('user1')
        self.user.email = self.email
        self.user.profile = Profile.objects.create(
            user=self.user,
            handle='user1',
            last_sync_date=timezone.now(),
            data={},
        )
        self.user.save()
        self.days = [1, 2, 3]

    @patch('django.utils.translation.activate')
    def test_setup_lang(self, mock_translation_activate):
        """Test the marketing mails setup_lang method."""
        setup_lang(self.email)
        assert mock_translation_activate.call_count == 1
        mock_translation_activate.assert_called_once_with('en-us')

    @patch('django.utils.translation.activate')
    def test_setup_lang_no_user(self, mock_translation_activate):
        """Test the marketing mails setup_lang method."""
        setup_lang('bademail@gitcoin.co')
        assert mock_translation_activate.call_count == 0
