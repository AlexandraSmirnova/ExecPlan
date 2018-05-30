# coding=utf-8
from __future__ import unicode_literals
import random
from datetime import timedelta
from django.core.management import BaseCommand
from scheduling.benchmarks.benchmark_100_10 import durations, members_count, members_type, successors
from scheduling.models import ProjectMember, Predecessor, Task, Project
from utils.string_utils import get_random_string


class Command(BaseCommand):
    available_tasks = []
    tasks_count = 0
    project_id = None

    def add_arguments(self, parser):
        parser.add_argument('p_id', default=1, type=int)
        parser.add_argument('cnt', default=10, type=int)

    def handle(self, p_id, cnt, *args, **options):
        self.project_id = p_id
        tasks_count = cnt

        print self.project_id
        print tasks_count
        self.available_tasks = Task.objects.filter(project=self.project_id, is_active=True)
        self.tasks_count = len(self.available_tasks)

        for i in range(tasks_count):
            name = self.get_random_name()
            duration = self.get_duration()
            member_id = self.get_member()
            soft_deadline, hard_deadline = self.get_deadlines(duration)

            task = Task.objects.create(
                        name=name,
                        project_id=self.project_id,
                        duration=duration,
                        author_id=member_id,
                        soft_deadline=soft_deadline,
                        hard_deadline=hard_deadline,
                    )
            self.create_executors(task)
            self.tasks_count += 1

            print 'Created task: {}, duration - {}, executor - {}'.format(name, duration, member_id)
        self.available_tasks = Task.objects.filter(project=self.project_id, is_active=True)
        self.create_predecessors()

    def get_duration(self):
        return durations[self.tasks_count]

    @staticmethod
    def get_random_name():
        names = [
            'Задача на проектирование',
            'Задача на разработку',
            'Задача на тестирование',
            'Задача на исправление ошибок после тестирования',
            'Задача на публикацию новой версии',
            'Задача на документирование'
        ]

        return '{} - {}'.format(names[random.randint(0, len(names) - 1)], get_random_string(5))

    def get_member(self):
        members = ProjectMember.objects.filter(project_id=self.project_id, is_active=True)

        if members:
            return members[random.randint(0, len(members) - 1)].user_id

        return None

    def create_executors(self, task):
        members = ProjectMember.objects.filter(project_id=self.project_id, is_active=True).exclude(user_id=1)
        members_cnt = members_count[self.tasks_count]
        member_type = members_type[self.tasks_count]
        if member_type:
            print 'type {}'.format(members_type)
            members = members.filter(role=member_type)

        executors = []
        while members_cnt:
            executor = members[random.randint(0, len(members) - 1)].user_id
            if executor not in executors:
                executors.append(executor)
                task.executors.add(executor)
                task.save()
                members_cnt -= 1

    def create_random_predecessors(self, task):
        if not self.available_tasks:
            return
        Predecessor.objects.create(task=task, predecessor=self.available_tasks[59])

        has_preds = random.choice([True, False])
        if not has_preds:
            return

        pred_count = random.randint(0, 3)

        for i in range(pred_count):
            Predecessor.objects.create(task=task, predecessor=random.choice(self.available_tasks))

    def create_predecessors(self):
        if not self.available_tasks:
            return

        for i in range(len(self.available_tasks)):
            task = self.available_tasks[i]
            succ = successors[i]

            for s in succ:
                Predecessor.objects.create(task=self.available_tasks[s-2], predecessor=task)

    def get_deadlines(self, duration):
        with_constrains = random.choice([True, False])

        if not with_constrains:
            return None, None

        constraint_types = {
            'only_soft_deadline': 0,
            'only_hard_deadline': 1,
            'both_deadlines': 2
        }

        project = Project.objects.filter(id=self.project_id).first()
        d_type = random.randint(0, 2)
        addition_days = random.randint(self.tasks_count + int(duration / 9), self.tasks_count + 100)

        if d_type == constraint_types['only_soft_deadline']:
            return project.start_date + timedelta(days=addition_days), None

        if d_type == constraint_types['only_hard_deadline']:
            return None, project.start_date + timedelta(days=addition_days)

        if d_type == constraint_types['both_deadlines']:
            soft_deadline = project.start_date + timedelta(days=addition_days)
            days_to_hard = random.randint(1, 100)
            return soft_deadline, soft_deadline + timedelta(days=days_to_hard)
