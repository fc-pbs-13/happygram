# Generated by Django 3.0.7 on 2020-07-14 07:00

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20200714_0353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='posts.Comment'),
        ),
    ]
