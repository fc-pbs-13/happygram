# Generated by Django 3.0.7 on 2020-07-14 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200714_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='relations_users',
        ),
        migrations.DeleteModel(
            name='Relations',
        ),
    ]
