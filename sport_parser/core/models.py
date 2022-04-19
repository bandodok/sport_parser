from django.db import models


class LiveMatches(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    league = models.CharField(max_length=100)
    match_id = models.IntegerField()
