# Generated by Django 2.2.4 on 2020-01-09 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0069_profile_hide_wallet_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="view_count",
            field=models.IntegerField(default=0),
        ),
    ]
