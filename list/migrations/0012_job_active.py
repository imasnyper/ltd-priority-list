# Generated by Django 2.1.5 on 2019-02-04 15:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('list', '0011_auto_20190114_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='active',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
