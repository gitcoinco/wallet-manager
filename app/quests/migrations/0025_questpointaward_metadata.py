# Generated by Django 2.2.4 on 2020-03-06 20:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0024_auto_20191204_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='questpointaward',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
