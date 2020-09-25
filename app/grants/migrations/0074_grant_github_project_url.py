# Generated by Django 2.2.4 on 2020-09-01 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0073_remove_grant_clr_matching"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="github_project_url",
            field=models.URLField(blank=True, help_text="Grant Github Project URL"),
        ),
    ]
