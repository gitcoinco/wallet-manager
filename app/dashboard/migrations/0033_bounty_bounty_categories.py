# Generated by Django 2.1.7 on 2019-06-12 18:40

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0032_auto_20190601_1103"),
    ]

    operations = [
        migrations.AddField(
            model_name="bounty",
            name="bounty_categories",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("frontend", "frontend"),
                        ("backend", "backend"),
                        ("design", "design"),
                        ("documentation", "documentation"),
                        ("other", "other"),
                    ],
                    max_length=50,
                ),
                default=list,
                size=None,
            ),
        ),
    ]
