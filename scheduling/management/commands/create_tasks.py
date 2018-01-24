# coding=utf-8
from __future__ import unicode_literals
import random

from datetime import timedelta
from django.core.management import BaseCommand

from scheduling.models import ProjectMember, Predecessor, Task, Project
from utils.string_utils import get_random_string


class Command(BaseCommand):
    available_tasks = None
    tasks_count = 0

    def add_arguments(self, parser):
        parser.add_argument('p_id', default=1, type=int)
        parser.add_argument('cnt', default=10, type=int)

    def handle(self, *args, **options):
        project_id = options['p_id']
        tasks_count = options['cnt']

        print project_id
        print tasks_count
        self.available_tasks = Task.objects.filter(project=project_id, is_active=True)
        self.tasks_count = len(self.available_tasks)

        for i in range(tasks_count):
            name = self.get_random_name()
            duration = self.get_duration()
            member_id = self.get_member(project_id)
            soft_deadline, hard_deadline = self.get_deadlines(project_id, duration)

            task = Task.objects.create(
                name=name,
                project_id=project_id,
                duration=duration,
                executor_id=member_id,
                author_id=member_id,
                soft_deadline=soft_deadline,
                hard_deadline=hard_deadline
            )

            self.create_predecessors(task)
            print 'Created task: {}, duration - {}, executor - {}'.format(name, duration, member_id)
            self.tasks_count += 1

    def get_duration(self):
        return random.randint(1, 40)

    def get_random_name(self):
        names = [
            'Задача на проектирование',
            'Задача на разработку',
            'Задача на тестирование',
            'Задача на исправление ошибок после тестирования',
            'Задача на публикацию новой версии',
            'Задача на документирование'
        ]

        return '{} - {}'.format(names[random.randint(0, len(names) - 1)], get_random_string(5))

    def get_member(self, project_id):
        members = ProjectMember.objects.filter(project_id=project_id, is_active=True)

        if members:
            return members[random.randint(0, len(members) - 1)].user_id

        return None

    def create_predecessors(self, task):
        if not self.available_tasks:
            return
        Predecessor.objects.create(task=task, predecessor=self.available_tasks[59])

        has_preds = random.choice([True, False])
        if not has_preds:
            return

        pred_count = random.randint(0, 3)

        for i in range(pred_count):
            Predecessor.objects.create(task=task, predecessor=random.choice(self.available_tasks))


        return

    def get_deadlines(self, project_id, duration):
        with_constrains = random.choice([True, False])

        if not with_constrains:
            return None, None

        constraint_types = {
            'only_soft_deadline': 0,
            'only_hard_deadline': 1,
            'both_deadlines': 2
        }

        project = Project.objects.filter(id=project_id).first()
        type = random.randint(0, 2)
        addition_days = random.randint(self.tasks_count + int(duration / 9), self.tasks_count + 100)

        if type == constraint_types['only_soft_deadline']:
            return project.start_date + timedelta(days=addition_days), None

        if type == constraint_types['only_hard_deadline']:
            return None, project.start_date + timedelta(days=addition_days)

        if type == constraint_types['both_deadlines']:
            soft_deadline = project.start_date + timedelta(days=addition_days)
            days_to_hard = random.randint(1, 100)
            return soft_deadline, soft_deadline + timedelta(days=days_to_hard)
