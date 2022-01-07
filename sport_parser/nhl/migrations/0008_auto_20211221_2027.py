# Generated by Django 3.2.6 on 2021-12-21 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0007_nhlmatch_postponed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nhlmatch',
            name='finished',
        ),
        migrations.RemoveField(
            model_name='nhlmatch',
            name='postponed',
        ),
        migrations.AddField(
            model_name='nhlmatch',
            name='status',
            field=models.CharField(choices=[('scheduled', 'scheduled'), ('finished', 'finished'), ('postponed', 'postponed')], default='scheduled', max_length=9),
        ),
    ]