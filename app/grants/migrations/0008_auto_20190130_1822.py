# Generated by Django 2.1.2 on 2019-01-30 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0007_grant_image_css"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grant",
            name="image_css",
            field=models.CharField(
                blank=True,
                default="",
                help_text="additional CSS to attach to the grant-banner img.",
                max_length=255,
            ),
        ),
    ]
