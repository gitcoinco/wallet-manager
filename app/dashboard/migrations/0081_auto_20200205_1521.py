# Generated by Django 2.2.4 on 2020-02-05 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0080_merge_20200205_1511"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="automatic_backup",
            field=models.BooleanField(
                default=False,
                help_text="automatic backup profile to cloud storage such as 3Box if the flag is true",
            ),
        ),
    ]
