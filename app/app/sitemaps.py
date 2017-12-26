from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from dashboard.models import Bounty, Profile


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'dashboard',
            'new_funding',
            'claim_funding',
            'process_funding',
            'funding_details',
            'tip',
            'terms',
            'privacy',
            'cookie',
            'prirp',
            'apitos',
            'about',
            'index',
            'help',
            'whitepaper',
            'whitepaper_access',
            '_leaderboard',
        ]

    def location(self, item):
        return reverse(item)


class IssueSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Bounty.objects.filter(current_bounty=True)

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class ProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Profile.objects.filter()

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


sitemaps = {
    'static': StaticViewSitemap,
    'issues': IssueSitemap,
    'orgs': ProfileSitemap,
}
