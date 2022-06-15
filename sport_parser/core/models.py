import json

from django.db import models


class AbstractModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LiveMatches(AbstractModel):
    league = models.CharField(max_length=100)
    match_id = models.IntegerField()


class SeasonModel(AbstractModel):
    id = models.IntegerField(primary_key=True)
    external_id = models.IntegerField(null=True)
    table_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True


class TeamModel(AbstractModel):
    season = models.ForeignKey(SeasonModel, on_delete=models.CASCADE, related_name='teams')

    name = models.CharField(max_length=100)
    img = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    arena = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    conference = models.CharField(max_length=100)

    chart_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True


class MatchModel(AbstractModel):
    season = models.ForeignKey(SeasonModel, on_delete=models.CASCADE, null=True, related_name='matches')
    home_team = models.ForeignKey(TeamModel, on_delete=models.CASCADE, related_name='home_matches', null=True)
    guest_team = models.ForeignKey(TeamModel, on_delete=models.CASCADE, related_name='guest_matches', null=True)
    teams = models.ManyToManyField(TeamModel, related_name='matches')

    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(null=True)
    arena = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    viewers = models.IntegerField(default=0)
    status = models.CharField(choices=[
        ('scheduled', 'scheduled'),
        ('finished', 'finished'),
        ('postponed', 'postponed'),
        ('live', 'live'),
        ('game over', 'game over'),
    ], max_length=9, default='scheduled')
    penalties = models.BooleanField(default=False)
    overtime = models.BooleanField(default=False)

    table_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)
    chart_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)
    bar_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True


class ProtocolModel(AbstractModel):
    team = models.ForeignKey(TeamModel, on_delete=models.CASCADE, related_name='protocols')
    match = models.ForeignKey(MatchModel, on_delete=models.CASCADE, related_name='protocols')
    season = models.ForeignKey(SeasonModel, on_delete=models.CASCADE, related_name='protocols')

    g = models.IntegerField(null=True, default=0)
    g_1 = models.IntegerField(null=True, default=0)
    g_2 = models.IntegerField(null=True, default=0)
    g_3 = models.IntegerField(null=True, default=0)
    g_ot = models.IntegerField(null=True, default=0)
    g_b = models.IntegerField(null=True, default=0)

    class Meta:
        abstract = True


class LiveMatchModel(AbstractModel):
    match = models.OneToOneField(MatchModel, on_delete=models.CASCADE, related_name='live')

    status = models.CharField(max_length=100, null=True, blank=True)
    team1_score = models.IntegerField(null=True, default=0)
    team2_score = models.IntegerField(null=True, default=0)

    bar_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    class Meta:
        abstract = True


class ModelList:
    season_model: SeasonModel
    match_model: MatchModel
    team_model: TeamModel
    protocol_model: ProtocolModel
    live_match_model: LiveMatchModel
