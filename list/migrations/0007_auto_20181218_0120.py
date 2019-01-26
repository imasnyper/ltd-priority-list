# Generated by Django 2.1.4 on 2018-12-18 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0006_auto_20181218_0037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='machine',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='machine',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False, verbose_name='order'),
            preserve_default=False,
        ),
    ]
