# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 23:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BubbleUpServer', '0004_registeredclient_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredclient',
            name='phrase',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]
