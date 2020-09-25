# Generated by Django 2.1.2 on 2019-01-25 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0006_grant_request_ownership_change"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="image_css",
            field=models.CharField(
                default="",
                help_text="additional CSS to attach to the grant-banner img.",
                max_length=255,
            ),
        ),
    ]
