# Generated by Django 2.1.5 on 2019-02-04 18:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('list', '0013_job_date_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='date_completed',
        ),
        migrations.AddField(
            model_name='job',
            name='datetime_completed',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
