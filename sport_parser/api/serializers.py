from abc import ABC

from rest_framework import serializers


class CalendarSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, match):
        if match.finished:
            protocol1, protocol2 = match.protocols.all()
            return {
                'date': match.date,
                'time': match.time,
                'id': match.id,
                'finished': match.finished,
                'team1_name': protocol1.team.name,
                'team1_score': protocol1.g,
                'team1_image': protocol1.team.img,
                'team1_id': protocol1.team.id,
                'team2_name': protocol2.team.name,
                'team2_score': protocol2.g,
                'team2_image': protocol2.team.img,
                'team2_id': protocol2.team.id,
            }
        else:
            team1, team2 = match.teams.all()
            return {
                'date': match.date,
                'time': match.time,
                'id': match.id,
                'finished': match.finished,
                'team1_name': team1.name,
                'team1_image': team1.img,
                'team1_id': team1.id,
                'team2_name': team2.name,
                'team2_image': team2.img,
                'team2_id': team2.id,
            }
