# Generated by Django 2.2.4 on 2020-01-13 21:15

from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("kudos", "0011_auto_20191106_0237"),
        ("dashboard", "0071_merge_20200109_2043"),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
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
                ("title", models.TextField(blank=True, default="")),
                ("desc", models.TextField(blank=True, default="")),
                ("valid_from", models.DateTimeField(db_index=True)),
                ("valid_to", models.DateTimeField(db_index=True)),
                (
                    "style",
                    models.CharField(
                        choices=[
                            ("primary", "primary"),
                            ("secondary", "secondary"),
                            ("success", "success"),
                            ("danger", "danger"),
                            ("warning", "warning"),
                            ("info", "info"),
                            ("light", "light"),
                            ("dark", "dark"),
                            ("white", "white"),
                        ],
                        db_index=True,
                        default="announce1",
                        help_text="https://getbootstrap.com/docs/4.0/utilities/colors/",
                        max_length=50,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Offer",
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
                ("title", models.TextField(blank=True, default="")),
                ("desc", models.TextField(blank=True, default="")),
                ("url", models.URLField(db_index=True)),
                ("valid_from", models.DateTimeField(db_index=True)),
                ("valid_to", models.DateTimeField(db_index=True)),
                (
                    "key",
                    models.CharField(
                        choices=[
                            ("daily", "daily"),
                            ("weekly", "weekly"),
                            ("monthly", "monthly"),
                            ("other", "other"),
                        ],
                        db_index=True,
                        max_length=50,
                    ),
                ),
                (
                    "style",
                    models.CharField(
                        choices=[
                            ("announce1", "light-pink"),
                            ("announce2", "blue"),
                            ("announce3", "teal"),
                            ("announce4", "yellow"),
                            ("announce5", "lime-green"),
                            ("announce6", "pink"),
                        ],
                        db_index=True,
                        default="announce1",
                        max_length=50,
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=True, help_text="Is this available publicly yet?"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offers_created",
                        to="dashboard.Profile",
                    ),
                ),
                (
                    "persona",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="offers",
                        to="kudos.Token",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OfferAction",
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
                ("what", models.CharField(db_index=True, max_length=50)),
                (
                    "offer",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to="townsquare.Offer",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offeractions",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Like",
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
                    "activity",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="dashboard.Activity",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Flag",
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
                    "activity",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flags",
                        to="dashboard.Activity",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flags",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Comment",
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
                ("comment", models.TextField(blank=True, default="")),
                (
                    "activity",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="dashboard.Activity",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="dashboard.Profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
