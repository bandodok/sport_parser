import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Updater:
    def __init__(self, config):
        self.model_list = config.models
        self.parser = config.parser(config)
        self.db = config.db(config)
        self.ignore = config.updater_ignore
        self.channel_layer = get_channel_layer()

    def update(self):
        season = self._get_first_unfinished_match_season()
        self._add_calendar_to_db(season, skip_finished=True)

        self.ws_send_status('updating matches')
        self._update_finished_matches()
        self.ws_send_status('matches updated')

    def parse_season(self, season_id):
        season = self.model_list.season_model.objects.get(id=season_id)
        self._add_teams_to_db(season)
        calendar = self._add_calendar_to_db(season)
        for match in calendar:
            self._add_match_to_db(match)
            if match.finished:
                self._add_protocol_to_db(match)
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
                self._add_finished_match_to_db(match)

    def _add_teams_to_db(self, season):
        self.ws_send_status(f'updating teams for season {season}')
        teams = self.parser.parse_teams(season)
        for team in teams:
            self.ws_send_status(f'updating team {team}')
            self.db.add_team(team)
        self.ws_send_status('teams updated')
        return self.model_list.team_model.objects.filter(season=season)

    def _add_calendar_to_db(self, season, *, skip_finished=False):
        self.ws_send_status('updating calendar dates')
        calendar = self.parser.parse_calendar(season)
        for match in calendar:
            if skip_finished or match['match_id'] in self.ignore:
                continue
            self.ws_send_status(f"updating match: {match['match_id']}")
            self.db.add_match(match)
        self.ws_send_status('calendar updated')
        return self.model_list.match_model.objects.filter(season=season)

    def _add_finished_match_to_db(self, match):
        match = self.parser.parse_finished_match(match)
        if match != 'match not updated':
            self.ws_send_status(f"updating match info: {match['match_id']}")
            db_match = self.db.add_match(match)
            self._add_protocol_to_db(db_match)

    def _add_match_to_db(self, match):
        match = self.parser.parse_match(match)
        if match == 'match not updated':
            return
        self.ws_send_status(f"updating match: {match['match_id']}")
        self.db.add_match(match)

    def _add_protocol_to_db(self, match):
        self.ws_send_status(f"updating protocols for match: {match.id}")
        protocol = self.parser.parse_protocol(match)
        self.db.add_protocol(protocol)

    def _get_unfinished_matches_until_today(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        return self.model_list.match_model.objects.filter(finished=False).filter(date__lte=tomorrow).order_by('date')

    def _get_first_unfinished_match_season(self):
        return self.model_list.match_model.objects.filter(finished=False)[0].season
