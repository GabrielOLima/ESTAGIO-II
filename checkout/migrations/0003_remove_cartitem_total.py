# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-10-16 01:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_remove_orderitem_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='total',
        ),
    ]