# Generated by Django 3.2.6 on 2021-11-21 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khl', '0013_rename_g_p_khlprotocol_g_b'),
    ]

    operations = [
        migrations.AddField(
            model_name='khlmatch',
            name='overtime',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='khlmatch',
            name='penalties',
            field=models.BooleanField(default=False),
        ),
    ]