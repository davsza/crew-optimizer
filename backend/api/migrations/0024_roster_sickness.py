# Generated by Django 5.0.4 on 2024-11-09 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_remove_roster_call_in_reserve_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='sickness',
            field=models.CharField(default=0, max_length=7),
            preserve_default=False,
        ),
    ]
