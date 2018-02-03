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
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Bounty, BountySyncRequest, Interest, Profile, Subscription, Tip


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


class ProfileAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['email', 'data']


class TipAdmin(admin.ModelAdmin):
    ordering = ['-id']
    readonly_fields = ['resend']
    search_fields = ['tokenName', 'comments_public', 'comments_priv', 'from_name', 'username', 'network', 'github_url', 'url', 'emails']

    def resend(self, instance):
        html = format_html('<a href="/_administration/email/new_tip/resend?pk={}">resend</a>', instance.pk)
        return html


# Register your models here.
class Bounty_Admin(admin.ModelAdmin):
    ordering = ['-id']

    search_fields = ['raw_data', 'title', 'bounty_owner_github_username', 'token_name']
    list_display = ['pk', 'img', 'what']
    readonly_fields = ['what', 'img']

    def img(self, instance):
        if not instance.avatar_url:
            return 'n/a'
        img_html = format_html("<img src={} style='max-width:30px; max-height: 30px'>", mark_safe(instance.avatar_url))
        return img_html

    def what(self, instance):
        return str(instance)


admin.site.register(Subscription, GeneralAdmin)
admin.site.register(Interest, GeneralAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Bounty, Bounty_Admin)
admin.site.register(BountySyncRequest, GeneralAdmin)
admin.site.register(Tip, TipAdmin)
