# Generated by Django 2.2.4 on 2020-07-27 15:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0130_auto_20200727_0628"),
    ]

    operations = [
        migrations.AddField(
            model_name="hackathonevent",
            name="display_showcase",
            field=models.BooleanField(default=False),
        ),
    ]
