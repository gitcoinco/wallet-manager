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

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone

import premailer
from marketing.utils import get_or_save_email_subscriber
from retail.utils import strip_double_chars, strip_html

### RENDERERS


def premailer_transform(html):
    import logging
    import cssutils
    cssutils.log.setLevel(logging.CRITICAL)
    return premailer.transform(html)


def render_tip_email(to_email, tip, is_new):

    warning = tip.network if tip.network != 'mainnet' else ""
    params = {
        'link': tip.url,
        'amount': round(tip.amount, 5),
        'tokenName': tip.tokenName,
        'comments_priv': tip.comments_priv,
        'comments_public': tip.comments_public,
        'tip': tip,
        'show_expires': tip.expires_date < (timezone.now() + timezone.timedelta(days=365)),
        'is_new': is_new,
        'warning': warning,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
        'is_sender': to_email not in tip.emails,
        'is_receiver': to_email in tip.emails,
    }

    response_html = premailer_transform(render_to_string("emails/new_tip.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_match_email(bounty, github_username):
    params = {
        'bounty': bounty,
        'github_username': github_username,
    }
    response_html = premailer_transform(render_to_string("emails/new_match.html", params))
    response_txt = render_to_string("emails/new_match.txt", params)

    return response_html, response_txt


def render_new_bounty(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_new_work_submission(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_rejection.html", params))
    response_txt = render_to_string("emails/new_bounty_rejection.txt", params)

    return response_html, response_txt


def render_bounty_expire_warning(to_email, bounty):
    from django.db.models.functions import Lower

    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))

    fulfiller_emails = list(bounty.fulfillments.annotate(lower_email=Lower('fulfiller_email')).values_list('lower_email'))

    params = {
        'bounty': bounty,
        'num': num,
        'unit': unit,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
        'is_claimee': (to_email.lower() in fulfiller_emails),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):

    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
    }

    response_html = premailer_transform(render_to_string("emails/bounty_startwork_expire_warning.html", params))
    response_txt = render_to_string("emails/bounty_startwork_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):

    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
    }

    response_html = premailer_transform(render_to_string("emails/render_bounty_startwork_expired.html", params))
    response_txt = render_to_string("emails/render_bounty_startwork_expired.txt", params)

    return response_html, response_txt


## ROUNDUP_EMAIL
def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty

    subject = "Gitcoin Weekly | ETHDenver Wrap Up Edition! 🌄"

    intro = '''

<p>
    Hi there.
</p>
<p>
    It was great meeting many of you at <a href="https://ethdenver.com">ETHDenver</a> this past weekend.  ETHDenver was a 1200 person hackathon with dozens of new teams formed during the weekend; and Gitcoin is proud to say that <a href="https://medium.com/gitcoin/gitcoin-ethdenver-wrap-up-cc52d9874b38">we sponosored bounties for much of what was built there!</a>.  We are also happy to show off <a href="https://medium.com/gitcoin/coloradocoin-ethdenver-wrap-up-94fabb667c61">ColoradoCoin</a> -- a physical Ethereum ERC20 token that was built using Gitcoin bounties.
</p>
<p>
    What else is new?  
    <ul>
        <li>
            <a href="https://medium.com/gitcoin/post-mortem-production-issues-2018-02-20-3b4bb4ea003e">
                Post Mortem — Production Issues 2018/02/20
            </a>
        </li>
        <li>
            <a href="https://medium.com/gitcoin/oss-today-some-wins-some-losses-89d1ab46ceb6">
                OSS Today -- Some Wins, Some Losses
            </a>
        </li>
        <li>
            <a href="https://gitcoin.co/community">
                gitcoin.co/community - An index of community calls since Gitcoin was started
            </a>
        </li>
    </ul>
</p>
<p>
    I hope to see you <a href="https://gitcoin.co/slack">on slack</a>, or on the community livestream this Friday at 3pm MST ! 🤖
</p>

'''

    bounties = [
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/MetaMask/metamask-extension/issues/3249'),
            'primer': 'This is a big one, and even better, its from the Metamask team! ~ @owocki',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/TrustWallet/trust-wallet-ios/issues/367'),
            'primer': 'Trust wallet is new to the Gitcoin platform.  Let\'s show them we\'re here to help! 👇\' ~ @owocki',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/MarketProject/Dapp/issues/53'),
            'primer': 'Market Protocol has a $300 bounty up;  Good oppy to play with the Binance API.  ~ @owocki',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/MetaMask/metamask-extension/issues/3133'),
            'primer': 'Last, but certainly not least -- Metamask has a new bounty up!  ~ @owocki',
        },
    ]
    highlights = [
        {
            'who': 'thelostone-mc',
            'what': 'doing XYZ - ABC.',
            'link': 'https://github.com/GridPlus/cryptobridge-contracts/issues/11',
            'link_copy': 'View more here',
        },
        {
            'who': 'vs77bb',
            'what': 'doing XYZ to the ZBC.',
            'link': 'https://github.com/GridPlus/cryptobridge-contracts/issues/11',
            'link_copy': 'View more here',
        },
        {
            'who': 'Demetri',
            'what': 'doing foo to the bar and doing a great job at ',
            'link': 'https://github.com/GridPlus/cryptobridge-contracts/issues/11',
            'link_copy': 'View the PR here here.',
        },
    ]

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'override_back_color': '#15003e',
        'invert_footer': True,
        'hide_header': True,
        'highlights': highlights,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt, subject


### DJANGO REQUESTS


@staff_member_required
def new_tip(request):
    from dashboard.models import Tip
    tip = Tip.objects.last()
    response_html, _ = render_tip_email(settings.CONTACT_EMAIL, tip, True)

    return HttpResponse(response_html)


@staff_member_required
def new_match(request):
    from dashboard.models import Bounty
    response_html, _ = render_match_email(Bounty.objects.exclude(title='').last(), 'owocki')

    return HttpResponse(response_html)


@staff_member_required
def resend_new_tip(request):
    from dashboard.models import Tip
    from marketing.mails import tip_email
    from django.contrib import messages
    from django.shortcuts import redirect

    pk = request.POST.get('pk', request.GET.get('pk'))
    params = {
        'pk': pk,
    }

    if request.POST.get('pk'):
        email = request.POST.get('email')

        if not pk or not email:
            messages.error(request, 'Not sent.  Invalid args.')
            return redirect('/_administration')

        tip = Tip.objects.get(pk=pk)
        tip.emails = tip.emails + [email]
        tip_email(tip, [email], True)
        tip.save()

        messages.success(request, 'Resend sent')

        return redirect('/_administration')

    return TemplateResponse(request, 'resend_tip.html', params)


@staff_member_required
def new_bounty(request):
    from dashboard.models import Bounty

    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)


@staff_member_required
def new_work_submission(request):
    from dashboard.models import Bounty

    bounty = Bounty.objects.filter(idx_status='submitted', current_bounty=True).last()
    response_html, _ = render_new_work_submission(settings.CONTACT_EMAIL, bounty)
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_rejection(request):
    from dashboard.models import Bounty

    response_html, _ = render_new_bounty_rejection(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty

    response_html, _ = render_new_bounty_acceptance(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)

@staff_member_required
def bounty_expire_warning(request):
    from dashboard.models import Bounty

    response_html, _ = render_bounty_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)

@staff_member_required
def start_work_expired(request):
    from dashboard.models import Bounty, Interest

    response_html, _ = render_bounty_startwork_expired(settings.CONTACT_EMAIL, Bounty.objects.all().last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)

@staff_member_required
def start_work_expire_warning(request):
    from dashboard.models import Bounty, Interest

    response_html, _ = render_bounty_startwork_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.all().last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    response_html, txt, subject = render_new_bounty_roundup(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)
