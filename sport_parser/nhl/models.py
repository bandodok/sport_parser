from django.db import models
import json


class NHLSeason(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.IntegerField(primary_key=True)
    external_id = models.IntegerField(null=True)
    table_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    def __str__(self):
        return str(self.id)


class NHLTeam(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    api_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=4)
    img = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    arena = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    conference = models.CharField(max_length=100)
    season = models.ForeignKey(NHLSeason, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return str(self.id)


class NHLMatch(models.Model):
    id = models.IntegerField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(null=True)
    season = models.ForeignKey(NHLSeason, on_delete=models.CASCADE, null=True, related_name='matches')
    arena = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(choices=[
        ('scheduled', 'scheduled'),
        ('finished', 'finished'),
        ('postponed', 'postponed'),
        ('live', 'live'),
    ], max_length=9, default='scheduled')
    teams = models.ManyToManyField(NHLTeam, related_name='matches')
    penalties = models.BooleanField(default=False)
    overtime = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class NHLProtocol(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(NHLTeam, on_delete=models.CASCADE, related_name='protocols')
    match = models.ForeignKey(NHLMatch, on_delete=models.CASCADE, related_name='protocols')
    g = models.IntegerField(null=True, default=0)
    g_1 = models.IntegerField(null=True, default=0)
    g_2 = models.IntegerField(null=True, default=0)
    g_3 = models.IntegerField(null=True, default=0)
    g_ot = models.IntegerField(null=True, default=0)
    g_b = models.IntegerField(null=True, default=0)

    sh = models.IntegerField(null=True, default=0)
    sog = models.IntegerField(null=True, default=0)
    penalty = models.IntegerField(null=True, default=0)
    faceoff = models.IntegerField(null=True, default=0)
    faceoff_p = models.DecimalField(max_length=100, decimal_places=2, max_digits=5, null=True, blank=True, default=0)
    blocks = models.IntegerField(null=True, default=0)
    hits = models.IntegerField(null=True, default=0)
    ppp = models.DecimalField(max_length=100, decimal_places=2, max_digits=5, null=True, blank=True, default=0)
    ppg = models.IntegerField(null=True, default=0)
    takeaways = models.IntegerField(null=True, default=0)
    giveaways = models.IntegerField(null=True, default=0)


class ModelList:
    season_model = NHLSeason
    match_model = NHLMatch
    team_model = NHLTeam
    protocol_model = NHLProtocol
