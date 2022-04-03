from django.db import models
import json


class LiveMatches(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    league = models.CharField(max_length=100)
    match_id = models.IntegerField()
    match_data = models.JSONField(
        null=True,
        encoder=json.JSONEncoder,
        decoder=json.JSONDecoder,
        default=dict(
            match_status='матч скоро начнется',
            team_1_score='-',
            team_2_score='-',
            data={
                'row_home': '',
                'row_guest': ''
            }))
