# Generated by Django 2.2.4 on 2021-04-25 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quadraticlands', '0003_qlvote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qlvote',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vote_profile', to='dashboard.Profile'),
        ),
    ]
