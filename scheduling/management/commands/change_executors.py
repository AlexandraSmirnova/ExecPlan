from django.core.management import BaseCommand
from django.db.models import Q

from scheduling.benchmarks.benchmark_j1201_1 import members_count, members_type
from scheduling.models import Task, ProjectMember


class Command(BaseCommand):
    available_tasks = []
    tasks_count = 0
    project_id = None

    type_flag = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    def add_arguments(self, parser):
        parser.add_argument('p_id', default=1, type=int)

    def handle(self, p_id, *args, **options):
        self.project_id = p_id

        self.available_tasks = Task.objects.filter(project=self.project_id, is_active=True)
        print [x.id for x in self.available_tasks]

        for task in self.available_tasks:
            self.change_executors(task)
            self.tasks_count += 1

    def change_executors(self, task):
        members = ProjectMember.objects.filter(project_id=self.project_id, is_active=True).exclude(user_id=1)
        members_cnt = members_count[self.tasks_count]
        member_type = members_type[self.tasks_count]

        if member_type:
            members = members.filter(role=member_type)

        task.executors.clear()

        executors = []
        while members_cnt:
            executor = members[self.type_flag[member_type]].user_id
            if executor not in executors:
                executors.append(executor)
                task.executors.add(executor)
                task.save()
                members_cnt -= 1
                self.type_flag[member_type] = (self.type_flag[member_type] + 1) % len(members)
                print task.id, executor