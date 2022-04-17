import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Max
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
from django.db.models import Q


class Updater:
    def __init__(self, config):
        self.model_list = config.models
        self.parser = config.parser(config)
        self.db = config.db(config)
        self.ignore = config.updater_ignore
        self.channel_layer = get_channel_layer()
        self.season_class = config.season_class
        self.match_class = config.match_class
        self.config = config

    def update(self):
        season, new_season = self._get_first_unfinished_match_season()
        if new_season:
            self.parse_season(season.id)
        else:
            self._add_calendar_to_db(season, skip_finished=True, skip_live=True, add_postponed=True)
            self.ws_send_status('updating matches')
            self._update_finished_matches()
            self.ws_send_status('matches updated')
            self._update_season_stats_data(season.id)
        self._add_matches_to_live_updater()

    def parse_season(self, season_id: int):
        season = self.model_list.season_model.objects.get(id=season_id)
        self._add_teams_to_db(season)
        calendar = self._add_calendar_to_db(season)
        for match in calendar:
            self._add_match_to_db(match)
        self.ws_send_status('complete')
        self._update_season_stats_data(season.id)

    def update_live_match(self, match_id):
        live_match_data = self.parser.parse_live_protocol(match_id)
        if live_match_data['match_status'] == 'матч скоро начнется':
            return

        match_class = self.match_class(match_id, config=self.config)
        live_match_data['match_id'] = match_id
        live_match_data['data'] = match_class.get_live_bar_stats(live_match_data['data'])
        self.db.update_live_match(live_match_data)

        if live_match_data['match_status'] == 'матч завершен':
            self.db.remove_live_match(match_id)
            self._set_game_over_status(match_class.data)
            return

    def ws_send_status(self, message):
        """Отправляет сообщение в вебсокет"""
        async_to_sync(self.channel_layer.group_send)(
            'update', {'type': 'update.update', 'text': message}
        )

    def _update_season_stats_data(self, season_id: int):
        self.ws_send_status('updating season stats data')
        season_class = self.season_class(season_id, config=self.config)
        season_class.update_season_table_stats()
        self.ws_send_status('season stats data updated')

    def _update_finished_matches(self):
        matches = self._get_unfinished_matches_until_today()
        if matches:
            for match in matches:
                self._add_match_to_db(match)

    def _add_teams_to_db(self, season):
        self.ws_send_status(f'updating teams for season {season}')
        teams = self.parser.parse_teams(season)
        for team in teams:
            self.ws_send_status(f'updating team {team}')
            self.db.add_team(team)
        self.ws_send_status('teams updated')
        return self.model_list.team_model.objects.filter(season=season)

    def _add_calendar_to_db(self, season, *, skip_finished=False, skip_live=True, add_postponed=False):
        self.ws_send_status('updating calendar dates')
        calendar = self.parser.parse_calendar(season)
        if add_postponed:
            self._postpone_missed_matches(calendar)
        for match in calendar:
            if skip_finished and match['status'] == 'finished' or match['match_id'] in self.ignore:
                continue
            self.ws_send_status(f"updating match: {match['match_id']}")
            if skip_live:
                self.db.add_match(match, skip_live=True)
            else:
                self.db.add_match(match)
        self.ws_send_status('calendar updated')

        self.ws_send_status('updating postponed matches')
        self._update_postponed(calendar)
        self.ws_send_status('complete')

        return self.model_list.match_model.objects.filter(season=season)

    def _add_match_to_db(self, match):
        match = self.parser.parse_match(match)
        if match != 'match not updated':
            self.ws_send_status(f"updating match info: {match['match_id']}")
            db_match = self.db.add_match(match)
            if db_match.status == 'finished':
                self._add_protocol_to_db(db_match)

    def _add_protocol_to_db(self, match):
        self.ws_send_status(f"updating protocols for match: {match.id}")
        protocol = self.parser.parse_protocol(match)
        self.db.add_protocol(protocol)

    def _get_unfinished_matches_id(self):
        return self.model_list.match_model.objects.filter(status='scheduled').values_list('id', flat=True)

    def _get_unfinished_matches_until_today(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        return self.model_list.match_model.objects\
            .filter(Q(status='scheduled') | Q(status='game over'))\
            .filter(date__lte=tomorrow)\
            .order_by('date')

    def _get_first_unfinished_match_season(self):
        scheduled_matches = self.model_list.match_model.objects.filter(status='scheduled')
        if scheduled_matches:
            season = scheduled_matches[0].season
            new_season = False
        else:
            last_season = self.model_list.match_model.objects.filter(status='finished')
            max_season = self.model_list.season_model.objects.aggregate(Max('id'))['id__max']
            if last_season and last_season[0].season.id == max_season:
                season = last_season[0].season
                new_season = False
            else:
                season = self.model_list.season_model.objects.get(id=max_season)
                new_season = True
        return season, new_season

    def _get_postponed_matches(self, season):
        return self.model_list.match_model.objects.filter(status='postponed').filter(season=season)

    def _postpone_missed_matches(self, calendar) -> None:
        """Задает статус 'postponed' для матчей, которые убрали из календаря"""
        calendar_ids = [match['match_id'] for match in calendar]
        db_ids = self._get_unfinished_matches_id()
        season = calendar[0]['season']
        for match_id in db_ids:
            if str(match_id) not in calendar_ids:
                self.db.add_match({
                    'match_id': match_id,
                    'status': 'postponed',
                    'season': season
                })

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

    def _set_game_over_status(self, match):
        """
        Устанавливает статус 'game over' для матча
        Такой матч не будет проигнорирован при регулярном обновлении

        :param match трока базы данных матча
        """
        self.db.set_match_status(match, 'game over')
