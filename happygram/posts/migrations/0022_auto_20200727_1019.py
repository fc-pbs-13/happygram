# Generated by Django 3.0.7 on 2020-07-27 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20200724_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='caption',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
