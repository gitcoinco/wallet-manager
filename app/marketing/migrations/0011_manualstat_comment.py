# Generated by Django 2.2.4 on 2020-03-24 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketing", "0010_auto_20200317_0356"),
    ]

    operations = [
        migrations.AddField(
            model_name="manualstat",
            name="comment",
            field=models.TextField(default="", max_length=255),
        ),
    ]
