from django.db import models
import json


class KHLProtocolManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_team_match_list(self, team):
        return self.get_queryset().filter(team_id=team).values_list('match_id', flat=True)


class KHLSeason(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.IntegerField(primary_key=True)
    external_id = models.IntegerField(null=True)
    table_data = models.JSONField(null=True, encoder=json.JSONEncoder, decoder=json.JSONDecoder)

    def __str__(self):
        return str(self.id)


class KHLTeams(models.Model):
    """ """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    arena = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    conference = models.CharField(max_length=100)
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return str(self.name)

    def last_matches(self, num, *, exclude=0):
        return self.matches.filter(finished=True).exclude(id=exclude).order_by('-date')[:num]

    def future_matches(self, num):
        return self.matches.filter(finished=False).order_by('date')[:num]


class KHLMatch(models.Model):
    """ """
    id = models.IntegerField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(null=True)
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, null=True, related_name='matches')
    arena = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    viewers = models.IntegerField(default=0)
    status = models.CharField(choices=[
        ('scheduled', 'scheduled'),
        ('finished', 'finished'),
        ('postponed', 'postponed'),
    ], max_length=9, default='scheduled')
    teams = models.ManyToManyField(KHLTeams, related_name='matches')
    penalties = models.BooleanField(default=False)
    overtime = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class KHLProtocol(models.Model):
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(KHLTeams, on_delete=models.CASCADE, related_name='protocols')
    match = models.ForeignKey(KHLMatch, on_delete=models.CASCADE, related_name='protocols')
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
    faceoff_p = models.DecimalField(max_length=100, decimal_places=2, max_digits=4, null=True, blank=True, default=0)
    blocks = models.IntegerField(null=True, default=0)
    hits = models.IntegerField(null=True, default=0)
    fop = models.IntegerField(null=True, default=0)
    time_a = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    vvsh = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    nshv = models.TimeField(max_length=100, null=True, blank=True, default='00:00:00')
    pd = models.DecimalField(max_length=100, decimal_places=2, max_digits=4, null=True, blank=True, default=0)

    objects = KHLProtocolManager()


class ModelList:
    season_model = KHLSeason
    match_model = KHLMatch
    team_model = KHLTeams
    protocol_model = KHLProtocol
