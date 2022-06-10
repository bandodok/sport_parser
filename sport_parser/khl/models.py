from django.db import models
import json

from sport_parser.core.models import SeasonModel, TeamModel, MatchModel, ProtocolModel, ModelList


class KHLSeason(SeasonModel):
    pass


class KHLTeams(TeamModel):
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, related_name='teams')


class KHLMatch(MatchModel):
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, null=True, related_name='matches')
    home_team = models.ForeignKey(KHLTeams, on_delete=models.CASCADE, related_name='home_matches', null=True)
    guest_team = models.ForeignKey(KHLTeams, on_delete=models.CASCADE, related_name='guest_matches', null=True)
    teams = models.ManyToManyField(KHLTeams, related_name='matches')


class KHLProtocol(ProtocolModel):
    """Таблица с протоколами матчей КХЛ
    created - Дата создания записи
    updated УДАЛИТЬ
    team - id клуба
    match_id - id матча
    Sh - Броски
    G - Голы
    SoG - Броски в створ
    Penalty - Штрафное время
    FaceOff - Выигранные вбрасывания
    vbr_p - Вбрасывания в процентах
    Blocks - Блокированные броски соперника
    Hits - Силовые приемы
    fop - Фол против игрока
    TimeA - Время в атаке
    vvsh - Время владения шайбой
    nshv - Нейтральное время владения шайбой
    pd - Пройденная дистанция
    """
    team = models.ForeignKey(KHLTeams, on_delete=models.CASCADE, related_name='protocols')
    match = models.ForeignKey(KHLMatch, on_delete=models.CASCADE, related_name='protocols')
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, related_name='protocols')

    sh = models.IntegerField(null=True, default=0)
    sog = models.IntegerField(null=True, default=0)
    penalty = models.IntegerField(null=True, default=0)
    faceoff = models.IntegerField(null=True, default=0)
    faceoff_p = models.DecimalField(max_length=100, decimal_places=2, max_digits=5, null=True, blank=True, default=0)
    blocks = models.IntegerField(null=True, default=0)
    hits = models.IntegerField(null=True, default=0)
    fop = models.IntegerField(null=True, default=0)
    time_a = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    vvsh = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    nshv = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    pd = models.DecimalField(max_length=100, decimal_places=2, max_digits=5, null=True, blank=True, default=0)


class KHLModelList(ModelList):
    season_model = KHLSeason
    match_model = KHLMatch
    team_model = KHLTeams
    protocol_model = KHLProtocol
