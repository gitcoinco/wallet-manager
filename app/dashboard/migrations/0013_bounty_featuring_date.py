# Generated by Django 2.1.5 on 2019-02-12 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0012_auto_20190209_1216"),
    ]

    operations = [
        migrations.AddField(
            model_name="bounty",
            name="featuring_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
