# Generated by Django 2.2.4 on 2020-03-08 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0090_auto_20200308_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='html_url',
            field=models.URLField(blank=True),
        ),
    ]
