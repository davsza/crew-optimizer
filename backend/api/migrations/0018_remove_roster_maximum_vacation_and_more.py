# Generated by Django 5.0.4 on 2024-10-06 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_roster_maximum_vacation_roster_taken_vacation_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roster',
            name='maximum_vacation',
        ),
        migrations.RemoveField(
            model_name='roster',
            name='taken_vacation',
        ),
    ]
