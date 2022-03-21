# Generated by Django 3.2.6 on 2022-03-21 15:12

from django.db import migrations, models
import json.decoder
import json.encoder


class Migration(migrations.Migration):

    dependencies = [
        ('nhl', '0009_alter_nhlteam_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='nhlseason',
            name='table_data',
            field=models.JSONField(decoder=json.decoder.JSONDecoder, encoder=json.encoder.JSONEncoder, null=True),
        ),
    ]
