# -*- coding: utf-8 -*-
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
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _

import cssutils
import premailer
from marketing.utils import get_or_save_email_subscriber
from retail.utils import strip_double_chars, strip_html

# RENDERERS

# key, name, frequency
MARKETING_EMAILS = [
    ('roundup', _('Roundup Emails'), _('Weekly')),
    ('new_bounty_notifications', _('New Bounty Notification Emails'), _('(up to) Daily')),
    ('important_product_updates', _('Product Update Emails'), _('Quarterly')),
]

TRANSACTIONAL_EMAILS = [
    ('tip', _('Tip Emails'), _('Only when you are sent a tip')),
    ('faucet', _('Faucet Notification Emails'), _('Only when you are sent a faucet distribution')),
    ('bounty', _('Bounty Notification Emails'), _('Only when you\'re active on a bounty')),
    ('bounty_match', _('Bounty Match Emails'), _('Only when you\'ve posted a open bounty and you have a new match')),
    ('bounty_feedback', _('Bounty Feedback Emails'), _('Only after a bounty you participated in is finished.')),
    (
        'bounty_expiration', _('Bounty Expiration Warning Emails'),
        _('Only after you posted a bounty which is going to expire')
    ),
]

ALL_EMAILS = MARKETING_EMAILS + TRANSACTIONAL_EMAILS


def premailer_transform(html):
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
        'show_expires': tip.expires_date < (timezone.now() + timezone.timedelta(days=365)) and tip.expires_date,
        'is_new': is_new,
        'warning': warning,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
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


def render_quarterly_stats(to_email, platform_wide_stats):
    from dashboard.models import Profile
    profile = Profile.objects.filter(email=to_email).first()
    quarterly_stats = profile.get_quarterly_stats
    params = {**quarterly_stats, **platform_wide_stats}
    params['subscriber'] = get_or_save_email_subscriber(to_email, 'internal'),
    print(params)
    response_html = premailer_transform(render_to_string("emails/quarterly_stats.html", params))
    response_txt = render_to_string("emails/quarterly_stats.txt", params)

    return response_html, response_txt


def render_bounty_feedback(bounty, persona='submitter', previous_bounties=[]):
    previous_bounties_str = ", ".join([bounty.github_url for bounty in previous_bounties])
    if persona == 'fulfiller':
        accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
        github_username = " @" + accepted_fulfillments.first().fulfiller_github_username if accepted_fulfillments.exists() and accepted_fulfillments.first().fulfiller_github_username else ""
        txt = f"""
hi{github_username},

thanks for turning around this bounty.  we're hyperfocused on making gitcoin a great place for blockchain developers to hang out, learn new skills, and make a little extra ETH.

in that spirit,  i have a few questions for you.

> what would you say your average hourly rate was for this bounty? {bounty.github_url}

> what was the best thing about working on the platform?  what was the worst?

> would you use gitcoin again?

thanks again for being a member of the community.

kevin

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

"""
    elif persona == 'funder':
        github_username = " @" + bounty.bounty_owner_github_username if bounty.bounty_owner_github_username else ""
        if bounty.status == 'done':
            txt = f"""

hi{github_username},

thanks for putting this bounty ({bounty.github_url}) on gitcoin.  i'm glad to see it was turned around.

we're hyperfocused on making gitcoin a great place for blockchain developers to hang out, learn new skills, and make a little extra ETH.

in that spirit,  i have a few questions for you:

> how much coaching/communication did it take the counterparty to turn around the issue?  was this burdensome?

> what was the best thing about working on the platform?  what was the worst?

> would you use gitcoin again?

thanks for being a member of the community.

kevin

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

"""
        elif bounty.status == 'cancelled':
            txt = f"""
hi{github_username},

we saw that you cancelled this bounty.

i was sorry to see that the bounty did not get done.

i have a few questions for you.

> why did you decide to cancel the bounty?

> would you use gitcoin again?

thanks again for being a member of the community.

kevin

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

"""
        else:
            raise Exception('unknown bounty status')
    else:
        raise Exception('unknown persona')

    params = {
        'txt': txt,
    }
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    response_txt = txt

    return response_html, response_txt



def render_new_bounty(to_email, bounties, old_bounties):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'old_bounties': old_bounties,
        'bounties': bounties,
        'subscriber': sub,
        'keywords': ",".join(sub.keywords),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_gdpr_reconsent(to_email):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'subscriber': sub,
    }

    response_html = premailer_transform(render_to_string("emails/gdpr_reconsent.html", params))
    response_txt = render_to_string("emails/gdpr_reconsent.txt", params)

    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
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
        'is_claimee': (to_email.lower() in fulfiller_emails),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_startwork_expire_warning.html", params))
    response_txt = render_to_string("emails/bounty_startwork_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_unintersted(to_email, bounty, interest):
    params = {
        'bounty': bounty,
        'interest': interest,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_uninterested.html", params))
    response_txt = render_to_string("emails/bounty_uninterested.txt", params)

    return response_html, response_txt


def render_faucet_rejected(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request_rejected.html", params))
    response_txt = render_to_string("emails/faucet_request_rejected.txt", params)

    return response_html, response_txt


def render_faucet_request(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request.html", params))
    response_txt = render_to_string("emails/faucet_request.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/render_bounty_startwork_expired.html", params))
    response_txt = render_to_string("emails/render_bounty_startwork_expired.txt", params)

    return response_html, response_txt


def render_gdpr_update(to_email):
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'terms_of_use_link': 'https://gitcoin.co/legal/terms',
        'privacy_policy_link': 'https://gitcoin.co/legal/privacy',
        'cookie_policy_link': 'https://gitcoin.co/legal/cookie',
    }

    subject = "Gitcoin: Updated Terms & Policies"
    response_html = premailer_transform(render_to_string("emails/gdpr_update.html", params))
    response_txt = render_to_string("emails/gdpr_update.txt", params)

    return response_html, response_txt, subject


def render_start_work_approved(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "Request Accepted "
    response_html = premailer_transform(render_to_string("emails/start_work_approved.html", params))
    response_txt = render_to_string("emails/start_work_approved.txt", params)

    return response_html, response_txt, subject


def render_start_work_rejected(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "Work Request Denied"
    response_html = premailer_transform(render_to_string("emails/start_work_rejected.html", params))
    response_txt = render_to_string("emails/start_work_rejected.txt", params)

    return response_html, response_txt, subject


def render_start_work_new_applicant(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "A new request to work on your bounty"
    response_html = premailer_transform(render_to_string("emails/start_work_new_applicant.html", params))
    response_txt = render_to_string("emails/start_work_new_applicant.txt", params)

    return response_html, response_txt, subject


def render_start_work_applicant_about_to_expire(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "24 Hrs to Approve"
    response_html = premailer_transform(render_to_string("emails/start_work_applicant_about_to_expire.html", params))
    response_txt = render_to_string("emails/start_work_applicant_about_to_expire.txt", params)

    return response_html, response_txt, subject


def render_start_work_applicant_expired(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "A Worker was Auto Approved"
    response_html = premailer_transform(render_to_string("emails/start_work_applicant_expired.html", params))
    response_txt = render_to_string("emails/start_work_applicant_expired.txt", params)

    return response_html, response_txt, subject


# ROUNDUP_EMAIL
def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    from external_bounties.models import ExternalBounty
    subject = "How to Price Work on Gitcoin | Colony Hackathon "

    intro = '''

<p>
    Hi there
</p>
<p>
This week, we shipped a <a href='https://medium.com/gitcoin/funder-guide-how-to-price-work-on-gitcoin-49bafcdd201e'>data-driven pricing guide for posting work on Gitcoin</a>. We share what we’ve learned about pricing for our first 300 bounties and look forward to continuing the analysis as time passes.  
</p>
<p>
We’ve proudly <a href='http://bit.ly/2LsssHG'>partnered up with our friends at Colony for their hackathon</a>! Colony is the Ethereum-based blockchain project building a platform for the future of work. The hackathon features $25K in prizes (paid in Dai) and an all-star panel of 16 judges from the ecosystem.
</p>
<p>
The online hackathon runs June 5th - June 24th and celebrates the release of the colonyJS library—tools that allow developers to leverage the power of Colony’s smart contracts in their own applications.
</p>
<p>
<a href='http://bit.ly/2LsssHG'>You can register here. </a>
</p>
<p style="text-align:center;">
<a href='http://bit.ly/2LsssHG'>
<img style="margin: 0px auto" src='https://gitcoin.co/static/v2/images/colony.png?1' width='450', height='184'>
</a>
</p>
<h3>What else is new?</h3>
    <ul>
        <li>
We released Richard Burton’s demo of Balance on the Gitcoin Livestream channel on YouTube. <a href=https://www.youtube.com/watch?v=SoIJ6JJdO8o&t=4s</a>Check it out here!</a>
        </li>
        <li>
I did a 2 minute interview  on Gitcoin at Ethereal 2018. <a href='https://www.youtube.com/watch?v=pdoa09b_2J4'>See it here.</a>
        </li>
        <li>
<a href='https://gitcoin.co/livestream'>The Gitcoin Livestream </a>is back as regularly scheduled today at 5PM ET. Colony will be joining to speak further on their hackathon alongside Livepeer, a fully decentralized live-video streaming service! 
        </li>
    </ul>
</p>
<p>
Back to BUIDLing, 
</p>
'''
    highlights = [
        {
            'who': 'dilatebrave',
            'who_link': True,
            'what': 'Worked with Bounties Network on Weekly Graph Support',
            'link': 'https://gitcoin.co/issue/Bounties-Network/StdBountiesAnaltyics/4/515',
            'link_copy': 'See more',
        },
        {
            'who': 'iamonuwa',
            'who_link': True,
            'what': 'Created a Smart Contract search engine with AbieFund!',
            'link': 'https://gitcoin.co/issue/AbieFund/abie/5/508',
            'link_copy': 'View more',
        },
        {
            'who': 'antonper',
            'who_link': True,
            'what': 'Cleaned up an error rejection messages on MetaMask! ',
            'link': 'https://gitcoin.co/issue/MetaMask/metamask-extension/1546/499',
            'link_copy': 'View more',
        },
    ]

    try:
        bounties = [
            {
                'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/XLNT/gnarly/issues/8'),
                'primer': 'Ethereum Foundation grantee XLNT needs help with their Gas Price Oracle Reducer!',
            },
            {
                'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/uport-project/buidlbox/issues/17'),
                'primer': 'uPort aims to build a Transaction Manager ',
            },
            {
                'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/paritytech/parity/issues/8725'),
                'primer': 'Contribute to Parity Tech, a leading Ethereum client',
            },
        ]
    except:
        bounties = []

    ecosystem_bounties = ExternalBounty.objects.filter(created_on__gt=timezone.now() - timezone.timedelta(weeks=1)).order_by('?')[0:5]

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'ecosystem_bounties': ecosystem_bounties,
        'invert_footer': False,
        'hide_header': False,
        'highlights': highlights,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt, subject


# DJANGO REQUESTS


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
    bounties = Bounty.objects.filter(current_bounty=True).order_by('-web3_created')[0:3]
    old_bounties = Bounty.objects.filter(current_bounty=True).order_by('-web3_created')[0:3]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties)
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
    response_html, _ = render_new_bounty_rejection(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty
    response_html, _ = render_new_bounty_acceptance(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def bounty_feedback(request):
    from dashboard.models import Bounty
    response_html, _ = render_bounty_feedback(Bounty.objects.filter(idx_status='done', current_bounty=True).last(), 'foo')
    return HttpResponse(response_html)


@staff_member_required
def bounty_expire_warning(request):
    from dashboard.models import Bounty
    response_html, _ = render_bounty_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def start_work_expired(request):
    from dashboard.models import Bounty, Interest
    response_html, _ = render_bounty_startwork_expired(settings.CONTACT_EMAIL, Bounty.objects.last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)


@staff_member_required
def start_work_expire_warning(request):
    from dashboard.models import Bounty, Interest
    response_html, _ = render_bounty_startwork_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)


@staff_member_required
def faucet(request):
    from faucet.models import FaucetRequest
    fr = FaucetRequest.objects.last()
    response_html, _ = render_faucet_request(fr)
    return HttpResponse(response_html)


@staff_member_required
def faucet_rejected(request):
    from faucet.models import FaucetRequest
    fr = FaucetRequest.objects.exclude(comment_admin='').last()
    response_html, _ = render_faucet_rejected(fr)
    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    response_html, _, _ = render_new_bounty_roundup(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)


@staff_member_required
def quarterly_roundup(request):
    from marketing.utils import get_platform_wide_stats
    platform_wide_stats = get_platform_wide_stats()
    response_html, _ = render_quarterly_stats(settings.CONTACT_EMAIL, platform_wide_stats)
    return HttpResponse(response_html)


@staff_member_required
def gdpr_reconsent(request):
    response_html, _ = render_gdpr_reconsent(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)


@staff_member_required
def start_work_approved(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_approved(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_rejected(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_rejected(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_new_applicant(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_new_applicant(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_applicant_about_to_expire(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_about_to_expire(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_applicant_expired(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_expired(interest, bounty)
    return HttpResponse(response_html)
