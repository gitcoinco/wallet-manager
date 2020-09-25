# Generated by Django 2.2.4 on 2020-06-17 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grants", "0060_cartactivity_latest"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="last_update",
            field=models.DateTimeField(
                blank=True, help_text="The last grant admin update date", null=True
            ),
        ),
        migrations.AlterField(
            model_name="cartactivity",
            name="action",
            field=models.CharField(
                choices=[
                    ("ADD_ITEM", "Add item to cart"),
                    ("REMOVE_ITEM", "Remove item to cart"),
                    ("CLEAR_CART", "Clear cart"),
                ],
                help_text="Type of activity",
                max_length=20,
            ),
        ),
    ]
