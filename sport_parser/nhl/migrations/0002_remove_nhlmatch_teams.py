# Generated by Django 3.2.13 on 2022-06-16 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nhlmatch',
            name='teams',
        ),
    ]
