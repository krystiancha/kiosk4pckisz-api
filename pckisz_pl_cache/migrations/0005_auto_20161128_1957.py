# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-28 18:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pckisz_pl_cache', '0004_auto_20161128_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screening',
            name='meeting',
            field=models.BooleanField(default=False, verbose_name='meeting'),
        ),
    ]
