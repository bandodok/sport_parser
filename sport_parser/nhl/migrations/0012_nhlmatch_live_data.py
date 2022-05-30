# Generated by Django 3.2.6 on 2022-04-07 17:25

from django.db import migrations, models
import json.decoder
import json.encoder


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0011_alter_nhlmatch_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='nhlmatch',
            name='live_data',
            field=models.JSONField(decoder=json.decoder.JSONDecoder, encoder=json.encoder.JSONEncoder, null=True),
        ),
    ]