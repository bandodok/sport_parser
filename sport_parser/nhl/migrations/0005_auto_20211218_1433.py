# Generated by Django 3.2.6 on 2021-12-18 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0004_auto_20211216_1934'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nhlmatch',
            old_name='date',
            new_name='datetime',
        ),
        migrations.RemoveField(
            model_name='nhlmatch',
            name='time',
        ),
    ]