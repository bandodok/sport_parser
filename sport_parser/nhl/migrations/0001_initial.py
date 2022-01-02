# Generated by Django 3.2.6 on 2021-12-14 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NHLMatch',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(null=True)),
                ('time', models.TimeField(null=True)),
                ('arena', models.CharField(blank=True, max_length=100, null=True)),
                ('finished', models.BooleanField(default=False)),
                ('penalties', models.BooleanField(default=False)),
                ('overtime', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NHLSeason',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('external_id', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NHLTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('api_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=4)),
                ('img', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('arena', models.CharField(max_length=100)),
                ('division', models.CharField(max_length=100)),
                ('conference', models.CharField(max_length=100)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='nhl.nhlseason')),
            ],
        ),
        migrations.CreateModel(
            name='NHLProtocol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('g', models.IntegerField(default=0, null=True)),
                ('g_1', models.IntegerField(default=0, null=True)),
                ('g_2', models.IntegerField(default=0, null=True)),
                ('g_3', models.IntegerField(default=0, null=True)),
                ('g_ot', models.IntegerField(default=0, null=True)),
                ('g_b', models.IntegerField(default=0, null=True)),
                ('sog', models.IntegerField(default=0, null=True)),
                ('penalty', models.IntegerField(default=0, null=True)),
                ('faceoff_p', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4, max_length=100, null=True)),
                ('blocks', models.IntegerField(default=0, null=True)),
                ('hits', models.IntegerField(default=0, null=True)),
                ('ppp', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4, max_length=100, null=True)),
                ('ppg', models.IntegerField(default=0, null=True)),
                ('takeaways', models.IntegerField(default=0, null=True)),
                ('giveaways', models.IntegerField(default=0, null=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocols', to='nhl.nhlmatch')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocols', to='nhl.nhlteam')),
            ],
        ),
        migrations.AddField(
            model_name='nhlmatch',
            name='season',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='nhl.nhlseason'),
        ),
        migrations.AddField(
            model_name='nhlmatch',
            name='teams',
            field=models.ManyToManyField(related_name='matches', to='nhl.NHLTeam'),
        ),
    ]
