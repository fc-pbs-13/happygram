# Generated by Django 3.0.7 on 2020-07-23 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relations', '0002_auto_20200717_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relation',
            name='related_type',
            field=models.CharField(choices=[('FOLLOW', 'Follow'), ('BLOCK', 'Block')], max_length=10),
        ),
    ]
