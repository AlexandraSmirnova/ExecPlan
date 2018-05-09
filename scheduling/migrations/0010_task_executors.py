# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-04-16 19:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0009_auto_20171105_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='executors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='\u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u0438'),
        ),
    ]