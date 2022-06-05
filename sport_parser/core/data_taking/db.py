from django.db import transaction

from sport_parser.core.data_taking.parser import TeamData, MatchData, MatchProtocolsData, ProtocolData, MatchStatus
from sport_parser.core.models import LiveMatches, MatchModel


class DB:
    def __init__(self, config):
        self.model_list = config.models
        self.updated_team_names = config.updated_team_names

    def add_team(self, team: TeamData) -> None:
        """
        Добавляет информацию о команде в базу данных.

        :param team: информация о команде в формате TeamData
        """
        season = self.model_list.season_model.objects.get(id=team.season_num)
        t, _ = self.model_list.team_model.objects.get_or_create(
            name=self._team_name_update(team.name),
            season=season,
            img=team.img,
            city=team.city,
            arena=team.arena,
            division=team.division,
            conference=team.conference,
        )
        t.save()

    def add_match(self, match: MatchData) -> None:
        """
        Добавляет информацию о матче в базу данных.

        :param match: информация о матче в формате MatchData
        """
        season = self.model_list.season_model.objects.get(id=match.season_num)
        with transaction.atomic():
            m, _ = self.model_list.match_model.objects.get_or_create(
                id=match.id
            )
            m.season = season
            m.status = match.status.value
            m.date = match.date
            m.arena = match.arena
            m.city = match.city
            m.viewers = match.viewers
            m.penalties = match.penalties
            m.overtime = match.overtime

            home_team = self._team_name_update(match.home_team_name)
            home_team = self.model_list.team_model.objects.filter(season=season).get(name=home_team)
            guest_team = self._team_name_update(match.guest_team_name)
            guest_team = self.model_list.team_model.objects.filter(season=season).get(name=guest_team)

            m.home_team = home_team
            m.guest_team = guest_team

            m.teams.add(home_team)
            m.save()
            m.teams.add(guest_team)
            m.save()

    def add_protocol(self, protocol: MatchProtocolsData) -> None:
        """
        Добавляет данные протокола матча в базу данных.

        :param protocol: протокол матча для двух команд в формате MatchProtocolsData
        """
        match = self.model_list.match_model.objects.get(id=protocol.match_id)
        home_protocol = protocol.home_protocol
        guest_protocol = protocol.guest_protocol

        with transaction.atomic():
            self._add_protocol_data(match, home_protocol)
            self._add_protocol_data(match, guest_protocol)

        # очистка данных прямого эфира
        match.live_data = ""
        match.save()

    def get_match_data(self, match_id: int) -> MatchData:
        """
        Возвращает информацию по матчу.

        :param match_id: id матча
        :return: информация по матчу в формате MatchData
        """
        match = self.model_list.match_model.objects.get(id=match_id)
        return MatchData(
            id=match_id,
            season_num=match.season.id,
            date=match.date,
            status=self._get_enum_status(match.status),
            home_team_name=match.home_team.name,
            guest_team_name=match.guest_team.name,
            penalties=match.penalties,
            overtime=match.overtime,
            arena=match.arena,
            city=match.city,
            viewers=match.viewers
        )

    def update_live_match(self, live_data):
        match = self.model_list.match_model.objects.get(
            id=live_data['match_id']
        )
        match.live_data = live_data
        match.save()

    def remove_live_match(self, league: str, match_id: int):
        live_match = LiveMatches.objects.get(
            league=league,
            match_id=match_id
        )
        live_match.delete()

    def set_match_status(self, match_id: int, status: MatchStatus) -> None:
        """
        Устанавливает статус матча

        :param match_id: id матча, которому присваивается статус
        :param status: статус в формате MatchStatus
        """
        match = self.model_list.match_model.objects.get(id=match_id)
        match.status = status.value
        match.save()

    def _add_protocol_data(self, match: MatchModel, protocol: ProtocolData) -> None:
        """
        Добавляет данные протокола матча для одной команды в базу данных.

        :param match: строка матча модели MatchModel
        :param protocol: протокол матча для команды в формате ProtocolData
        """
        team_name = self._team_name_update(protocol.team_name)
        team = self.model_list.team_model.objects.filter(season=match.season).get(name=team_name)

        p, _ = self.model_list.protocol_model.objects.get_or_create(
            team=team,
            match=match
        )

        # обязательные данные
        p.g = protocol.required_stats.g
        p.g_1 = protocol.required_stats.g_1
        p.g_2 = protocol.required_stats.g_2
        p.g_3 = protocol.required_stats.g_3
        p.g_ot = protocol.required_stats.g_ot
        p.g_b = protocol.required_stats.g_b

        # дополнительные данные
        for arg, value in protocol.additional_stats.items():
            p.__dict__[arg] = value

        p.save()

    @staticmethod
    def _get_enum_status(status: str) -> MatchStatus:
        enum_str_status = status.upper().replace(' ', '_')
        return MatchStatus[enum_str_status]

    def _team_name_update(self, team):
        if self.updated_team_names.get(team):
            return self.updated_team_names[team]
        return team
