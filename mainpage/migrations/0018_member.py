# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0017_auto_20170803_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('jobTitle', models.CharField(max_length=150)),
                ('jobDescription', models.CharField(max_length=1000)),
                ('avatar_uri', models.CharField(max_length=200)),
            ],
        ),
    ]
