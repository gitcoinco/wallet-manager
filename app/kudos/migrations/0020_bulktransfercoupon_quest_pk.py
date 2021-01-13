# Generated by Django 2.2.4 on 2021-01-13 03:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0030_quest_force_visible'),
        ('kudos', '0019_tokenrequest_gas_price_overide'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulktransfercoupon',
            name='quest_pk',
            field=models.ForeignKey(blank=True, help_text='ForeignKey linking the btc to a Quest (to allow the same Kudos to be rewarded from multiple Quests)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_transfers', to='quests.Quest'),
        ),
    ]
