from abc import ABC

from rest_framework import serializers


def get_sorted_teams_by_m2m_table(match):
    meta = match._meta
    app_label = meta.app_label
    match_model = meta.model_name
    team_model = meta.many_to_many[0].column
    m2m_table = f'{app_label}_{match_model}_{team_model}'
    team1, team2 = match.teams.all().extra(select={'add_id': f'{m2m_table}.id'}).order_by('add_id')
    return team1, team2


class CalendarSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, match):
        if match.status == 'finished':
            protocol1, protocol2 = match.protocols.all().order_by('id')
            return {
                'date': match.date,
                'id': match.id,
                'status': match.status,
                'overtime': match.overtime,
                'penalties': match.penalties,
                'team1_name': protocol1.team.name,
                'team1_score': {
                    'match': protocol1.g + protocol1.g_b,
                    'p1': protocol1.g_1,
                    'p2': protocol1.g_2,
                    'p3': protocol1.g_3,
                    'ot': protocol1.g_ot,
                    'b': protocol1.g_b,
                },
                'team1_image': protocol1.team.img,
                'team1_id': protocol1.team.id,
                'team2_name': protocol2.team.name,
                'team2_score': {
                    'match': protocol2.g + protocol2.g_b,
                    'p1': protocol2.g_1,
                    'p2': protocol2.g_2,
                    'p3': protocol2.g_3,
                    'ot': protocol2.g_ot,
                    'b': protocol2.g_b,
                },
                'team2_image': protocol2.team.img,
                'team2_id': protocol2.team.id,
            }
        else:
            team1, team2 = get_sorted_teams_by_m2m_table(match)
            output = {
                'date': match.date,
                'id': match.id,
                'status': match.status,
                'team1_name': team1.name,
                'team1_image': team1.img,
                'team1_id': team1.id,
                'team2_name': team2.name,
                'team2_image': team2.img,
                'team2_id': team2.id,
                'match_data': match.live_data
            }
            return output


class LiveMatchSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, match):
        live_data = match.live_data
        return {
            'id': match.id,
            'status': live_data.get('match_status', ''),
            'team_1_score': live_data.get('team_1_score', ''),
            'team_2_score': live_data.get('team_2_score', ''),
            'data': live_data.get('data', '')
        }
