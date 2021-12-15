from sport_parser.khl.config import Config
from sport_parser.nhl.config import NHLConfig


class Creator:
    def __init__(self, request):
        if isinstance(request, str):
            app_name = request
        else:
            app_name = request.app_name
        if app_name == 'khl':
            self.config = Config
        elif app_name == 'nhl':
            self.config = NHLConfig
        else:
            raise AttributeError('no config selected')

    def get_season_class(self, season_id):
        return self.config.season_class(season_id, config=self.config)

    def get_team_class(self, team_id):
        return self.config.team_class(team_id, config=self.config)

    def get_match_class(self, match_id):
        return self.config.match_class(match_id, config=self.config)

    def get_updater(self):
        return self.config.updater(config=self.config)

    # методы для шаблонов
    def get_title(self):
        return self.config.title

    def get_league_title(self):
        return self.config.league_title

    def get_league_logo(self):
        return self.config.league_logo

    def get_background_image(self):
        return self.config.background_image

    def get_theme(self):
        return self.config.theme
