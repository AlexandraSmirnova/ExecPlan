# coding=utf-8
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from import_export.admin import ImportExportMixin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import messages
from app import settings
from core.models import User
from core.resources import UserResource


@admin.register(User)
class UserAdmin(ImportExportMixin, DjangoUserAdmin):

    list_display = ('get_avatar_img', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')

    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('avatar', 'email', 'password', 'first_name', 'last_name')}),
        (u'Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        (u'Даты', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2'),
            'classes': ('wide',),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    resource_class = UserResource

    def get_avatar_img(self, obj):
        default_avatar = u'core/img/placeholder_200.png'
        img_tag = u'<img src="{0}{1}" width="100" height="100"/>'
        if obj.avatar:
            return format_html(img_tag, settings.MEDIA_URL, obj.avatar)
        return format_html(img_tag, settings.STATIC_URL, default_avatar)
    get_avatar_img.allow_tags = True
    get_avatar_img.description = u'Изображение'


