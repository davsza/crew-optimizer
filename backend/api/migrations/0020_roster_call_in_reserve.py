# Generated by Django 5.0.4 on 2024-11-09 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_roster_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='call_in_reserve',
            field=models.CharField(default=0, max_length=21),
            preserve_default=False,
        ),
    ]
