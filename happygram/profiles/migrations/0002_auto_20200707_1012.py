# Generated by Django 3.0.7 on 2020-07-07 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='introduce',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
