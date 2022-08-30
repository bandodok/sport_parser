from sport_parser.core.data_taking.parser import Parser, TeamData, MatchData, MatchStatus, MatchProtocolsData, \
    ProtocolRequiredStats, ProtocolData, MatchLiveData, MatchLiveProtocolsData
from datetime import datetime
import pytz

from sport_parser.core.models import SeasonModel


class NHLParser(Parser):

    def parse_teams(self, season: SeasonModel) -> list[TeamData]:
        url = f'https://statsapi.web.nhl.com/api/v1/schedule?season={season.external_id}'
        dates_dict = self.get_api_request_content(url)
        dates_list = dates_dict.get('dates')
        games_list = []
        for dates in [date.get('games') for date in dates_list]:
            for game in dates:
                if game.get('gameType') not in ('PR', 'A', 'WA', 'O', 'WCOH_EXH', 'WCOH_PRELIM', 'WCOH_FINAL'):
                    games_list.append(game)

        teams_list = [game.get('teams') for game in games_list]
        team_ids_list = []
        for team in teams_list:
            team_ids_list.append(team['home']['team']['id'])
        team_ids = list(set(team_ids_list))
        return self._parse(self._get_team_data, team_ids, season.id)

    def parse_calendar(self, season: SeasonModel) -> list[MatchData]:
        url = f'https://statsapi.web.nhl.com/api/v1/schedule?season={season.external_id}'
        dates_dict = self.get_api_request_content(url)
        dates_list = dates_dict.get('dates')
        games_list = []
        for dates in [date.get('games') for date in dates_list]:
            games_list.extend([game for game in dates])

        calendar = []
        for game in games_list:

            game_type = game.get('gameType')
            if game_type in ('PR', 'A', 'WA', 'O', 'WCOH_EXH', 'WCOH_PRELIM', 'WCOH_FINAL'):
                continue

            status = MatchStatus.SCHEDULED
            if game['status']['statusCode'] == '9':  # postponed code
                status = MatchStatus.POSTPONED
            elif game['status']['statusCode'] in ('6', '7'):  # finished codes
                status = MatchStatus.FINISHED

            utc = pytz.utc
            naive_date = game.get('gameDate')
            date = datetime.strptime(naive_date, '%Y-%m-%dT%H:%M:%SZ')
            date_utc = utc.localize(date)

            match_data = MatchData(
                id=game.get('gamePk'),
                season_num=season.id,
                date=date_utc,
                home_team_name=game['teams']['home']['team']['name'],
                guest_team_name=game['teams']['away']['team']['name'],
                status=status,
                arena=game['venue']['name']
            )
            calendar.append(match_data)
        return calendar

    def parse_matches_additional_info(self, matches: list[MatchData]):
        return self._parse(self.parse_match_additional_info, matches)

    async def parse_match_additional_info(self, match: MatchData) -> None:
        await self.parse_finished_match(match)

    async def parse_finished_match(self, match: MatchData) -> MatchData:
        url = f'https://statsapi.web.nhl.com/api/v1/game/{match.id}/feed/live'  # 2021010003
        match_dict = await self.get_async_api_response(url)
        if match_dict.get('message') == "Game data couldn't be found":
            return match
        live_data = match_dict.get('liveData')
        linescore = live_data.get('linescore')
        match_status = linescore.get('currentPeriodOrdinal')
        if match_status == 'OT':
            match.overtime = True
        if match_status == 'SO':
            match.penalties = True
        return match

    def is_match_finished(self, match_id: int) -> bool:
        url = f'https://statsapi.web.nhl.com/api/v1/game/{match_id}/feed/live'
        match_dict = self.get_api_request_content(url)
        if match_dict['gameData']['status']['statusCode'] in ('6', '7'):
            return True
        return False

    def parse_protocol(self, match_id: int) -> MatchProtocolsData:
        match_data = self._get_match_data(match_id)

        home_team = match_data['liveData']['boxscore']['teams']['home']['team']['name']
        guest_team = match_data['liveData']['boxscore']['teams']['away']['team']['name']

        # статистика из основного раздела
        stat_dict = {
            'sog': 'shots',
            'penalty': 'pim',
            'blocks': 'blocked',
            'hits': 'hits',
            'faceoff_p': 'faceOffWinPercentage',
            'ppp': 'powerPlayPercentage',
            'ppg': 'powerPlayGoals',
            'takeaways': 'takeaways',
            'giveaways': 'giveaways'
        }
        main_data = self._get_main_data(match_data, stat_dict)

        # счет по периодам
        required_data = self._get_score_by_period(match_data)

        # сбор статистики из всех ивентов матча
        event_data = self._get_events_data(match_data, home_team, guest_team)

        home_protocol = ProtocolData(
            team_name=home_team,
            required_stats=required_data['row_home'],
            additional_stats=main_data['row_home'] | event_data['row_home']
        )
        guest_protocol = ProtocolData(
            team_name=guest_team,
            required_stats=required_data['row_guest'],
            additional_stats=main_data['row_guest'] | event_data['row_guest']
        )
        protocols = MatchProtocolsData(
            match_id=match_id,
            home_protocol=home_protocol,
            guest_protocol=guest_protocol
        )
        return protocols

    def parse_live_match(self, match_id: int) -> MatchLiveData:
        match_data = self._get_match_data(match_id)
        match_status = self._get_match_status(match_data)

        match_live_data = MatchLiveData(
            match_id=match_id,
            status=match_status,
            team1_score=0,
            team2_score=0,
            protocols=MatchLiveProtocolsData(
                home_protocol={},
                guest_protocol={}
            )
        )
        if match_status == 'матч скоро начнется':
            return match_live_data

        home_team = match_data['liveData']['boxscore']['teams']['home']['team']['name']
        guest_team = match_data['liveData']['boxscore']['teams']['away']['team']['name']

        # статистика из основного раздела
        stat_dict = {
            'g': 'goals',
            'sog': 'shots',
            'penalty': 'pim',
            'blocks': 'blocked',
            'hits': 'hits',
            'takeaways': 'takeaways',
            'giveaways': 'giveaways'
        }
        main_data = self._get_main_data(match_data, stat_dict)

        # сбор статистики из всех ивентов матча
        event_data = self._get_events_data(match_data, home_team, guest_team)

        home_protocol = main_data['row_home'] | event_data['row_home']
        guest_protocol = main_data['row_guest'] | event_data['row_guest']

        match_live_data.team1_score = home_protocol.get('g', 0)
        match_live_data.team2_score = guest_protocol.get('g', 0)
        match_live_data.protocols.home_protocol = home_protocol
        match_live_data.protocols.guest_protocol = guest_protocol

        return match_live_data

    def parse_live_protocol(self, match_id):
        match_data = self._get_match_data(match_id)

        match_status = self._get_match_status(match_data)
        if match_status == 'матч скоро начнется':
            return {
                'match_status': match_status,
                'team_1_score': '-',
                'team_2_score': '-',
                'data': {
                    'row_home': '',
                    'row_guest': ''
                }
            }

        home_team = match_data['liveData']['boxscore']['teams']['home']['team']['name']
        guest_team = match_data['liveData']['boxscore']['teams']['away']['team']['name']

        # статистика из основного раздела
        stat_dict = {
            'g': 'goals',
            'sog': 'shots',
            'penalty': 'pim',
            'blocks': 'blocked',
            'hits': 'hits',
            'takeaways': 'takeaways',
            'giveaways': 'giveaways'
        }
        main_data = self._get_main_data(match_data, stat_dict)

        # сбор статистики из всех ивентов матча
        event_data = self._get_events_data(match_data, home_team, guest_team)

        home_protocol = main_data['row_home'] | event_data['row_home']
        guest_protocol = main_data['row_guest'] | event_data['row_guest']

        home_protocol['match_id'] = match_id
        guest_protocol['match_id'] = match_id

        return {
            'match_status': match_status,
            'team_1_score': home_protocol.get('g', 0),
            'team_2_score': guest_protocol.get('g', 0),
            'data': {
                'row_home': home_protocol,
                'row_guest': guest_protocol
            }
        }

    def get_picture(self, team_name: str):
        updated_team_name = team_name.replace(' ', '').lower()
        url = f'https://www.nhl.com/{updated_team_name}'
        soup = self.get_request_content(url)
        img_class1 = 'logo site-footer__team-logo'
        img_class2 = 'site-footer__team-logo'
        img_tag = soup.find('img', class_=img_class1) or soup.find('img', class_=img_class2)
        img = img_tag['src']
        if not img.startswith('http'):
            img = f'https:{img}'
        return img

    async def _get_team_data(self, team_id: str, season_id: int) -> TeamData:
        team_api_url = 'https://statsapi.web.nhl.com/api/v1/teams/'
        url = f'{team_api_url}/{team_id}'
        team_response = await self.get_async_api_response(url)
        team_data = team_response.get('teams')[0]
        name = team_data.get('name')
        print(name)
        return TeamData(
            name=name,
            img=self.get_picture(team_data.get('teamName')),
            city=team_data.get('locationName'),
            arena=team_data.get('venue').get('name'),
            division=team_data.get('division').get('name'),
            conference=team_data.get('conference').get('name'),
            season_num=season_id
        )

    def _get_match_data(self, match_id):
        url = f'https://statsapi.web.nhl.com/api/v1/game/{match_id}/feed/live'  # 2021010003
        return self.get_api_request_content(url)

    @staticmethod
    def _get_match_status(match_data):
        status = match_data['gameData']['status']
        if status['detailedState'] in ('Pre-Game', 'Scheduled'):
            return 'матч скоро начнется'
        if status['detailedState'] in ('In Progress', 'In Progress - Critical'):
            status = match_data['liveData']['linescore']
            if status['currentPeriodTimeRemaining'] == 'END':
                return f"{status['currentPeriod']}-й перерыв"
            if status['currentPeriod'] == 4:
                return 'овертайм'
            if status['currentPeriod'] == 5:
                return 'послематчевые буллиты'
            return f"{status['currentPeriod']}-й период"
        if status['detailedState'] == 'Game Over':
            return 'завершение'
        if status['detailedState'] == 'Final':
            return 'матч завершен'
        return status['detailedState']

    @staticmethod
    def _get_main_data(match_data, stat_dict):
        live_data = match_data.get('liveData')
        boxscore = live_data['boxscore']

        home_stats = boxscore['teams']['home']['teamStats']['teamSkaterStats']
        guest_stats = boxscore['teams']['away']['teamStats']['teamSkaterStats']

        home_protocol = {'team': boxscore['teams']['home']['team']['name']}
        guest_protocol = {'team': boxscore['teams']['away']['team']['name']}

        for model_key, api_key in stat_dict.items():
            home_protocol[model_key] = home_stats[api_key]
            guest_protocol[model_key] = guest_stats[api_key]

        return {
            'row_home': home_protocol,
            'row_guest': guest_protocol
        }

    @staticmethod
    def _get_events_data(match_data, home_team, guest_team):
        plays_data = match_data.get('liveData').get('plays').get('allPlays')

        events = {
            home_team: {},
            guest_team: {}
        }

        for event in plays_data:
            event_name = event['result']['event']
            team = event.get('team')
            if not team:
                continue
            event_team = team.get('name')

            if event_name in events[event_team]:
                events[event_team][event_name] += 1
            else:
                events[event_team][event_name] = 1

        output = []
        for team in (home_team, guest_team):
            output.append({
                'faceoff': events[team].get('Faceoff'),
                'sh': sum((
                    events[team].get('Shot') or 0,
                    events[team].get('Goal') or 0,
                    events[team].get('Blocked Shot') or 0,
                    events[team].get('Missed Shot') or 0
                )),
            })
        return {
            'row_home': output[0],
            'row_guest': output[1],
        }

    @staticmethod
    def _get_score_by_period(match_data) -> dict[str, ProtocolRequiredStats]:
        live_data = match_data.get('liveData')
        linescore = live_data['linescore']

        row_home = {}
        row_guest = {}
        for period in linescore['periods']:
            num = period["num"]
            if num == 4:
                num = 'ot'
            row_home[f'g_{num}'] = period['home']['goals']
            row_guest[f'g_{num}'] = period['away']['goals']

        # +1 гол выигравшему по буллитам
        home_b = linescore.get('shootoutInfo').get('home').get('scores')
        guest_b = linescore.get('shootoutInfo').get('away').get('scores')
        row_home['g_b'] = 0
        row_guest['g_b'] = 0
        if home_b > guest_b:
            row_home['g_b'] += 1
        if home_b < guest_b:
            row_guest['g_b'] += 1

        home_req_stats = ProtocolRequiredStats(
            g_1=row_home.get('g_1', 0),
            g_2=row_home.get('g_2', 0),
            g_3=row_home.get('g_3', 0),
            g_ot=row_home.get('g_ot', 0),
            g_b=row_home.get('g_b', 0),
            g=sum(row_home.values()) - row_home.get('b', 0)
        )
        guest_req_stats = ProtocolRequiredStats(
            g_1=row_guest.get('g_1', 0),
            g_2=row_guest.get('g_2', 0),
            g_3=row_guest.get('g_3', 0),
            g_ot=row_guest.get('g_ot', 0),
            g_b=row_guest.get('g_b', 0),
            g=sum(row_guest.values()) - row_guest.get('b', 0)
        )

        return {
            'row_home': home_req_stats,
            'row_guest': guest_req_stats
        }
