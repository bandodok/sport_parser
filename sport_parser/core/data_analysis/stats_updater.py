from sport_parser.core.data_analysis.bar_stats import BarStats
from sport_parser.core.data_analysis.chart_stats import ChartStats
from sport_parser.core.data_analysis.table_stats import TableStats
from sport_parser.core.data_taking.db import DB
from sport_parser.core.exceptions import UnableToCalculateBarStats


class StatsUpdater:
    """
    Класс для обработки статистики.
    Сохраняет списки сезонов, матчей и команд, для которых необходимо обновить статистику, затем выполняет обновление.

    :param db: экземпляр класса DB для взаимодействия с базой данных.
    :param table_stats: экземпляр класса TableStats для расчета табличной статистики.
    :param chart_stats: экземпляр класса ChartStats для расчета графиков.
    :param bar_stats: экземпляр класса BarStats для расчета статистики в виде полос.
    """

    db: DB
    table_stats: TableStats
    chart_stats: ChartStats
    bar_stats: BarStats

    _seasons_to_update: set[int]
    _teams_to_update: set[int]
    _matches_to_update: set[int]

    def __init__(self, db: DB, table_stats: TableStats, chart_stats: ChartStats, bar_stats: BarStats):
        self.table_stats = table_stats
        self.chart_stats = chart_stats
        self.bar_stats = bar_stats
        self.db = db

        self._seasons_to_update = set()
        self._teams_to_update = set()
        self._matches_to_update = set()

    def update(self) -> None:
        """Выполняет обновление статистики для всех сохраненных сезонов, матчей и команд."""
        self._update_seasons()
        self._update_teams()
        self._update_matches()

    def add_season(self, season_id: int) -> None:
        """
        Добавляет сезон в список к обновлению.

        :param season_id: id сезона
        """
        self._seasons_to_update.add(season_id)

    def add_team(self, team_id: int) -> None:
        """
        Добавляет команду в список к обновлению.

        :param team_id: id команды
        """
        self._teams_to_update.add(team_id)

    def add_match(self, match_id: int) -> None:
        """
        Добавляет матч в список к обновлению.

        :param match_id: id матча
        """
        self._matches_to_update.add(match_id)

    def _update_seasons(self):
        """Рассчитывает статистику для сезонов и сохраняет ее в базу данных."""
        for season in self._seasons_to_update:
            table_stats = self._calculate_season_table_stats(season)
            self.db.set_season_table_stats(season, table_stats)

    def _update_teams(self):
        """Рассчитывает статистику для команд и добавляет ее в базу данных."""
        for team in self._teams_to_update:
            chart_stats = self._calculate_team_chart_stats(team)
            self.db.set_team_chart_stats(team, chart_stats)

    def _update_matches(self):
        """Рассчитывает статистику для матчей и добавляет ее в базу данных."""
        for match in self._matches_to_update:
            table_stats = self._calculate_match_table_stats(match)
            chart_stats = self._calculate_match_chart_stats(match)
            self.db.set_match_table_stats(match, table_stats)
            self.db.set_match_chart_stats(match, chart_stats)

            # если матч не завершен, статистика в виде полос не рассчитывается
            try:
                bar_stats = self._calculate_match_bar_stats(match)
                self.db.set_match_bar_stats(match, bar_stats)
            except UnableToCalculateBarStats:
                continue

    def _calculate_season_table_stats(self, season_id: int):
        season = self.db.get_season(season_id)
        return self.table_stats.season_stats_calculate(season)

    def _calculate_match_table_stats(self, match_id: int):
        match = self.db.get_match(match_id)
        return self.table_stats.match_stats_calculate(match)

    def _calculate_team_chart_stats(self, team_id: int):
        team = self.db.get_team(team_id)
        return self.chart_stats.team_stats_calculate(team)

    def _calculate_match_chart_stats(self, match_id: int):
        match = self.db.get_match(match_id)
        return self.chart_stats.match_stats_calculate(match)

    def _calculate_match_bar_stats(self, match_id: int):
        match = self.db.get_match(match_id)
        return self.bar_stats.match_stats_calculate(match)
