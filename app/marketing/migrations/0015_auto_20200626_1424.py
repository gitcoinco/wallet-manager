# Generated by Django 2.2.4 on 2020-06-26 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketing", "0014_upcomingdate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roundupemail",
            name="body",
            field=models.TextField(blank=True, max_length=15000),
        ),
    ]
