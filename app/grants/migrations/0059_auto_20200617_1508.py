# Generated by Django 2.2.4 on 2020-06-17 15:08

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0122_auto_20200615_1510"),
        ("grants", "0058_auto_20200615_1226"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contribution",
            name="tx_id",
            field=models.CharField(
                blank=True,
                default="0x0",
                help_text="The transaction ID of the Contribution.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="grant_type",
            field=models.CharField(
                choices=[
                    ("tech", "tech"),
                    ("health", "health"),
                    ("Community", "media"),
                    ("change", "change"),
                    ("matic", "matic"),
                ],
                default="tech",
                help_text="Grant CLR category",
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="matchpledge",
            name="pledge_type",
            field=models.CharField(
                choices=[
                    ("tech", "tech"),
                    ("media", "media"),
                    ("health", "health"),
                    ("change", "change"),
                ],
                default="tech",
                help_text="CLR pledge type",
                max_length=15,
            ),
        ),
        migrations.CreateModel(
            name="CartActivity",
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
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("ADD_ITEM", "Add item to cart"),
                            ("REMOVE_ITEM", "Remove item to cart"),
                        ],
                        help_text="Type of activity",
                        max_length=20,
                    ),
                ),
                (
                    "metadata",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, default=dict, help_text="Related data to the action"
                    ),
                ),
                ("bulk", models.BooleanField(default=False)),
                (
                    "grant",
                    models.ForeignKey(
                        help_text="Related Grant Activity ",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_actions",
                        to="grants.Grant",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        help_text="User Cart Activity",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_activity",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
