# Generated by Django 5.0.4 on 2024-06-24 15:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_shift_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='reserve_last_modified',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='reserve_shift',
            field=models.CharField(default=0, max_length=3),
            preserve_default=False,
        ),
    ]