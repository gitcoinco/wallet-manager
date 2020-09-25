# Generated by Django 2.1.4 on 2018-12-26 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GitcoinBotResponses",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "request",
                    models.CharField(db_index=True, max_length=500, unique=True),
                ),
                ("response", models.CharField(max_length=500)),
            ],
        ),
    ]
