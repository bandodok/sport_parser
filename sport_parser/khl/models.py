from django.db import models


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
    time = models.TimeField(null=True)
    season = models.ForeignKey(KHLSeason, on_delete=models.CASCADE, null=True, related_name='matches')
    arena = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    viewers = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
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
    g = models.IntegerField(null=True)
    g_1 = models.IntegerField(null=True)
    g_2 = models.IntegerField(null=True)
    g_3 = models.IntegerField(null=True)
    g_ot = models.IntegerField(null=True)
    g_b = models.IntegerField(null=True)
    sh = models.IntegerField(null=True)
    sog = models.IntegerField(null=True)
    penalty = models.IntegerField(null=True)
    faceoff = models.IntegerField(null=True)
    faceoff_p = models.DecimalField(max_length=100, decimal_places=2, max_digits=4, null=True, blank=True)
    blocks = models.IntegerField(null=True)
    hits = models.IntegerField(null=True)
    fop = models.IntegerField(null=True)
    time_a = models.TimeField(max_length=100, null=True, blank=True)
    vvsh = models.TimeField(max_length=100, null=True, blank=True)
    nshv = models.TimeField(max_length=100, null=True, blank=True)
    pd = models.DecimalField(max_length=100, decimal_places=2, max_digits=4, null=True, blank=True)

    objects = KHLProtocolManager()
