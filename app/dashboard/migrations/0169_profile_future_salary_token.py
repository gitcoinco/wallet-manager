# Generated by Django 2.2.4 on 2021-01-20 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0168_auto_20201216_2058'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='future_salary_token',
            field=models.BigIntegerField(null=True),
        ),
    ]
