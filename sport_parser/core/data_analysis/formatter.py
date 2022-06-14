import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers


class Formatter:

    def __init__(
            self,
            calendar_serializer: serializers.BaseSerializer
    ):
        self.calendar_serializer = calendar_serializer

    @staticmethod
    def time_to_sec(time):
        """Возвращает время в секундах"""
        return time.hour * 3600 + time.minute * 60 + time.second

    @classmethod
    def sec_to_time(cls, time):
        """Возвращает время в виде строки в формате MM:SS"""
        if isinstance(time, datetime.time):
            time = cls.time_to_sec(time)
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
            if format not in ('int', 'percent', 'time'):
                continue
            else:
                formatted_stats[stat] = cls._set_format(value, format)
        return formatted_stats

    @classmethod
    def bar_stat_format(cls, stats, stat_names):
        for stat, value in stats.items():
            format = stat_names.get(stat, [0, 0, 0])[2]
            if format not in ('int', 'percent', 'time'):
                continue
            else:
                stats[stat]['left_value'] = cls._set_format(value['left_value'], format)
                stats[stat]['right_value'] = cls._set_format(value['right_value'], format)
        return stats

    @classmethod
    def live_bar_stat_format(cls, stat):
        if not stat:
            return 0
        if cls._isfloat(stat):
            return int(stat)
        if ':' in str(stat):
            hours, mins, secs = stat.split(':')
            return int(secs) + int(mins) * 60 + int(hours) * 3600

    def get_json_matches_info(self, matches):
        json_matches = {}
        for match in matches:
            json_matches[f'{match.id}/{match.date}'] = self.calendar_serializer.to_representation(match)
        return json.dumps(json_matches, cls=DjangoJSONEncoder)

    @classmethod
    def _set_format(cls, stat, format):
        if format == 'int':
            return "{:.1f}".format(stat)
        elif format == 'percent':
            return f'{"{:.2f}".format(round(stat, 2))}%'
        elif format == 'time':
            return cls.sec_to_time(stat)

    @staticmethod
    def _isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False
