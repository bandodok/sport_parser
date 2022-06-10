import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Max
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
from django.db.models import Q

from sport_parser.core.data_analysis.stats_updater import StatsUpdater

from sport_parser.core.data_taking.db import DB
from sport_parser.core.data_taking.parser import Parser, MatchStatus, MatchData, TeamData, MatchProtocolsData
from sport_parser.core.exceptions import UnableToGetProtocolException
from sport_parser.core.models import MatchModel


class Updater:
    def __init__(self, config):
        self.model_list = config.models
        self.parser: Parser = config.parser(config)
        self.db: DB = config.db(config)
        self.ignore = config.updater_ignore
        self.channel_layer = get_channel_layer()
        self.season_class = config.season_class
        self.match_class = config.match_class
        self.config = config
        self.stats_updater = StatsUpdater(
            db=config.db(config),
            table_stats=config.TableStats(config=config),
            chart_stats=config.ChartStats(config=config),
            bar_stats=config.BarStats(config=config),
        )

    def update(self):
        """Обновляет последний сезон. Парсит сезон, если  он еще не выгружен."""
        season_id, new_season = self._get_first_unfinished_match_season()
        if new_season:
            self.ws_send_status(f'parsing new season')
            self.parse_season(season_id)
        else:
            self.ws_send_status(f'updating season')
            self.update_season(season_id)

    def update_season(self, season_id: int) -> None:
        """
        Обновляет информацию по матчам сезона.

        :param season_id: id сезона
        """
        self._add_season_to_stats_updater(season_id)
        calendar_data = self._parse_calendar(season_id, skip_finished=True, skip_live=True)
        for match in calendar_data:
            self._add_match_to_db(match)
        self._update_finished_matches()
        self._postpone_missed_matches(calendar_data)

        self._update_stats()

    def parse_season(self, season_id: int) -> None:
        """
        Парсит информацию по командам и матчам сезона и сохраняет в базу данных

        :param season_id: id сезона
        """
        self._add_season_to_stats_updater(season_id)
        # парсинг команд
        teams_data = self._parse_teams(season_id)
        self._add_teams_to_db(teams_data)

        # парсинг матчей
        calendar_data = self._parse_calendar(season_id)
        for match in calendar_data:
            self._add_match_to_db(match)

        # обновление статистики
        self._update_stats()

    def update_live_match(self, match_id):
        live_match_data = self.parser.parse_live_protocol(match_id)
        if live_match_data['match_status'] == 'матч скоро начнется':
            return

        match_class = self.match_class(match_id, config=self.config)
        live_match_data['match_id'] = match_id
        live_match_data['data'] = match_class.get_live_bar_stats(live_match_data['data'])
        self.db.update_live_match(live_match_data)

        if live_match_data['match_status'] == 'матч завершен':
            self.db.remove_live_match(self.config.name, match_id)
            self.db.set_match_status(match_id, MatchStatus.GAME_OVER)
            return

    def ws_send_status(self, message: str) -> None:
        """Отправляет сообщение в вебсокет"""
        async_to_sync(self.channel_layer.group_send)(
            'update', {'type': 'update.update', 'text': message}
        )

    def _update_stats(self) -> None:
        """Запускает обновление статистики сезонов, команд и матчей, добавленных ранее в stats_updater"""
        self.ws_send_status('updating stats')
        self.stats_updater.update()
        self._add_matches_to_live_updater()
        self.ws_send_status('complete')

    def _update_finished_matches(self) -> None:
        """Проверяет последние незавершенные матчи, если они завершились - обновляет статус и парсит протоколы"""
        matches = self._get_unfinished_matches_until_today()
        if matches:
            for match in matches:
                if self.parser.is_match_finished(match.id):
                    try:
                        protocol = self._parse_protocol(match.id)
                    except UnableToGetProtocolException:
                        self.ws_send_status(f'Unable to parse protocol for match {match.id}.')
                    else:
                        match_data = self._parse_finished_match(match.id)
                        match_data.status = MatchStatus.FINISHED
                        self._add_match_to_db(match_data)
                        self._add_protocol_to_db(protocol)

    def _parse_teams(self, season_id: int) -> list[TeamData]:
        """
        Возвращает список информации по командам сезона

        :param season_id: id сезона
        :return: список информации по командам в формате TeamData
        """
        self.ws_send_status(f'parsing teams for season {season_id}')
        season = self.model_list.season_model.objects.get(id=season_id)
        return self.parser.parse_teams(season)

    def _parse_calendar(self, season_id: int, *, skip_finished=False, skip_live=True) -> list[MatchData]:
        """
        Возвращает список информации по матчам сезона

        :param season_id: id сезона
        :param skip_finished: если True, не возвращает информацию по завершенным матчам
        :param skip_live: если True, не возвращает информацию по текущим матчам
        :return: список информации по матчам в формате MatchData
        """
        self.ws_send_status('parsing calendar')
        season = self.model_list.season_model.objects.get(id=season_id)
        calendar_data = self.parser.parse_calendar(season)
        self.ws_send_status(f'calendar len: {len(calendar_data)}')
        output_calendar_data = []
        for match in calendar_data:
            if skip_finished and match.status == MatchStatus.FINISHED or \
               skip_live and match.status == MatchStatus.LIVE or \
               match.id in self.ignore:
                continue
            else:
                self._parse_additional_match_info(match)
                output_calendar_data.append(match)
        self.ws_send_status(f'ret calendar len: {len(output_calendar_data)}')
        return output_calendar_data

    def _parse_additional_match_info(self, match: MatchData) -> None:
        """
        Парсит дополнительную информацию по матчу и дополняет экземпляр MatchData
        :param match: информация о матче в формате MatchData
        """
        self.ws_send_status(f"parsing info for match: {match.id}")
        self.parser.parse_match_additional_info(match)

    def _parse_finished_match(self, match_id: int) -> MatchData:
        """
        Парсит информацию по завершенному матчу

        :param match_id: id матча
        :return: информация о матче в формате MatchData
        """
        match = self.db.get_match_data(match_id)
        return self.parser.parse_finished_match(match)

    def _parse_protocol(self, match_id: int) -> MatchProtocolsData:
        """
        Возвращает протокол матча для обеих команд

        :param match_id: id матча
        :return: протокол матча в формате MatchProtocolsData
        """
        self.ws_send_status(f"updating protocols for match: {match_id}")
        return self.parser.parse_protocol(match_id)

    def _add_teams_to_db(self, teams: list[TeamData]) -> None:
        """
        Сохраняет информацию по матчам в базу данных.

        :param teams: список информации по командам в формате TeamData
        """
        self.ws_send_status('saving teams info')
        for team in teams:
            self.ws_send_status(f'team: {team.name}')
            self.db.add_team(team)
        self.ws_send_status('teams saved')

    def _add_match_to_db(self, match: MatchData) -> None:
        """
        Сохраняет информацию по матчу в базу данных.

        :param match: информацию по матчу в формате MatchData
        """
        if match != 'match not updated':
            self.ws_send_status(f"updating match info: {match.id}")
            match_model, new = self.db.add_match(match)
            if new:
                self._add_match_to_stats_updater(match_model)
            if match.status.value == 'finished':
                try:
                    protocol = self._parse_protocol(match.id)
                except UnableToGetProtocolException:
                    self.ws_send_status(
                        f'Unable to parse protocol for match {match.id}. Match status will be changed for "scheduled"'
                    )
                    self.db.set_match_status(match.id, MatchStatus.SCHEDULED)
                else:
                    self._add_protocol_to_db(protocol)
                    self._add_match_to_stats_updater(match_model)

    def _add_protocol_to_db(self, protocol: MatchProtocolsData):
        """
        Сохраняет протокол матча в базу данных.

        :param protocol: протокол матча в формате MatchProtocolData
        """
        self.db.add_protocol(protocol)

    def _add_season_to_stats_updater(self, season_id: int) -> None:
        """
        Добавляет сезон в список к обновлению статистики.

        :param season_id: id сезона
        """
        self.stats_updater.add_season(season_id)

    def _add_match_to_stats_updater(self, match: MatchModel) -> None:
        """
        Добавляет матч и команды матча в список к обновлению статистики.
        :param match: id матча
        """
        self.stats_updater.add_match(match.id)
        self.stats_updater.add_team(match.home_team.id)
        self.stats_updater.add_team(match.guest_team.id)

    def _get_unfinished_matches_id(self) -> list[int]:
        """
        Возвращает список id всех незавершенных матчей.

        :return: список id матчей
        """
        return self.model_list.match_model.objects.filter(status='scheduled').values_list('id', flat=True)

    def _get_unfinished_matches_until_today(self) -> list[MatchModel]:
        """
        Возвращает список незавершенных матчей по текущий день.

        :return: список матчей в формате строк модели MatchModel
        """
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        return self.model_list.match_model.objects\
            .filter(Q(status='scheduled') | Q(status='game over'))\
            .filter(date__lte=tomorrow)\
            .order_by('date')

    def _get_first_unfinished_match_season(self) -> tuple[int, bool]:
        """
        Первым параметром возвращает номер сезона первого незавершенного матча.
        Вторым параметром возвращает True, если сезон есть в базе данных, но для него еще не парсились матчи.

        :return: кортеж с номером и состоянием сезона
        """
        scheduled_matches = self.model_list.match_model.objects.filter(status='scheduled')
        if scheduled_matches:
            season = scheduled_matches[0].season.id
            new_season = False
        else:
            last_season = self.model_list.match_model.objects.filter(status='finished')
            max_season = self.model_list.season_model.objects.aggregate(Max('id'))['id__max']
            if last_season and last_season[0].season.id == max_season:
                season = last_season[0].season.id
                new_season = False
            else:
                season = max_season
                new_season = True
        return season, new_season

    def _get_postponed_matches(self, season) -> list[MatchModel]:
        """
        Возвращает все отмененные матчи сезона.

        :param season: id сезона
        :return: список матчей в формате строк модели MatchModel
        """
        return self.model_list.match_model.objects.filter(status='postponed').filter(season=season)

    def _postpone_missed_matches(self, calendar: list[MatchData]) -> None:
        """Задает статус 'postponed' для матчей, которые убрали из календаря"""
        calendar_ids = [match.id for match in calendar]
        db_ids = self._get_unfinished_matches_id()
        for match_id in db_ids:
            if match_id not in calendar_ids:
                self.db.set_match_status(match_id, MatchStatus.POSTPONED)

    def _update_postponed(self, calendar) -> None:
        """Обновляет информацию по отмененным матчам"""
        calendar_dict = {match['match_id']: match for match in calendar}
        season = calendar[0]['season']
        postponed_matches = self._get_postponed_matches(season)
        for match in postponed_matches:
            if match.id in calendar_dict:
                if calendar_dict[match.id]['status'] != 'postponed':
                    self._add_match_to_db(match)

    def _add_matches_to_live_updater(self):
        interval = IntervalSchedule.objects.get(every=1, period='seconds')
        today = timezone.now()
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        matches = self.model_list.match_model.objects. \
            filter(status='scheduled'). \
            filter(date__gte=today). \
            filter(date__lte=tomorrow)
        for match in matches:
            config = self.config.name
            match_id = match.id
            update_start_date = match.date - datetime.timedelta(minutes=10)
            PeriodicTask.objects.get_or_create(
                name=f'{config}_{match_id}_live_match',
                interval_id=interval.id,
                task='schedule_live_match',
                args=f'["{config}", "{match_id}"]',
                start_time=update_start_date,
                one_off=True,
                enabled=True,
                queue='regular_update'
            )
