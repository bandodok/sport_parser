# Generated by Django 3.2.6 on 2021-10-09 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('khl', '0007_alter_khlmatch_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='khlprotocol',
            name='team_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='khl.khlteams'),
        ),
    ]