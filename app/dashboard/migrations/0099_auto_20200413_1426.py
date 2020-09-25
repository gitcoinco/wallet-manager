# Generated by Django 2.2.4 on 2020-04-13 14:26

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0098_auto_20200413_1223"),
    ]

    operations = [
        migrations.AddField(
            model_name="hackathonevent",
            name="default_channels",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="hackathonevent",
            name="sponsor_profiles",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={"data__type": "Organization"},
                to="dashboard.Profile",
            ),
        ),
    ]
