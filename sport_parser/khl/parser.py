import datetime
import tempfile
import pytz
import requests
from bs4 import BeautifulSoup

from sport_parser.core.exceptions import UnableToGetProtocolException

from sport_parser.core.data_taking.parser import Parser, TeamData, MatchData, MatchStatus, MatchProtocolsData, \
    ProtocolRequiredStats, ProtocolData, MatchLiveData, MatchLiveProtocolsData
from sport_parser.core.models import SeasonModel


class KHLParser(Parser):

    def parse_teams(self, season: SeasonModel) -> list[TeamData]:
        """
        Парсит информацию о командах сезона

        :param season: строка сезона модели SeasonModel
        :return: список информации по командам в формате TeamData
        """
        url = f'https://www.khl.ru/standings/{season.external_id}/division/'
        soup = self.get_request_content(url)
        divisions = soup.find('div', id='tab-standings-division').find_all('div', class_='k-data_table')
        teams = []
        d_c = {
            'Боброва': 'Запад',
            'Тарасова': 'Запад',
            'Харламова': 'Восток',
            'Чернышева': 'Восток',
        }
        for division_soup, division, conference in zip(divisions, d_c.keys(), d_c.values()):
            teams.extend(self._get_division_team_list(division_soup, division, conference, season.id))
        return teams

    def parse_calendar(self, season: SeasonModel) -> list[MatchData]:
        """
        Парсит основную информацию о матчах сезона

        :param season: строка сезона модели SeasonModel
        :return: список информации по матчам сезона в формате MatchData
        """
        output = []

        regular_url = f'https://www.khl.ru/calendar/{season.external_id}/00/'
        playoff_url = f'https://www.khl.ru/calendar/{season.external_id + 1}/00/'
        regular_soup = self._calendar_request_content(regular_url)
        playoff_soup = self._calendar_request_content(playoff_url)

        dates, matches = self._get_dates_and_matches(regular_soup)

        if playoff_soup != 'redirected':
            playoff_dates, playoff_matches = self._get_dates_and_matches(playoff_soup)
            dates = [*dates, *playoff_dates]
            matches = [*matches, *playoff_matches]

        match_dict = {}
        for date, match_soup in zip(dates, matches):
            if date in match_dict:
                date = f'{date}_1'
            match_dict[date] = match_soup

        for date, matches in match_dict.items():
            if date.endswith('_1'):
                date = date[:-2]

            match_list = matches.find_all('li', class_='b-wide_tile_item')

            # определение даты
            string_date = self._date_format(date)
            msk = pytz.timezone('Europe/Moscow')
            date = datetime.datetime.strptime(string_date, '%Y-%m-%d')
            date_msk = msk.localize(date)

            for match in match_list:
                href = match.find('dl', class_='b-title-option').div.div.ul.li.a['href']
                match_id = href.split('/')[3]
                # у матчей дивизиона нет ссылок на страницу команды
                home_team_a = match.find('dl', class_='b-details m-club').dd.h5.a
                if not home_team_a:
                    continue
                home_team = home_team_a.text
                guest_team = match.find('dl', class_='b-details m-club m-rightward').dd.h5.a.text

                # определение статуса
                score = match.find('dl', class_='b-score')
                if '+' in score.dt.h3.text:
                    status = MatchStatus.POSTPONED
                elif '—' in score.dt.h3.text:
                    status = MatchStatus.FINISHED
                else:
                    status = MatchStatus.SCHEDULED

                match_data = MatchData(
                    id=match_id,
                    season_num=season.id,
                    date=date_msk,
                    home_team_name=home_team,
                    guest_team_name=guest_team,
                    status=status
                )

                # в кхл если матч запланирован, то у него можно узнать точное время игры и город
                if status == MatchStatus.SCHEDULED:
                    time = score.dt.h3.text.split(' ')[0]
                    hours, minutes = time.split(':')
                    timedelta = datetime.timedelta(hours=int(hours), minutes=int(minutes))
                    city = score.dd.p.text

                    match_data.date = date_msk + timedelta
                    match_data.city = city

                output.append(match_data)
        return output

    def parse_match_additional_info(self, match: MatchData) -> None:
        self.parse_finished_match(match)

    def parse_finished_match(self, match: MatchData) -> MatchData:
        url = f'https://text.khl.ru/text/{match.id}.html'
        soup = self.get_request_content(url)

        extra_info = soup.find_all('li', class_="b-match_add_info_item")
        if not extra_info:
            return match

        match_status = soup.find('dd', class_="b-period_score").text
        if match_status != 'матч завершен':
            return match

        # определение, были ли буллиты или овертайм
        score_status = soup.find('dt', class_="b-total_score").h3
        if 'Б' in score_status.text:
            match.penalties = True
        if 'ОТ' in score_status.text:
            match.overtime = True

        # обновление времени игры
        date_info = extra_info[0]
        info = date_info.find_all('span')[1]
        info = str(info).split('<br/>')
        time = info[1][:5]
        hours, minutes = time.split(':')
        msk_delta = datetime.timedelta(hours=3)
        date = match.date + msk_delta
        new_date = datetime.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=int(hours),
            minute=int(minutes)
        )
        msk = pytz.timezone('Europe/Moscow')
        match.date = msk.localize(new_date)

        # обновление информации о месте проведения игры
        arena_info = extra_info[1]
        info = arena_info.find_all('span')[1]

        info = str(info).split('<br/>')
        arena_city = info[0][6:]
        arena, city = arena_city.split('(')
        arena = arena[:-1]
        city = city[:-1]
        city = city.strip()
        match.arena = arena
        match.city = city

        if info[1] != '</span>':
            match.viewers = info[1][:-16]

        return match

    def is_match_finished(self, match_id: int) -> bool:
        url = f'https://text.khl.ru/text/{match_id}.html'
        soup = self.get_request_content(url)

        extra_info = soup.find_all('li', class_="b-match_add_info_item")
        if not extra_info:
            return False

        match_status = soup.find('dd', class_="b-period_score").text
        if match_status == 'матч завершен':
            return True
        return False

    def parse_protocol(self, match_id: int) -> MatchProtocolsData:
        """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
        url = f"https://text.khl.ru/text/{match_id}.html"
        soup = self.get_request_content(url)
        match_status = self._get_match_status(soup)
        if match_status != 'матч завершен':
            raise UnableToGetProtocolException

        # из текстовой трансляции берется количество бросков и голы по периодам
        text_broadcast_data = self._get_text_broadcast_stats(soup)

        # сборка обязательных данных
        g_home = text_broadcast_data['g_home']
        g_guest = text_broadcast_data['g_guest']

        home_req_stats = ProtocolRequiredStats(
            g_1=g_home.get('p1', 0),
            g_2=g_home.get('p2', 0),
            g_3=g_home.get('p3', 0),
            g_ot=g_home.get('ot', 0),
            g_b=g_home.get('b', 0),
            g=sum(g_home.values())
        )
        guest_req_stats = ProtocolRequiredStats(
            g_1=g_guest.get('p1', 0),
            g_2=g_guest.get('p2', 0),
            g_3=g_guest.get('p3', 0),
            g_ot=g_guest.get('ot', 0),
            g_b=g_guest.get('b', 0),
            g=sum(g_guest.values())
        )

        # сборка дополнительных данных
        stat_dict = {
            'Команда': 'team',
            'Ш': 'g',
            'БВ': 'sog',
            'Штр': 'penalty',
            'ВВбр': 'faceoff',
            '%ВВбр': 'faceoff_p',
            'БлБ': 'blocks',
            'СПр': 'hits',
            'ФоП': 'fop',
            'ВВА': 'time_a',
            'ВВШ': 'vvsh',
            'НВШ': 'nshv',
            'ПД': 'pd'
        }
        additional_data = self._get_additional_stats(soup, stat_dict)
        home_add_stats = additional_data['row_home']
        guest_add_stats = additional_data['row_guest']
        home_add_stats['sh'] = text_broadcast_data['sh_home']
        guest_add_stats['sh'] = text_broadcast_data['sh_guest']

        home_team_name = home_add_stats.pop('team')
        guest_team_name = guest_add_stats.pop('team')

        return MatchProtocolsData(
            match_id=match_id,
            home_protocol=ProtocolData(
                team_name=home_team_name,
                required_stats=home_req_stats,
                additional_stats=home_add_stats
            ),
            guest_protocol=ProtocolData(
                team_name=guest_team_name,
                required_stats=guest_req_stats,
                additional_stats=guest_add_stats
            )
        )

    def parse_live_match(self, match_id: int) -> MatchLiveData:
        url = f'https://text.khl.ru/text/{match_id}.html'
        soup = self.get_request_content(url)
        match_status = self._get_match_status(soup)

        match_data = MatchLiveData(
            match_id=match_id,
            status=match_status,
            team1_score=0,
            team2_score=0,
            protocols=MatchLiveProtocolsData(
                home_protocol={},
                guest_protocol={}
            )
        )

        if match_status in ('матч скоро начнется', 'status not found', 'подготовка'):
            match_data.status = 'матч скоро начнется'
            return match_data

        if match_status != 'подготовка' and match_status != 'status not found':
            stat_dict = {
                'Команда': 'team',
                'Ш': 'g',
                'БВ': 'sog',
                'Штр': 'penalty',
                'ВВбр': 'faceoff',
                '%ВВбр': 'faceoff_p',
                'БлБ': 'blocks',
                'СПр': 'hits',
                'ФоП': 'fop',
                'ВВА': 'time_a',
            }
            main_data = self._get_additional_stats(soup, stat_dict)

            match_data.team1_score = main_data['row_home'].get('g', 0)
            match_data.team2_score = main_data['row_guest'].get('g', 0)
            match_data.protocols.home_protocol = main_data['row_home']
            match_data.protocols.guest_protocol = main_data['row_home']

        return match_data

    def parse_live_protocol(self, match_id):
        url = f"https://text.khl.ru/text/{match_id}.html"
        soup = self.get_request_content(url)

        match_status = self._get_match_status(soup)
        if match_status in ('матч скоро начнется', 'status not found', 'подготовка'):
            return {
                'match_status': 'матч скоро начнется',
                'team_1_score': '-',
                'team_2_score': '-',
                'data': {
                    'row_home': '',
                    'row_guest': ''
                }
            }

        row_home = {}
        row_guest = {}

        if match_status != 'подготовка' and match_status != 'status not found':
            stat_dict = {
                'Команда': 'team',
                'Ш': 'g',
                'БВ': 'sog',
                'Штр': 'penalty',
                'ВВбр': 'faceoff',
                '%ВВбр': 'faceoff_p',
                'БлБ': 'blocks',
                'СПр': 'hits',
                'ФоП': 'fop',
                'ВВА': 'time_a',
            }
            main_data = self._get_additional_stats(soup, stat_dict)
            row_home = main_data['row_home']
            row_guest = main_data['row_guest']

        return {
            'match_status': match_status,
            'team_1_score': row_home.get('g', 0),
            'team_2_score': row_guest.get('g', 0),
            'data': {
                'row_home': row_home,
                'row_guest': row_guest
            }
        }

    @staticmethod
    def _get_match_status(soup):
        match_status = soup.find('dd', class_="b-period_score")
        if not match_status:
            return 'status not found'
        return match_status.text

    @staticmethod
    def _get_text_broadcast_stats(soup):
        """Возвращает количество голов и всего бросков по периодам из текстовой трансляции"""
        text_stats = soup.find_all('p', class_='e-action_txt')

        match_stats = {}
        for stats in text_stats:
            if 'Статистика матча:' in stats.text or 'Game stats:' in stats.text:
                if match_stats.get('match'):
                    continue
                match_stats['match'] = stats.text
            if 'Статистика 1-го периода:' in stats.text or 'Stats of 1st period:' in stats.text:
                match_stats['p1'] = stats.text
            if 'Статистика 2-го периода:' in stats.text or 'Stats of 2nd period:' in stats.text:
                match_stats['p2'] = stats.text
            if 'Статистика 3-го периода:' in stats.text or 'Stats of 3rd period:' in stats.text:
                match_stats['p3'] = stats.text
            if 'Статистика овертайма:' in stats.text or 'Stats of overtime:' in stats.text:
                match_stats['ot'] = stats.text

        sh_home = 0
        sh_guest = 0
        g_home = {'b': 0}
        g_guest = {'b': 0}

        score_status = soup.find('dt', class_="b-total_score").h3
        if 'Б' in score_status.text:
            score = score_status.text.split('–')
            score[0] = int(score[0])
            score[1] = int(score[1][:-1])
            if score[0] > score[1]:
                g_home['b'] = 1
                g_guest['b'] = 0
            else:
                g_home['b'] = 0
                g_guest['b'] = 1

        if not match_stats.get('p1') or not match_stats.get('p2') or not match_stats.get('p3'):
            sh_home = match_stats['match'].split(':')[2].split('-')[0].strip()
            sh_guest = match_stats['match'].split(':')[2].split('-')[1].split(' ')[0]
        else:
            for key, value in match_stats.items():
                if key == 'match':
                    continue
                sh_home += int(value.split(';')[0].strip().split(' ').pop().split('-')[0])
                sh_guest += int(value.split(';')[0].strip().split(' ').pop().split('-')[1])
                g_home[key] = int(value.split(';')[2].strip().split(' ').pop().split('-')[0])
                g_guest[key] = int(value.split(';')[2].strip().split(' ').pop().split('-')[1])

        return {
            'sh_home': sh_home,
            'sh_guest': sh_guest,
            'g_home': g_home,
            'g_guest': g_guest,
        }

    def _get_additional_stats(self, soup, stat_dict: dict[str, str]):
        """Возвращает статистику из основной таблицы"""
        team_stats = soup.find_all('div', class_="table-responsive")
        head = [x.find_all('th') for x in team_stats][0]
        body = [x.find_all('td') for x in team_stats][0]
        columns = [i.text.strip() for i in head]
        rows = [i.text.strip() for i in body]

        # находим индекс объединенной ячейки чтобы дублировать его во вторую строку
        rowspan = {body.index(i): i.text.strip() for i in body if i.attrs == {'rowspan': '2'}}
        for k, v in rowspan.items():
            len_ = int((len(rows) + 1) / 2)
            rows.insert((k + len_), v)

        row_home = {stat_dict[stat]: value for stat, value in zip(columns, rows) if stat in stat_dict}
        row_guest = {stat_dict[stat]: value for stat, value in zip(columns, rows[len(columns):]) if stat in stat_dict}

        return {
            'row_home': self._row_update_type(row_home),
            'row_guest': self._row_update_type(row_guest)
        }

    @staticmethod
    def _row_update_type(row):
        """Приводит некорректные типы данных в протоколах к корректному
        для восприятия базой данных"""
        for stat, value in row.items():
            if stat in ('time_a', 'vvsh', 'nshv'):
                if value == "":
                    row[stat] = '00:00:00'
                else:
                    row[stat] = f'00:{value}'
            elif not value:
                row[stat] = 0
        return row

    def _get_division_team_list(self, division_soup, division, conference, season) -> list[TeamData]:
        """Возвращает список информации о командах дивизиона"""
        teams = []
        for team in division_soup.find_all('a'):
            team_src = f"https://www.khl.ru{team['href']}arena/"
            soup = self.get_request_content(team_src)
            city_table = soup.find('div', class_='b-blocks_cover')

            name = team.text
            img = f"https://www.khl.ru{city_table.find('img')['src']}"
            city = city_table.find('p').text
            arena = soup.find_all('div', class_='b-short_block').pop().find('h4').text

            teams.append(TeamData(
                name=name,
                img=img,
                city=city,
                arena=arena,
                division=division,
                conference=conference,
                season_num=season
            ))

        return teams

    @staticmethod
    def _calendar_request_content(url):
        r = requests.get(url, allow_redirects=False)
        if r.status_code == 301:
            return 'redirected'
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(f'{tmpdirname}/file1.txt', 'w', encoding='utf-8') as f:
                a = r.text.replace('<!--div align="center" style="margin-top: 1em;">', ' ')
                f.write(a)
            with open(f'{tmpdirname}/file1.txt', 'rb') as f:
                soup = BeautifulSoup(f, 'html.parser')
            return soup

    @staticmethod
    def _get_dates_and_matches(soup: BeautifulSoup) -> tuple[list, list[BeautifulSoup]]:
        match_soup = soup.find('div', id='tab-calendar-all')
        if not match_soup:
            match_soup = soup.find('div', id='tab-calendar-last')
        if not match_soup:
            match_soup = soup.find('div', id='tab-calendar-future')

        dates = match_soup.find_all('div', class_='b-final_cup_date')
        dates = [date.b.text for date in dates]

        matches = match_soup.find_all('div', class_='m-future')
        return dates, matches

    def _date_format(self, date):
        if ', ' in date:
            date = date.split(',')[0]
        splitted_date = date.split(' ')
        if not splitted_date[0]:
            splitted_date.pop(0)
        day, month, year = splitted_date
        if len(day) == 1:
            day = f'0{day}'
        month = self._month_to_int_replace(month)
        return f'{year}-{month}-{day}'

    @staticmethod
    def _month_to_int_replace(month: str):
        """Возвращает номер месяца по слову"""
        months = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        return months.get(month)
