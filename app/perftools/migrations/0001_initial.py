# Generated by Django 2.1.4 on 2018-12-26 17:16

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JSONStore",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=economy.models.get_time
                    ),
                ),
                ("modified_on", models.DateTimeField(default=economy.models.get_time)),
                (
                    "view",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=255
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=255
                    ),
                ),
                (
                    "data",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, default=dict
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
