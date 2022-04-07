from sport_parser.core.data_taking.parser import Parser
from datetime import datetime
import pytz


class NHLParser(Parser):

    def parse_teams(self, season):
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

        team_ids = set(team_ids_list)
        team_api_url = 'https://statsapi.web.nhl.com/api/v1/teams/'

        teams = []
        for team in team_ids:
            team_url = f'{team_api_url}{team}'
            team_response = self.get_api_request_content(team_url).get('teams')[0]
            teams.append({
                'api_id': team,
                'name': team_response.get('name'),
                'short_name': team_response.get('teamName'),
                'abbreviation': team_response.get('abbreviation'),
                'season': season,
                'arena': team_response.get('venue').get('name'),
                'city': team_response.get('locationName'),
                'division': team_response.get('division').get('name'),
                'conference': team_response.get('conference').get('name'),
                'img': self.get_picture(team_response.get('teamName')),
            })
        return teams

    def parse_calendar(self, season, *, webdriver=None):
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

            match_type = 'unknown'
            if game_type == 'R':
                match_type = 'Regular season'
            if game_type == 'P':
                match_type = 'Playoffs'

            status = 'scheduled'
            if game['status']['statusCode'] == '9':  # postponed code
                status = 'postponed'
            elif game['status']['statusCode'] == '7':  # finished code
                status = 'finished'

            utc = pytz.utc
            naive_date = game.get('gameDate')
            date = datetime.strptime(naive_date, '%Y-%m-%dT%H:%M:%SZ')
            date_utc = utc.localize(date)

            match_info = {
                'match_id': game.get('gamePk'),
                'match_type': match_type,
                'date': date_utc,
                'home_team': game['teams']['home']['team']['name'],
                'guest_team': game['teams']['away']['team']['name'],
                'season': season,
                'status': status,
                'arena': game['venue']['name'],
            }
            calendar.append(match_info)
        return calendar

    def parse_match(self, match):
        url = f'https://statsapi.web.nhl.com/api/v1/game/{match.id}/feed/live'  # 2021010003
        match_dict = self.get_api_request_content(url)

        status_code = match_dict.get('gameData').get('status').get('statusCode')
        linescore = match_dict.get('liveData').get('linescore')

        match_data = self._parse_finished_match(match, linescore)
        if status_code == '9':  # postponed code
            match_data['status'] = 'postponed'
        elif status_code == '7':  # finished code
            match_data['status'] = 'finished'
        else:
            match_data['status'] = 'scheduled'

        return match_data

    def _parse_finished_match(self, match, linescore):
        match_status = linescore.get('currentPeriodOrdinal')
        overtime = False
        penalties = False
        if match_status == 'OT':
            overtime = True
        if match_status == 'SO':
            penalties = True

        match_info = {
            'match_id': match.id,
            'season': match.season,
            'overtime': overtime,
            'penalties': penalties,
        }
        return match_info

    def parse_protocol(self, match):
        match_data = self._get_match_data(match.id)

        home_team = match_data['liveData']['boxscore']['teams']['home']['team']['name']
        guest_team = match_data['liveData']['boxscore']['teams']['away']['team']['name']

        # статистика из основного раздела
        stat_dict = {
            'g': 'goals',
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
        periods_data = self._get_score_by_period(match_data)

        # сбор статистики из всех ивентов матча
        event_data = self._get_events_data(match_data, home_team, guest_team)

        home_protocol = main_data['row_home'] | periods_data['row_home'] | event_data['row_home']
        guest_protocol = main_data['row_guest'] | periods_data['row_guest'] | event_data['row_guest']

        home_protocol['match_id'] = match.id
        guest_protocol['match_id'] = match.id

        return home_protocol, guest_protocol

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
    def _get_score_by_period(match_data):
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

        return {
            'row_home': row_home,
            'row_guest': row_guest
        }
