import datetime

from sport_parser.khl.db import DB
from sport_parser.khl.objects import ModelList
from sport_parser.khl.parser import Parser


class Updater:
    model_list = ModelList
    parser = Parser()
    db = DB()

    def update(self):
        season = self._get_first_unfinished_match_season()
        self._add_calendar_to_db(season, skip_finished=True)
        self._update_finished_matches()

    def parse_season(self, season_id):
        season = self.model_list.season_model.objects.get(id=season_id)
        self._add_teams_to_db(season)
        calendar = self._add_calendar_to_db(season)
        for match in calendar:
            self._add_match_to_db(match)
            if match.finished:
                self._add_protocol_to_db(match)

    def _update_finished_matches(self):
        matches = self._get_unfinished_matches_until_today()
        if matches:
            for match in matches:
                self._add_finished_match_to_db(match)

    def _add_teams_to_db(self, season):
        teams = self.parser.parse_teams(season)
        for team in teams:
            self.db.add_team(team)
        return self.model_list.team_model.objects.filter(season=season)

    def _add_calendar_to_db(self, season, *, skip_finished=False):
        calendar = self.parser.parse_calendar(season)
        for match in calendar:
            if skip_finished:
                continue
            self.db.add_match(match)
        return self.model_list.match_model.objects.filter(season=season)

    def _add_finished_match_to_db(self, match):
        match = self.parser.parse_finished_match(match)
        if match != 'match not updated':
            db_match = self.db.add_match(match)
            self._add_protocol_to_db(db_match)

    def _add_match_to_db(self, match):
        match = self.parser.parse_match(match)
        self.db.add_match(match)

    def _add_protocol_to_db(self, match):
        protocol = self.parser.parse_protocol(match)
        self.db.add_protocol(protocol)

    def _get_unfinished_matches_until_today(self):
        today = datetime.date.today()
        return self.model_list.match_model.objects.filter(finished=False).filter(date__lte=today).order_by('date', 'time')

    def _get_first_unfinished_match_season(self):
        return self.model_list.match_model.objects.filter(finished=False)[0].season
