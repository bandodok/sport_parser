# Generated by Django 3.2.6 on 2022-03-26 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khl', '0018_khlseason_table_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='khlprotocol',
            name='faceoff_p',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='khlprotocol',
            name='pd',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, max_length=100, null=True),
        ),
    ]