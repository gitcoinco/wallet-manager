# Generated by Django 2.2.3 on 2019-10-01 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0031_grant_weighted_shuffle"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="contribution_count",
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name="grant",
            name="contributor_count",
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]
