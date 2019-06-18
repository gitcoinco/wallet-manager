# -*- coding: utf-8 -*-
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

from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

''''
Context Parameters For the ETHEREAL VIRTUAL HACKATHON static landing page
'''
eth_hack = {
    'hackathon_id'  : 'eth_hack',
    'meta_description': _('Ethereal Virtual Hackathon, powered by Gitcoin and Microsoft'),
    'primary_color' : 'ethhk-pink-bg',
    'bg'            : 'ethhk-blue-bg',
    'banner_text'   : 'ethhk-white-f',
    'logo'          : static('v2/images/hackathon/ethereal.svg'),
    'logo_bg'       : 'ethhk-banner-bg',
    'title'         : 'ETHEREAL VIRTUAL HACKATHON',
    'title_banner'  : 'ETHEREAL <br> VIRTUAL HACKATHON',
    'subtitle'      : _('The largest Ethereum virtual hackathon'),
    'powered_by'    : [
        {
            'name'  : 'gitcoin',
            'logo'  : static('v2/images/top-bar/gitcoin-logo.svg')
        },
        {
            'name'  : 'eth',
            'logo'  : static('v2/images/hackathon/ethhack/microsoft.svg')   
        }
    ],
    'period'        : _('April 15th, 2019 - April 30th, 2019'),
    'register_link' : _('https://gitcoin.typeform.com/to/j7CSbV'),
    'discord_link'  : _('https://discord.gg/TxRKTn8'),
    'prize_link'    : _('https://gitcoin.co/hackathon/ethereal-virtual-hackathon/'),
    'results_link'  : _('https://medium.com/gitcoin/the-results-msft-gitcoins-ethereal-hackathon-30f5ed05757e'),
    'starter_guide' : _('https://medium.com/gitcoin/ethereal-virtual-hackathon-get-started-92084f05d9ee'),
    'sponsors_gold' : [
        {
            'name'  : 'Quorum',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/quorum.svg')
        },
        {
            'name'  : 'Consensys Labs',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/labs-logo-blue.svg')
        },
        {
            'name'  : 'MythX',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/mythx-light.png')
        },
        {
            'name'  : 'Pegasys',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/pegasys-logo.svg')
        },
        {
            'name'  : 'Microsoft',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/microsoft.svg')
        },
        {
            'name'  : 'Adex',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/adex-vector-logo.svg')
        }            
    ],
    'sponsors_silver' : [
        {
            'name'  : 'Chainlink',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/chainlink-hexagon.svg')
        },
        {
            'name'  : 'Kauri',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/kauri_logo_vertical.svg')
        },
        {
            'name'  : 'LeapDAO',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/leapdao.svg')
        },
        {
            'name'  : 'Kleros',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/kleros-logo-vertical.svg')
        },
        {
            'name'  : 'Alethio',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/alethio-no-bg.svg')
        },
        {
            'name'  : 'Coinmark',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/coinmark_blue_lg.svg')
        },
        {
            'name'  : 'Autom(8)',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/autom8.svg')
        },
        {
            'name'  : 'POA',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/logo_poa.svg')
        }
    ],
    'sections' : [
        {
            'title'         : _('Participate today!'),
            'bg'            : 'ethhk-blue-bg',
            'subtitle'      : '''During this hackathon, you can participate in <br>tens of thousands of dollars of bounties, <br>
                with the TOP projects in the Ethereum space, from anywhere!''',
            'font-bg-color'    : 'black-f',
        },
        {
            'title'     : 'April 15th - April 30th',
            'bg'        : 'ethhk-white-bg',
            'register_link' : True,
            'subtitle'  : 'Hackathon challenges will be posted as bounties, <br> with the best hacks receiving prizes in ETH & ERC-20 tokens.',
            'content'   : ''' Main track winners will receive free tickets to Ethereal NY
                to present their project live on stage. <br>
                Bounty winners can build relationships with the top employers in the space <br> 
                & win up to $7k each (varies by sponsor).
                Referral bountiy now live! <br> There is a $500 bounty to refer hackathon participants to the hackathon.'''
        },
        {
            'title'         : _('Fund a Prize Bounty'),
            'bg'            : 'ethhk-blue-bg',
            'subtitle'      : _('Have an epic challenge you want to see the community tackle? <br> Registrations are CLOSED for this hackathon, <br> but you can sign up for our next hackathon below.'),
            'img'           :  static('v2/images/hackathon/bot.svg')
        }
    ],
    'notification': '<strong class="mr-2">Did you know?</strong> - Gitcoin has delivered over $1mm to Open Source developers in the last year. <a href="https://gitcoin.co/results">See our results</a>',
    'footer_links': [
        {
            'logo'  : static('v2/images/top-bar/gitcoin-logo.svg'),
            'name'  : 'Gitcoin',
            'link'  : 'https://gitcoin.co/'
        },
        {
            'logo'  : static('v2/images/hackathon/ethhack/microsoft.svg'),
            'name'  : 'Microsoft',
            'link'  : 'https://www.microsoft.com/'
        },
        {
            'logo'  : static('v2/images/hackathon/ethmain.svg'),
            'name'  : 'Ethereal Summit',
            'link'  : 'https://etherealsummit.com/'
        }
    ]
}
