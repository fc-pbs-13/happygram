# Generated by Django 3.0.7 on 2020-08-04 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20200724_0715'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follower',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
