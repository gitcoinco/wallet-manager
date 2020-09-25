# Generated by Django 2.2.4 on 2019-10-16 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0056_auto_20191007_2254"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profileview",
            options={"ordering": ["-pk"]},
        ),
        migrations.AlterField(
            model_name="profile",
            name="referrer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referred",
                to="dashboard.Profile",
            ),
        ),
    ]
