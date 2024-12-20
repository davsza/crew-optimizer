# Generated by Django 5.0.4 on 2024-11-15 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_roster_sickness'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='day_off_call_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='roster',
            name='day_off_call_in_days',
            field=models.CharField(default=0, max_length=7),
            preserve_default=False,
        ),
    ]
