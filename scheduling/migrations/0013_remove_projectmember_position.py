# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-04-30 10:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0012_projectmember_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectmember',
            name='position',
        ),
    ]
