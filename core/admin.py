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
    change_form_template = 'admin/user_change.html'

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

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<user_id>\d+)/login_as_user/$',
                self.admin_site.admin_view(self.login_as_user),
                name='login_as_user'),
        ]
        return my_urls + urls

    @staticmethod
    def login_as_user(request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            messages.add_message(request, messages.ERROR, u'Несуществующий пользователь')
            return HttpResponseRedirect('/ssadmin/core/user/{0}/'.format(user_id))

        user = authenticate(admin=request.user, email=user.email)
        login(request, user)
        return HttpResponseRedirect(reverse('core:profile'))

    def get_avatar_img(self, obj):
        default_avatar = u'core/img/placeholder_200.png'
        img_tag = u'<img src="{0}{1}" width="100" height="100"/>'
        if obj.avatar:
            return format_html(img_tag, settings.MEDIA_URL, obj.avatar)
        return format_html(img_tag, settings.STATIC_URL, default_avatar)
    get_avatar_img.allow_tags = True
    get_avatar_img.description = u'Изображение'


