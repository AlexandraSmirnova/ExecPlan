# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-04-25 20:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0010_task_executors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_executor', to=settings.AUTH_USER_MODEL, verbose_name='\u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c'),
        ),
    ]
