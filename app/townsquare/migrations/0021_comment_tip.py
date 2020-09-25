# Generated by Django 2.2.4 on 2020-05-26 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0114_auto_20200522_0730"),
        ("townsquare", "0020_auto_20200521_1020"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="tip",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="awards",
                to="dashboard.Tip",
            ),
        ),
    ]
