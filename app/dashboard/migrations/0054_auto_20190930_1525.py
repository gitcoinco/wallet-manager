# Generated by Django 2.2.4 on 2019-09-30 15:25

from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
        ("dashboard", "0053_auto_20190920_1816"),
    ]

    operations = [
        migrations.CreateModel(
            name="Repo",
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
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Organization",
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
                ("name", models.CharField(max_length=255)),
                ("groups", models.ManyToManyField(blank=True, to="auth.Group")),
                ("repos", models.ManyToManyField(blank=True, to="dashboard.Repo")),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="profile",
            name="profile_organizations",
            field=models.ManyToManyField(blank=True, to="dashboard.Organization"),
        ),
        migrations.AddField(
            model_name="profile",
            name="repos",
            field=models.ManyToManyField(blank=True, to="dashboard.Repo"),
        ),
    ]
