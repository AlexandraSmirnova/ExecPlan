# coding=utf-8
from __future__ import unicode_literals
from django.core.management import BaseCommand
from core.models import User
from scheduling.models import ProjectMember
from utils.string_utils import get_random_string


class Command(BaseCommand):
    available_tasks = None
    users_count = 0

    def add_arguments(self, parser):
        parser.add_argument('cnt', default=10, type=int)
        parser.add_argument('p_id', default=0, type=int)

    def handle(self, cnt, p_id, *args, **options):
        users_count = cnt
        project_id = p_id

        for i in range(users_count):
            user = User.objects.create_user(email='{0}@{1}.com'.format(get_random_string(7), get_random_string(5)),
                                            password=get_random_string(8),
                                            first_name='{0}{1}'.format(get_random_string(1, False).upper(),
                                                                       get_random_string(5, False).lower()),
                                            last_name='{0}{1}'.format(get_random_string(1, False).upper(),
                                                                      get_random_string(7, False).lower()),
                                            is_active=True)
            if project_id:
                ProjectMember.objects.create(project_id=project_id, user=user, is_active=True)
