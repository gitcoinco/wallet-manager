# Generated by Django 2.1.7 on 2019-04-24 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kudos", "0003_auto_20190423_2056"),
    ]

    operations = [
        migrations.AddField(
            model_name="token",
            name="preview_img_mode",
            field=models.CharField(default="png", max_length=255),
        ),
    ]
