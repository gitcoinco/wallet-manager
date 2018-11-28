# Generated by Django 2.1.2 on 2018-11-24 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0115_merge_20181124_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='tip',
            name='receive_tx_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tip',
            name='tx_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tip',
            name='receive_tx_status',
            field=models.CharField(choices=[('na', 'na'), ('pending', 'pending'), ('success', 'success'), ('error', 'error'), ('unknown', 'unknown'), ('dropped', 'dropped')], db_index=True, default='na', max_length=9),
        ),
        migrations.AlterField(
            model_name='tip',
            name='tx_status',
            field=models.CharField(choices=[('na', 'na'), ('pending', 'pending'), ('success', 'success'), ('error', 'error'), ('unknown', 'unknown'), ('dropped', 'dropped')], db_index=True, default='na', max_length=9),
        ),
    ]
