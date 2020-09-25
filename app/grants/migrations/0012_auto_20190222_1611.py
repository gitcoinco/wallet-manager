# Generated by Django 2.1.2 on 2019-02-22 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0011_auto_20190221_2050"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grant",
            name="clr_matching",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="The CLR matching amount",
                max_digits=20,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="contributor_signature",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The contributor's signature.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="subscription_hash",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The contributor's Subscription hash.",
                max_length=255,
            ),
        ),
    ]
