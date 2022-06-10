from django.db import models

from sport_parser.core.models import SeasonModel, TeamModel, MatchModel, ProtocolModel, ModelList


class NHLSeason(SeasonModel):
    pass


class NHLTeam(TeamModel):
    season = models.ForeignKey(NHLSeason, on_delete=models.CASCADE, related_name='teams')


class NHLMatch(MatchModel):
    season = models.ForeignKey(NHLSeason, on_delete=models.CASCADE, null=True, related_name='matches')
    home_team = models.ForeignKey(NHLTeam, on_delete=models.CASCADE, related_name='home_matches', null=True)
    guest_team = models.ForeignKey(NHLTeam, on_delete=models.CASCADE, related_name='guest_matches', null=True)
    teams = models.ManyToManyField(NHLTeam, related_name='matches')


class NHLProtocol(ProtocolModel):
    team = models.ForeignKey(NHLTeam, on_delete=models.CASCADE, related_name='protocols')
    match = models.ForeignKey(NHLMatch, on_delete=models.CASCADE, related_name='protocols')
    season = models.ForeignKey(NHLSeason, on_delete=models.CASCADE, related_name='protocols')

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


class NHLModelList(ModelList):
    season_model = NHLSeason
    match_model = NHLMatch
    team_model = NHLTeam
    protocol_model = NHLProtocol
