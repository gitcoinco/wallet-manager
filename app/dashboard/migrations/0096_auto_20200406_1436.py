# Generated by Django 2.2.4 on 2020-04-06 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0096_auto_20200401_2038"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bountyfulfillment",
            name="payout_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("expired", "expired"),
                    ("pending", "pending"),
                    ("done", "done"),
                ],
                max_length=10,
            ),
        ),
    ]
