# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BubbleUpServer', '0002_score_played_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredclient',
            name='country',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]