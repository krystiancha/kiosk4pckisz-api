# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-20 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pckisz_pl_cache', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='screening',
            name='meeting',
            field=models.BooleanField(default=False, verbose_name='spotkanie z reżyserem'),
        ),
    ]
