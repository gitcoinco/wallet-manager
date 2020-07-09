# Generated by Django 2.2.4 on 2020-06-15 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0121_merge_20200615_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileverification',
            name='success',
            field=models.BooleanField(default=False, help_text='Was a successful transaction verification?'),
        ),
        migrations.AddField(
            model_name='profileverification',
            name='validation_comment',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profileverification',
            name='validation_passed',
            field=models.BooleanField(default=False, help_text='Did the initial validation pass?'),
        ),
    ]
