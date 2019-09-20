# Generated by Django 2.2.4 on 2019-09-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0051_profile_gitcoin_discord_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='reserved_for_user_expiration',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bounty',
            name='reserved_for_user_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bounty',
            name='idx_status',
            field=models.CharField(choices=[('cancelled', 'cancelled'), ('done', 'done'), ('expired', 'expired'), ('reserved', 'reserved'), ('open', 'open'), ('started', 'started'), ('submitted', 'submitted'), ('unknown', 'unknown')], db_index=True, default='open', max_length=9),
        ),
    ]
