# Generated by Django 2.2.4 on 2020-02-21 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("townsquare", "0010_comment_likes"),
    ]

    operations = [
        migrations.AddField(
            model_name="matchranking",
            name="contributors",
            field=models.IntegerField(default=1),
        ),
    ]
