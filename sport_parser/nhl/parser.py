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
        url = f'https://statsapi.web.nhl.com/api/v1/game/{match.id}/feed/live'  # 2021010003

        match_data = self.get_api_request_content(url)
        live_data = match_data.get('liveData')
        plays_data = match_data.get('liveData').get('plays').get('allPlays')

        boxscore = live_data['boxscore']
        home_stats = boxscore['teams']['home']['teamStats']['teamSkaterStats']
        guest_stats = boxscore['teams']['away']['teamStats']['teamSkaterStats']

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

        home_protocol = {
            'team': boxscore['teams']['home']['team']['name'],
            'match_id': match.id,
            'g_b': 0,
        }
        guest_protocol = {
            'team': boxscore['teams']['away']['team']['name'],
            'match_id': match.id,
            'g_b': 0,
        }

        for model_key, api_key in stat_dict.items():
            home_protocol[model_key] = home_stats[api_key]
            guest_protocol[model_key] = guest_stats[api_key]

        linescore = live_data['linescore']

        # счет по периодам
        for period in linescore['periods']:
            num = period["num"]
            if num == 4:
                num = 'ot'
            home_protocol[f'g_{num}'] = period['home']['goals']
            guest_protocol[f'g_{num}'] = period['away']['goals']

        # +1 гол выигравшему по буллитам
        home_b = linescore.get('shootoutInfo').get('home').get('scores')
        guest_b = linescore.get('shootoutInfo').get('away').get('scores')
        if home_b > guest_b:
            home_protocol['g_b'] += 1
        if home_b < guest_b:
            guest_protocol['g_b'] += 1

        # сбор статистики из всех ивентов матча
        events = {
            'home': {},
            'guest': {}
        }

        for event in plays_data:
            event_name = event['result']['event']
            team = event.get('team')
            if not team:
                continue
            team = team.get('name')

            if team == home_protocol['team']:
                event_team = 'home'
            elif team == guest_protocol['team']:
                event_team = 'guest'
            else:
                event_team = 'unknown'

            if event_name in events[event_team]:
                events[event_team][event_name] += 1
            else:
                events[event_team][event_name] = 1

        home_protocol.update({
            'faceoff': events['home'].get('Faceoff'),
            'sh': sum((
                events['home'].get('Shot') or 0,
                events['home'].get('Goal') or 0,
                events['home'].get('Blocked Shot') or 0,
                events['home'].get('Missed Shot') or 0
            )),
        })
        guest_protocol.update({
            'faceoff': events['guest'].get('Faceoff'),
            'sh': sum((
                events['guest'].get('Shot') or 0,
                events['guest'].get('Goal') or 0,
                events['guest'].get('Blocked Shot') or 0,
                events['guest'].get('Missed Shot') or 0
            )),
        })

        return home_protocol, guest_protocol

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
