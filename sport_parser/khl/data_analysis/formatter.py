import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder


class Formatter:
    @staticmethod
    def time_to_sec(time):
        """Возвращает время в секундах"""
        return time.hour * 3600 + time.minute * 60 + time.second

    @staticmethod
    def sec_to_time(time):
        """Возвращает время в виде строки в формате HH:MM"""
        min = int(time // 60)
        sec = int(time - min * 60)
        if sec < 10:
            sec = f'0{sec}'
        return f'{min}:{sec}'

    @classmethod
    def chart_stat_format(cls, stat):
        if type(stat) == datetime.time:
            return cls.time_to_sec(stat)
        else:
            return stat

    @classmethod
    def table_stat_format(cls, stats, stat_names):
        formatted_stats = {}
        for stat, value in stats.items():
            format = stat_names.get(stat, [0, 0])[1]
            if format == 'int':
                formatted_stats[stat] = "{:.1f}".format(value)
            elif format == 'percent':
                formatted_stats[stat] = f'{"{:.2f}".format(round(value, 2))}%'
            elif format == 'time':
                formatted_stats[stat] = cls.sec_to_time(value)
            else:
                continue
        return formatted_stats

    @staticmethod
    def get_json_last_matches_info(matches):
        last_matches = {}
        for match in matches:
            protocol1, protocol2 = match.protocols.all()
            last_matches[f'{match.id}/{match.date}'] = {
                'date': match.date,
                'time': match.time,
                'id': match.id,
                'team1_name': protocol1.team.name,
                'team1_score': protocol1.g,
                'team1_image': protocol1.team.img,
                'team1_id': protocol1.team.id,
                'team2_name': protocol2.team.name,
                'team2_score': protocol2.g,
                'team2_image': protocol2.team.img,
                'team2_id': protocol2.team.id,
            }
        return json.dumps(last_matches, cls=DjangoJSONEncoder)

    @staticmethod
    def get_json_future_matches_info(matches):
        future_matches = {}
        for match in matches:
            team1, team2 = match.teams.all()
            future_matches[f'{match.id}/{match.date}'] = {
                'date': match.date,
                'time': match.time,
                'id': match.id,
                'team1_name': team1.name,
                'team1_image': team1.img,
                'team1_id': team1.id,
                'team2_name': team2.name,
                'team2_image': team2.img,
                'team2_id': team2.id,
            }
        return json.dumps(future_matches, cls=DjangoJSONEncoder)
