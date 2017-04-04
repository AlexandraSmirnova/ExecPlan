# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from core.models import DefaultModel, User


class Project(DefaultModel):
    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    name = models.CharField(verbose_name='название', max_length=255)
    author = models.ForeignKey(User, verbose_name='автор')

    def __unicode__(self):
        return self.name


class ProjectMember(DefaultModel):
    class Meta:
        verbose_name = 'участник проекта'
        verbose_name_plural = 'участники проектов'

    user = models.ForeignKey(User, verbose_name='пользователь')
    project = models.ForeignKey(Project, verbose_name='проект')
    position = models.CharField(verbose_name='должность', max_length=128)
    is_project_admin = models.BooleanField(verbose_name='администратор проекта?', default=False)

    def __unicode__(self):
        return '{0} (проект {1})'.format(self.user, self.project)


class TaskManager(models.Manager):
    def get_project_tasks(self, project_id):
        return self.filter(project_id=project_id, is_active=True)


class Task(DefaultModel):
    class Meta:
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'

    name = models.CharField(verbose_name='название', max_length=255)
    description = models.TextField(verbose_name='описание', blank=True, null=True)
    author = models.ForeignKey(User, verbose_name='автор', related_name='task_author')
    project = models.ForeignKey(Project, verbose_name='проект', related_name='task_project')
    executor = models.ForeignKey(User, verbose_name='исполнитель', related_name='task_executor')

    start_date = models.DateField(verbose_name='дата начала', default=timezone.now)
    end_date = models.DateField(verbose_name='дата окончания', default=timezone.now)
    duration = models.FloatField(verbose_name='длительность', help_text='в часах')

    # predecessors = models.OneToManyField('self', verbose_name='предшественники', blank=True)

    objects = TaskManager()

    def __unicode__(self):
        return self.name

    def as_dict(self):
        return {
            'id': self.id,
            'executor_id': self.executor.id,
            'duration': self.duration,
            'start_time': None,
            'end_time': None,
            'predecessors': list(Predecessor.objects.filter(task=self).values_list('predecessor_id', flat=True))
        }


class Predecessor(models.Model):
    class Meta:
        verbose_name = 'предшественник'
        verbose_name_plural = 'предшественники'

    task = models.ForeignKey(Task, verbose_name='основной таск')
    predecessor = models.ForeignKey(Task, verbose_name='предшественник', related_name='predecessor_task')
