# Generated by Django 2.2.1 on 2019-05-15 17:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('list', '0015_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='active',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]