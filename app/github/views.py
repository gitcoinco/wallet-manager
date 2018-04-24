# -*- coding: utf-8 -*-
"""Handle github views.

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

from __future__ import print_function, unicode_literals

import logging
import time

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.views.decorators.http import require_GET

from app.utils import get_location_from_ip
from dashboard.models import Profile, UserAction
from github.utils import (
    get_auth_url, get_github_primary_email, get_github_user_data, get_github_user_token, revoke_token,
)
from ipware.ip import get_real_ip


@require_GET
def github_callback(request):
    """Handle the Github authentication callback."""
    # Get request parameters to handle authentication and the redirect.
    code = request.GET.get('code', None)
    redirect_uri = request.GET.get('redirect_uri')

    if not code or not redirect_uri:
        raise Http404

    # Get OAuth token and github user data.
    access_token = get_github_user_token(code)
    github_user_data = get_github_user_data(access_token)
    handle = github_user_data.get('login')
    ip_address = '24.210.224.38' if settings.DEBUG else get_real_ip(request)
    geolocation_data = {}

    if ip_address:
        geolocation_data = get_location_from_ip(ip_address)

    if handle:
        # Create or update the Profile with the github user data.
        user_profile, _ = Profile.objects.update_or_create(
            handle=handle,
            defaults={
                'data': github_user_data or {},
                'email': get_github_primary_email(access_token),
                'github_access_token': access_token
            })

        # Update the user's session with handle, email info, preffered language.
        session_data = {
            'handle': user_profile.handle,
            'email': user_profile.email,
            'access_token': user_profile.github_access_token,
            'profile_id': user_profile.pk,
            'name': user_profile.data.get('name', None),
            'access_token_last_validated': timezone.now().isoformat()
        }

        if user_profile.pref_lang_code:
            session_data[LANGUAGE_SESSION_KEY] = user_profile.pref_lang_code

        for k, v in session_data.items():            
            request.session[k] = v

        # record a useraction for this
        UserAction.objects.create(
            profile=user_profile,
            action='Login',
            metadata={},
            ip_address=ip_address,
            location_data=geolocation_data)

    response = redirect(redirect_uri)
    response.set_cookie('last_github_auth_mutation', int(time.time()))
    return response


@require_GET
def github_authentication(request):
    """Handle Github authentication."""
    redirect_uri = request.GET.get('redirect_uri', '/')

    if not request.session.get('access_token'):
        return redirect(get_auth_url(redirect_uri))

    # Alert local developer that Github integration needs configured.
    if settings.ENV == 'local' and (not settings.GITHUB_CLIENT_ID or settings.GITHUB_CLIENT_ID == 'TODO'):
        logging.info('GITHUB_CLIENT_ID is not set. Github integration is disabled!')

    response = redirect(redirect_uri)
    response.set_cookie('last_github_auth_mutation', int(time.time()))
    return response


def github_logout(request):
    """Handle Github logout."""
    access_token = request.session.pop('access_token', '')
    handle = request.session.pop('handle', '')
    redirect_uri = request.GET.get('redirect_uri', '/')
    geolocation_data = {}
    ip_address = '24.210.224.38' if settings.DEBUG else get_real_ip(request)

    if ip_address:
        geolocation_data = get_location_from_ip(ip_address)

    if access_token:
        revoke_token(access_token)
        request.session.pop('access_token_last_validated')

    try:
        # If the profile exists, clear the github access token.
        profile = Profile.objects.get(handle=handle)
        profile.github_access_token = ''
        profile.save()

        # record a useraction for this
        UserAction.objects.create(
            profile=profile,
            action='Logout',
            metadata={},
            ip_address=ip_address,
            location_data=geolocation_data)
    except Profile.DoesNotExist:
        pass

    request.session.modified = True
    response = redirect(redirect_uri)
    response.set_cookie('last_github_auth_mutation', int(time.time()))
    return response
