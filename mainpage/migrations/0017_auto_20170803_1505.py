# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-03 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0016_auto_20170803_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project',
            name='projectId',
            field=models.CharField(max_length=1000),
        ),
    ]
