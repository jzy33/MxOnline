# Generated by Django 2.2 on 2019-12-09 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_auto_20191207_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='is_banner',
            field=models.BooleanField(default=False, verbose_name='是否广告位'),
        ),
    ]
