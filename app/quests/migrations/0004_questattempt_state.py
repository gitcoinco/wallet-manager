# Generated by Django 2.2.3 on 2019-09-23 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quests", "0003_auto_20190923_0040"),
    ]

    operations = [
        migrations.AddField(
            model_name="questattempt",
            name="state",
            field=models.IntegerField(default=0),
        ),
    ]
