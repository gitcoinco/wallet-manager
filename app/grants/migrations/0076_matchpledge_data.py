# Generated by Django 2.2.4 on 2020-09-04 17:54

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0075_remove_matchpledge_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="matchpledge",
            name="data",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
