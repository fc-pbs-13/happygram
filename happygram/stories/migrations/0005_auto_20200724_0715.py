# Generated by Django 3.0.7 on 2020-07-24 07:15

from django.db import migrations, models
import stories.models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0004_auto_20200723_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=stories.models.story_img_path),
        ),
    ]