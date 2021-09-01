from django.db import models


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
    team_id = models.CharField(max_length=100, null=True)
    match_id = models.IntegerField(null=True)
    g = models.IntegerField(null=True)
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

