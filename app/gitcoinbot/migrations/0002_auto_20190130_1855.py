# Generated by Django 2.1.2 on 2019-01-30 18:55

from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ("gitcoinbot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="gitcoinbotresponses",
            name="created_on",
            field=models.DateTimeField(db_index=True, default=economy.models.get_time),
        ),
        migrations.AddField(
            model_name="gitcoinbotresponses",
            name="modified_on",
            field=models.DateTimeField(default=economy.models.get_time),
        ),
    ]
