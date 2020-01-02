# Generated by Django 2.1.4 on 2018-12-11 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("list", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(name="job", options={"ordering": ("order",)},),
        migrations.AddField(
            model_name="job",
            name="order",
            field=models.PositiveIntegerField(
                db_index=True, default=1, editable=False, verbose_name="order"
            ),
            preserve_default=False,
        ),
    ]
