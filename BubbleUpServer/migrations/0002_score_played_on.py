# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 21:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('BubbleUpServer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='played_on',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 25, 21, 2, 11, 704876, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
