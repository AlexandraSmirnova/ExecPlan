# coding=utf-8
from import_export import resources

from core.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        import_id_fields = ('email',)
        fields = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login']

    def get_export_order(self):
        return ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login']

    def get_export_headers(self):
        return [u'Email', u'Имя', u'Фамилия', u'Активен?', u'Персонал?', u'Дата регистрации', u'Последний вход']