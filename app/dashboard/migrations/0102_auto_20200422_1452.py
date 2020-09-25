# Generated by Django 2.2.4 on 2020-04-22 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0101_auto_20200420_1427"),
    ]

    operations = [
        migrations.AddField(
            model_name="earning",
            name="token_name",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="earning",
            name="token_value",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50),
        ),
        migrations.AddField(
            model_name="earning",
            name="txid",
            field=models.CharField(default="", max_length=255),
        ),
    ]
