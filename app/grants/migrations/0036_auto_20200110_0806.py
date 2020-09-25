# Generated by Django 2.2.4 on 2020-01-10 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0035_auto_20191214_0736"),
    ]

    operations = [
        migrations.AddField(
            model_name="contribution",
            name="split_tx_confirmed",
            field=models.BooleanField(
                default=False, help_text="Whether or not the split tx succeeded."
            ),
        ),
        migrations.AddField(
            model_name="contribution",
            name="split_tx_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The tx id of the split transfer",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="contribution",
            name="tx_override",
            field=models.BooleanField(
                default=False,
                help_text="Whether or not the tx success and tx_cleared have been manually overridden. If this setting is True, update_tx_status will not change this object.",
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="split_tx_confirmed",
            field=models.BooleanField(
                default=False, help_text="Whether or not the split tx succeeded."
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="split_tx_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The tx id of the split transfer",
                max_length=255,
            ),
        ),
    ]
