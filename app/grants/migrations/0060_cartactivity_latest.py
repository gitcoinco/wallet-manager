# Generated by Django 2.2.4 on 2020-06-17 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0059_auto_20200617_1508"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartactivity",
            name="latest",
            field=models.BooleanField(default=False),
        ),
    ]
