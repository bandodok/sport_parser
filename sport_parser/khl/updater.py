import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Max


class Updater:
    def __init__(self, config):
        self.model_list = config.models
        self.parser = config.parser(config)
        self.db = config.db(config)
        self.ignore = config.updater_ignore
        self.channel_layer = get_channel_layer()
        self.season_class = config.season_class
        self.config = config

    def update(self):
        season, new_season = self._get_first_unfinished_match_season()
        if new_season:
            self.parse_season(season)
        else:
            self._add_calendar_to_db(season, skip_finished=True, add_postponed=True)
            self.ws_send_status('updating matches')
            self._update_finished_matches()
            self.ws_send_status('matches updated')
        season_class = self.season_class(season.id, config=self.config)
        season_class.update_season_table_stats()

    def parse_season(self, season_id):
        season = self.model_list.season_model.objects.get(id=season_id)
        self._add_teams_to_db(season)
        calendar = self._add_calendar_to_db(season)
        for match in calendar:
            self._add_match_to_db(match)
        self.ws_send_status('complete')

    def ws_send_status(self, message):
        """Отправляет сообщение в вебсокет"""
        async_to_sync(self.channel_layer.group_send)(
            'update', {'type': 'update.update', 'text': message}
        )

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

    def _add_calendar_to_db(self, season, *, skip_finished=False, add_postponed=False):
        self.ws_send_status('updating calendar dates')
        calendar = self.parser.parse_calendar(season)
        if add_postponed:
            self._postpone_missed_matches(calendar)
        for match in calendar:
            if skip_finished and match['status'] == 'finished' or match['match_id'] in self.ignore:
                continue
            self.ws_send_status(f"updating match: {match['match_id']}")
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
        return self.model_list.match_model.objects.filter(status='scheduled').filter(date__lte=tomorrow).order_by('date')

    def _get_first_unfinished_match_season(self):
        season = self.model_list.match_model.objects.filter(status='scheduled')
        if not season:
            season = self.model_list.season_model.objects.aggregate(Max('id'))['id__max']
            new_season = True
        else:
            season = season[0].season
            new_season = False
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
