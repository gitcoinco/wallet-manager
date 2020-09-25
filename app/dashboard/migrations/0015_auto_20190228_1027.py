# Generated by Django 2.1.7 on 2019-02-28 10:27

from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0014_merge_20190221_2246"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackEntry",
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
                ("rating", models.SmallIntegerField(blank=True, default=0)),
                ("comment", models.TextField(blank=True, default="")),
                (
                    "feedbackType",
                    models.TextField(blank=True, default="", max_length=20),
                ),
                (
                    "bounty",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks",
                        to="dashboard.Bounty",
                    ),
                ),
                (
                    "receiver_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks_got",
                        to="dashboard.Profile",
                    ),
                ),
                (
                    "sender_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks_sent",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
