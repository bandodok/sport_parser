import datetime
import json
from sport_parser.api.serializers import CalendarSerializer
from django.core.serializers.json import DjangoJSONEncoder


class Formatter:
    def __init__(self, config):
        self.calendar_serializer = config.calendar_serializer

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

    def date_format(self, date):
        splitted_date = date.split(' ')[:-1]
        if not splitted_date[0]:
            splitted_date.pop(0)
        day, month, year = splitted_date
        if len(day) == 1:
            day = f'0{day}'
        month = self.month_to_int_replace(month)
        year = year[:-1]
        return f'{year}-{month}-{day}'

    @staticmethod
    def month_to_int_replace(month: str):
        """Возвращает номер месяца по слову"""
        months = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        return months.get(month)

    def get_json_last_matches_info(self, matches):
        last_matches = {}
        for match in matches:
            last_matches[f'{match.id}/{match.date}'] = self.calendar_serializer.to_representation(match)
        return json.dumps(last_matches, cls=DjangoJSONEncoder)

    def get_json_future_matches_info(self, matches):
        future_matches = {}
        for match in matches:
            future_matches[f'{match.id}/{match.date}'] = self.calendar_serializer.to_representation(match)
        return json.dumps(future_matches, cls=DjangoJSONEncoder)

    @classmethod
    def _set_format(cls, stat, format):
        if format == 'int':
            return "{:.1f}".format(stat)
        elif format == 'percent':
            return f'{"{:.2f}".format(round(stat, 2))}%'
        elif format == 'time':
            return cls.sec_to_time(stat)
