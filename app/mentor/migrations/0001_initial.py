# Generated by Django 2.2.4 on 2020-01-12 11:42

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '0071_auto_20200112_1142'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('description', models.TextField(default='', max_length=500)),
                ('priceFinney', models.IntegerField(default=18)),
                ('network', models.CharField(db_index=True, max_length=25)),
                ('to_address', models.CharField(max_length=255)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('active', models.BooleanField(default=False)),
                ('start_datetime', models.DateTimeField(null=True)),
                ('end_datetime', models.DateTimeField(null=True)),
                ('mentee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_mentee', to='dashboard.Profile')),
                ('mentor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_mentor', to='dashboard.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
