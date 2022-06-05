# Generated by Django 3.2.13 on 2022-06-05 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nhlmatch',
            name='guest_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guest_matches', to='nhl.nhlteam'),
        ),
        migrations.AlterField(
            model_name='nhlmatch',
            name='home_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_matches', to='nhl.nhlteam'),
        ),
    ]
