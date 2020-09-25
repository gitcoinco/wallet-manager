# Generated by Django 2.2.4 on 2020-04-14 11:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0052_merge_20200413_2142"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="backup_clr_prediction_curve",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.FloatField(), size=2
                ),
                blank=True,
                default=list,
                help_text="backup 5 point curve to predict CLR donations - used to store a secondary backup of the clr prediction curve, in the case a new identity mechanism is used",
                size=None,
            ),
        ),
    ]
