# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0007_auto_20170727_0804'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='runnerExist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='projects',
            name='runnerName',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
