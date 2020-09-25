# Generated by Django 2.2.4 on 2020-03-06 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0084_auto_20200226_0332"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="hackathonevent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activities",
                to="dashboard.HackathonEvent",
            ),
        ),
    ]
