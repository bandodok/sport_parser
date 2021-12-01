import datetime
import json
from sport_parser.api.serializers import CalendarSerializer
from django.core.serializers.json import DjangoJSONEncoder


class Formatter:
    calendar_serializer = CalendarSerializer()

    @staticmethod
    def time_to_sec(time):
        """Возвращает время в секундах"""
        return time.hour * 3600 + time.minute * 60 + time.second

    @classmethod
    def sec_to_time(cls, time):
        """Возвращает время в виде строки в формате HH:MM"""
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
            if format == 'int':
                formatted_stats[stat] = "{:.1f}".format(value)
            elif format == 'percent':
                formatted_stats[stat] = f'{"{:.2f}".format(round(value, 2))}%'
            elif format == 'time':
                formatted_stats[stat] = cls.sec_to_time(value)
            else:
                continue
        return formatted_stats

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
