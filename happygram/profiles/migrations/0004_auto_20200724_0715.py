# Generated by Django 3.0.7 on 2020-07-24 07:15

from django.db import migrations, models
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20200710_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=profiles.models.profile_img_path),
        ),
    ]
