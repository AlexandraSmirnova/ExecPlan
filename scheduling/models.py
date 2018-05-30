# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from core.models import DefaultModel, User


class Project(DefaultModel):
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    name = models.CharField(verbose_name='название', max_length=255)
    author = models.ForeignKey(User, verbose_name='автор')
    start_date = models.DateTimeField(verbose_name='дата начала', default=timezone.now)

    def __unicode__(self):
        return self.name


class ProjectMemberManager(models.Manager):
    def get_user_projects_ids(self, user):
        return self.filter(user=user, is_active=True).values_list('project', flat=True)

    def check_membership(self, user, project):
        return self.filter(user=user, project=project, is_active=True).first()


class ProjectMember(DefaultModel):
    TESTER = 1
    DEVELOPER = 2
    DESIGNER = 3
    MANAGER = 4

    ROLE_CHOICES = (
        (TESTER, 'Tester'),
        (DEVELOPER, 'Developer'),
        (DESIGNER, 'Designer'),
        (MANAGER, 'Manager')
    )

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'

    user = models.ForeignKey(User, verbose_name='пользователь')
    project = models.ForeignKey(Project, verbose_name='проект')
    role = models.IntegerField(verbose_name='роль', choices=ROLE_CHOICES, default=DEVELOPER)
    is_project_admin = models.BooleanField(verbose_name='администратор проекта?', default=False)

    objects = ProjectMemberManager()

    def __unicode__(self):
        return '{0} (проект {1})'.format(self.user, self.project)


class TaskManager(models.Manager):
    def get_project_tasks(self, project_id):
        return self.filter(project_id=project_id, is_active=True)


class Task(DefaultModel):
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    name = models.CharField(verbose_name='название', max_length=255)
    description = models.TextField(verbose_name='описание', blank=True, null=True)
    author = models.ForeignKey(User, verbose_name='автор', related_name='task_author')
    project = models.ForeignKey(Project, verbose_name='проект', related_name='task_project')
    executor = models.ForeignKey(User, verbose_name='исполнитель', related_name='task_executor', blank=True, null=True)
    executors = models.ManyToManyField(User, verbose_name='исполнители')

    start_date = models.DateTimeField(verbose_name='дата начала', default=timezone.now)
    end_date = models.DateTimeField(verbose_name='дата окончания', default=timezone.now)
    soft_deadline = models.DateTimeField(verbose_name='крайний срок (мягкий)', blank=True, null=True)
    hard_deadline = models.DateTimeField(verbose_name='крайний срок (жесткий)', blank=True, null=True)
    duration = models.FloatField(verbose_name='длительность', help_text='в часах')

    objects = TaskManager()

    def __unicode__(self):
        return self.name

    def as_dict(self):
        dic = {
            'id': self.id,
            # 'executor_id': self.executor.id,
            'executors_ids': [x.id for x in self.executors.all()],
            'duration': self.duration,
            'start_time': None,
            'end_time': None,
            's_deadline_time': (self.soft_deadline - self.project.start_date).days * 9 if self.soft_deadline else 0,
            'h_deadline_time': (self.hard_deadline - self.project.start_date).days * 9 if self.hard_deadline else 0,
            'predecessors': list(Predecessor.objects.filter(task=self).values_list('predecessor_id', flat=True)),
            'role': ProjectMember.objects.filter(user=self.executors.first()).first().role
        }
        members = ProjectMember.objects.filter(project_id=self.project_id, is_active=True, role=dic['role']).exclude(user_id=1)
        dic['demanded_count'] = len(dic['executors_ids'])
        dic['limit'] = len(members)
        return dic


class Predecessor(models.Model):
    class Meta:
        verbose_name = 'Предшественник'
        verbose_name_plural = 'Предшественники'

    task = models.ForeignKey(Task, verbose_name='основной таск')
    predecessor = models.ForeignKey(Task, verbose_name='предшественник', related_name='predecessor_task')
