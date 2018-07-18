# Generated by Django 2.0.7 on 2018-07-18 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0095_auto_20180715_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='needs_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interest',
            name='status',
            field=models.CharField(choices=[('review', 'Needs Review'), ('warned', 'Hunter Warned'), ('okay', 'Okay'), ('snoozed', 'Snoozed'), ('pending', 'Pending')], default='okay', help_text='Whether or not the interest requires review', max_length=7, verbose_name='Needs Review'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='activity_type',
            field=models.CharField(blank=True, choices=[('new_bounty', 'New Bounty'), ('start_work', 'Work Started'), ('stop_work', 'Work Stopped'), ('work_submitted', 'Work Submitted'), ('work_done', 'Work Done'), ('worker_approved', 'Worker Approved'), ('worker_rejected', 'Worker Rejected'), ('worker_applied', 'Worker Applied'), ('increased_bounty', 'Increased Funding'), ('killed_bounty', 'Canceled Bounty'), ('new_tip', 'New Tip'), ('receive_tip', 'Tip Received'), ('bounty_abandonment_escalation_to_mods', 'Escalated for Abandonment of Bounty'), ('bounty_abandonment_warning', 'Warning for Abandonment of Bounty'), ('bounty_removed_slashed_by_staff', 'Dinged and Removed from Bounty by Staff'), ('bounty_removed_by_staff', 'Removed from Bounty by Staff'), ('bounty_removed_by_funder', 'Removed from Bounty by Funder')], max_length=50),
        ),
        migrations.AlterField(
            model_name='interest',
            name='acceptance_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date Accepted'),
        ),
        migrations.AlterField(
            model_name='interest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='interest',
            name='issue_message',
            field=models.TextField(blank=True, default='', verbose_name='Issue Comment'),
        ),
        migrations.AlterField(
            model_name='interest',
            name='pending',
            field=models.BooleanField(default=False, help_text='If this option is chosen, this interest is pending and not yet active', verbose_name='Pending'),
        ),
    ]
