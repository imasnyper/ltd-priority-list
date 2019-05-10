# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='color_event',
            field=models.CharField(verbose_name='Color event', blank=True, max_length=10, null=True),
        ),
    ]
