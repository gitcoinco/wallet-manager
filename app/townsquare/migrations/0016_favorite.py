# Generated by Django 2.2.4 on 2020-03-09 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dashboard", "0095_hackathonevent_visible"),
        ("townsquare", "0015_offer_comments_admin"),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorite",
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
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=economy.models.get_time
                    ),
                ),
                ("modified_on", models.DateTimeField(default=economy.models.get_time)),
                ("created", models.DateTimeField(auto_now=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.Activity",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
