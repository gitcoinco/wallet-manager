# Generated by Django 2.1.7 on 2019-05-24 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_bounty_bounty_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='persona_is_funder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='persona_is_hunter',
            field=models.BooleanField(default=False),
        ),
    ]