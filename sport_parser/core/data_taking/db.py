from django.db import transaction
from sport_parser.core.models import LiveMatches


class DB:
    def __init__(self, config):
        self.config = config
        self.model_list = config.models
        self.updated_team_names = config.updated_team_names

    def add_team(self, team):
        team_name = self._team_name_update(team['name'])
        season = team['season']
        t, _ = self.model_list.team_model.objects.get_or_create(name=team_name, season=season)

        for arg, value in team.items():
            if arg in ('season', 'name'):
                continue
            t.__dict__[arg] = value

        t.save()

    def add_match(self, match, *, skip_live=False):
        """Добавляет информацию о матче в базу данных"""
        with transaction.atomic():
            a, _ = self.model_list.match_model.objects.get_or_create(
                id=match['match_id'],
            )
            if skip_live and a.status == 'live':
                return
            a.season = match['season']

            for arg, value in match.items():
                if arg in ('season', 'home_team', 'guest_team'):
                    continue
                a.__dict__[arg] = value
            a.save()

            # домашняя команда должна гарантированно добавиться первой
            if match.get('home_team'):
                home_team = self._team_name_update(match.get('home_team'))
                home_team = self.model_list.team_model.objects.filter(season=match['season']).get(name=home_team)
                guest_team = self._team_name_update(match.get('guest_team'))
                guest_team = self.model_list.team_model.objects.filter(season=match['season']).get(name=guest_team)
                a.teams.add(home_team)
                a.save()
                a.teams.add(guest_team)
                a.save()
        return a

    def add_protocol(self, protocol) -> None:
        """Добавляет данные из протокола в базу данных"""
        for row in protocol:
            team = self._team_name_update(row['team'])
            season = self.model_list.match_model.objects.get(id=row['match_id']).season
            p, _ = self.model_list.protocol_model.objects.get_or_create(
                team=self.model_list.team_model.objects.filter(season=season).get(name=team),
                match=self.model_list.match_model.objects.get(id=row['match_id'])
            )

            for arg, value in row.items():
                if arg in ('team', 'match_id'):
                    continue
                p.__dict__[arg] = value
            p.save()

    def update_live_match(self, live_data):
        match = self.model_list.match_model.objects.get(
            id=live_data['match_id']
        )
        match.live_data = live_data
        match.save()

    def remove_live_match(self, match_id):
        live_match = LiveMatches.objects.get(
            league=self.config.name,
            match_id=match_id
        )
        live_match.delete()

    def set_match_status(self, match, status: str) -> None:
        """
        Устанавливает статус матча

        :param match строка базы данных матча
        :param status статус в формате строки
        """
        match = self.model_list.match_model.objects.get(id=match.id)
        match.status = status
        match.save()

    def _team_name_update(self, team):
        if self.updated_team_names.get(team):
            return self.updated_team_names[team]
        return team
