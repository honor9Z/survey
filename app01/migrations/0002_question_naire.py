# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-07 03:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='naire',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app01.Questionnaire'),
        ),
    ]
