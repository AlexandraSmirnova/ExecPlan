# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-03-25 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0002_task_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='task',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='\u0434\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f'),
        ),
    ]
