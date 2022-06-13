from django.db.models import Max

from sport_parser.core.configs import ConfigType


class Creator:
    def __init__(self, config: ConfigType):
        self.config = config.value

    def get_season_class(self, season_id):
        if season_id == 0:
            season_id = self.config.models.season_model.objects.aggregate(Max('id'))['id__max']
        return self.config.season_class(season_id, config=self.config)

    def get_team_class(self, team_id):
        if team_id == 0:
            team_id = self.config.models.team_model.objects.aggregate(Max('id'))['id__max']
        return self.config.team_class(team_id, config=self.config)

    def get_match_class(self, match_id):
        if match_id == 0:
            match_id = self.config.models.match_model.objects.aggregate(Max('id'))['id__max']
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

    def get_glossary(self):
        return self.config.glossary
