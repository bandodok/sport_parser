import datetime
import pytz
import re
import asyncio
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
        divisions = [soup.find('tbody', id=f'standings_content_{num}') for num in (3, 4, 5, 6)]
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
        regular_soup = self.get_request_content(regular_url)
        playoff_soup = self.get_request_content(playoff_url)

        regular_matches_grouped_by_date = regular_soup.find_all('div', class_='calendary-body__item')
        playoff_matches_grouped_by_date = playoff_soup.find_all('div', class_='calendary-body__item')
        matches_grouped_by_date = [*regular_matches_grouped_by_date, *playoff_matches_grouped_by_date]

        for day_matches in matches_grouped_by_date:
            match_list = day_matches.find_all('div', class_='card-game')

            # определение даты
            date = day_matches.find('time').text.strip()
            string_date = self._date_format(date)
            msk = pytz.timezone('Europe/Moscow')
            date = datetime.datetime.strptime(string_date, '%Y-%m-%d')
            date_msk = msk.localize(date)

            for match in match_list:
                href = match.div.a['href']
                match_id = int(href.split('/')[3])
                # у матчей дивизиона нет ссылок на страницу команды
                home_team_a = match.find('a', class_='card-game__club card-game__club_left')
                try:
                    home_team_a['href']
                except KeyError:
                    continue

                home_team = home_team_a.p.text.strip()
                guest_team = match.find('a', class_='card-game__club card-game__club_right').p.text.strip()

                # определение статуса
                time = match.find('p', class_='card-game__center-time')
                if time:
                    status = MatchStatus.SCHEDULED
                else:
                    home_team_score = match.find('span', class_='card-game__center-score-left').text.strip()
                    if home_team_score == '+':
                        status = MatchStatus.POSTPONED
                    else:
                        status = MatchStatus.FINISHED

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
                    _small_text = time.small.text
                    time = time.text.replace(_small_text, '').strip()
                    hours, minutes = time.split(':')
                    timedelta = datetime.timedelta(hours=int(hours), minutes=int(minutes))
                    city = match.find('p', class_='card-game__club-position').text.strip()

                    match_data.date = date_msk + timedelta
                    match_data.city = city

                output.append(match_data)
        return output

    def parse_matches_additional_info(self, matches: list[MatchData]):
        return self._parse(self.parse_match_additional_info, matches)

    async def parse_match_additional_info(self, match: MatchData) -> None:
        await self.async_parse_finished_match(match)

    def parse_finished_match(self, match: MatchData) -> MatchData:
        return asyncio.run(self.async_parse_finished_match(match))

    async def async_parse_finished_match(self, match: MatchData) -> MatchData:
        url = f'https://text.khl.ru/text/{match.id}.html'
        soup = await self.get_async_response(url)

        parser = _get_parser(soup)
        if not parser:
            return match

        match_status = parser.get_status()
        if match_status != 'матч завершен':
            return match

        match.penalties = parser.have_penalties()
        match.overtime = parser.have_overtime()
        match.date = parser.update_date(match.date)
        match.city = parser.get_city()
        match.arena = parser.get_arena()
        match.viewers = parser.get_viewers()

        return match

    def is_match_finished(self, match_id: int) -> bool:
        url = f'https://text.khl.ru/text/{match_id}.html'
        soup = self.get_request_content(url)

        parser = _get_parser(soup)
        if not parser:
            return False

        match_status = parser.get_status()
        return match_status == 'матч завершен'

    def parse_protocol(self, match_id: int) -> MatchProtocolsData:
        """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
        url = f"https://text.khl.ru/text/{match_id}.html"
        soup = self.get_request_content(url)
        parser = _get_parser(soup)

        match_status = parser.get_status()
        if match_status != 'матч завершен':
            raise UnableToGetProtocolException

        # из текстовой трансляции берется количество бросков и голы по периодам
        text_broadcast_data = parser.get_text_broadcast_stats()

        # сборка обязательных данных
        g_home = self._row_update_type(text_broadcast_data['g_home'])
        g_guest = self._row_update_type(text_broadcast_data['g_guest'])

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
        additional_data = parser.get_additional_stats(stat_dict)
        home_add_stats = self._row_update_type(additional_data['row_home'])
        guest_add_stats = self._row_update_type(additional_data['row_guest'])
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
        parser = _get_parser(soup)

        match_status = parser.get_status()

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
            main_data = parser.get_additional_stats(stat_dict)
            home_stats = self._row_update_type(main_data['row_home'])
            guest_stats = self._row_update_type(main_data['row_guest'])

            match_data.team1_score = home_stats.get('g', 0)
            match_data.team2_score = guest_stats.get('g', 0)
            match_data.protocols.home_protocol = home_stats
            match_data.protocols.guest_protocol = guest_stats

        return match_data

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

            name_city = soup.find('div', class_='infoclub-club__info').find_all('p')
            name = name_city[0].text.strip()
            city = name_city[1].text.strip()
            if name == 'Динамо':
                if city == 'Москва':
                    name = 'Динамо М'
                if city == 'Минск':
                    name = 'Динамо Мн'
                if city == 'Рига':
                    name = 'Динамо Р'
            img = f"https://www.khl.ru{soup.find('img', class_='infoclub-club__logo-img')['src']}"
            arena = ''
            arena_info = soup.find('div', class_='arena-info__header')
            if arena_info:
                arena = arena_info.find('h2').text.strip()

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


class _LocalParser:
    _soup: BeautifulSoup

    def __init__(self, soup):
        self._soup = soup

    def get_status(self) -> str:
        pass

    def get_arena(self) -> str:
        pass

    def get_city(self) -> str:
        pass

    def get_text_broadcast_stats(self) -> dict[str, int | dict[str, int]]:
        pass

    def get_additional_stats(self, stat_dict: dict[str, str]) -> dict[str, dict]:
        pass

    def update_date(self, date: datetime.datetime) -> datetime:
        pass

    def get_viewers(self) -> int:
        pass

    def have_penalties(self) -> bool:
        pass

    def have_overtime(self) -> bool:
        pass

    @staticmethod
    def _get_stats_by_period(text_stats) -> dict:
        match_stats = {}
        for stats in text_stats:
            if 'Статистика матча:' in stats.text or 'Game stats:' in stats.text:
                if match_stats.get('match'):
                    continue
                match_stats['match'] = stats.text
            if 'Статистика 1-го периода:' in stats.text or 'Stats of 1st period:' in stats.text:
                if match_stats.get('p1'):
                    continue
                match_stats['p1'] = stats.text
            if 'Статистика 2-го периода:' in stats.text or 'Stats of 2nd period:' in stats.text:
                if match_stats.get('p2'):
                    continue
                match_stats['p2'] = stats.text
            if 'Статистика 3-го периода:' in stats.text or 'Stats of 3rd period:' in stats.text:
                if match_stats.get('p3'):
                    continue
                match_stats['p3'] = stats.text
            if 'Статистика овертайма:' in stats.text or 'Stats of overtime:' in stats.text:
                if match_stats.get('ot'):
                    continue
                match_stats['ot'] = stats.text
        return match_stats

    @staticmethod
    def _parse_stats_by_period(match_stats) -> dict:
        """Обрабатывает статистику из текстовой трансляции"""
        sh_home = 0
        sh_guest = 0
        g_home = {'b': 0}
        g_guest = {'b': 0}

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

    @staticmethod
    def _parse_table_stats(head, body, stat_dict) -> dict:
        """Обрабатывает статистику из основной таблицы"""
        columns = [i.text.strip() for i in head]
        rows = [i.text.strip() for i in body]

        # находим индекс объединенной ячейки, чтобы дублировать значение во вторую строку
        rowspan = {body.index(i): i.text.strip() for i in body if i.attrs == {'rowspan': '2'}}
        for k, v in rowspan.items():
            len_ = int((len(rows) + 1) / 2)
            rows.insert((k + len_), v)

        row_home = {stat_dict[stat]: value for stat, value in zip(columns, rows) if stat in stat_dict}
        row_guest = {stat_dict[stat]: value for stat, value in zip(columns, rows[len(columns):]) if stat in stat_dict}

        return {
            'row_home': row_home,
            'row_guest': row_guest
        }


class _NewDesignParser(_LocalParser):

    def get_status(self) -> str:
        return self._soup.find('p', class_='preview-frame__center-text').text.strip()

    def get_arena(self) -> str:
        card_infos = self._soup.find('div', class_='card-infos')
        arena_city_viewers_infos = card_infos.find_all('div', class_='card-infos__item-info')[1]
        arena = arena_city_viewers_infos.find_all()[0]
        return arena.text.strip()

    def get_city(self) -> str:
        card_infos = self._soup.find('div', class_='card-infos')
        arena_city_viewers_infos = card_infos.find_all('div', class_='card-infos__item-info')[1]
        city = arena_city_viewers_infos.find_all()[1]
        return city.text.strip()

    def get_viewers(self) -> int:
        card_infos = self._soup.find('div', class_='card-infos')
        arena_city_viewers_infos = card_infos.find_all('div', class_='card-infos__item-info')[1]
        try:
            viewers = arena_city_viewers_infos.find_all()[2]
            return int(viewers.text.split(' ')[0])
        except Exception:
            return 0

    def get_text_broadcast_stats(self) -> dict[str, int | dict[str, int]]:
        items = self._soup.findAll('p', class_='textBroadcast-item__right-text')
        text_stats = [row for row in items if row.strong]

        match_stats = self._get_stats_by_period(text_stats)
        stats = self._parse_stats_by_period(match_stats)

        if self.have_penalties():
            score_status = self._soup.find('p', class_="preview-frame__center-score")
            score_text = re.split('[<>]', str(score_status))
            score = []
            for item in score_text:
                if item.isdigit():
                    score.append(int(item))
            if score[0] > score[1]:
                stats['g_home']['b'] = 1
                stats['g_guest']['b'] = 0
            else:
                stats['g_home']['b'] = 0
                stats['g_guest']['b'] = 1

        return stats

    def get_additional_stats(self, stat_dict: dict[str, str]) -> dict[str, dict]:
        team_stats = self._soup.find('table', class_="broadcast-table__group-item")
        head = team_stats.find_all('th')
        body = team_stats.find_all('td')
        # заголовок команды отмечен тегом td, поэтому попадает в боди
        head.insert(0, body.pop(0))
        return self._parse_table_stats(head, body, stat_dict)

    def update_date(self, date: datetime.datetime) -> datetime:
        msk_delta = datetime.timedelta(hours=3)
        _date = date + msk_delta
        card_infos = self._soup.find('div', class_='card-infos')
        date_text = card_infos.find('div', class_='card-infos__item-info').text
        time = date_text.split(',')[1].strip()
        hours, minutes = time.split(':')
        new_date = datetime.datetime(
            year=_date.year,
            month=_date.month,
            day=_date.day,
            hour=int(hours),
            minute=int(minutes)
        )
        msk = pytz.timezone('Europe/Moscow')
        return msk.localize(new_date)

    def have_penalties(self) -> bool:
        ots = self._soup.find('span', class_='preview-frame__ots')
        if not ots:
            return False
        return 'Б' in ots.text

    def have_overtime(self) -> bool:
        ots = self._soup.find('span', class_='preview-frame__ots')
        if not ots:
            return False
        return 'ОТ' in ots.text


class _OldDesignParser(_LocalParser):

    def get_status(self) -> str:
        return self._soup.find('dd', class_="b-period_score").text

    def get_arena(self) -> str:
        arena_info = self._soup.find_all('li', class_="b-match_add_info_item")[1]
        info = arena_info.find_all('span')[1]
        info = str(info).split('<br/>')
        arena_city = info[0][6:]
        return arena_city.split('(')[0][:-1]

    def get_city(self) -> str:
        arena_info = self._soup.find_all('li', class_="b-match_add_info_item")[1]
        info = arena_info.find_all('span')[1]
        info = str(info).split('<br/>')
        arena_city = info[0][6:]
        return arena_city.split('(')[1][:-1].strip()

    def get_viewers(self) -> int:
        arena_info = self._soup.find_all('li', class_="b-match_add_info_item")[1]
        info = arena_info.find_all('span')[1]
        info = str(info).split('<br/>')
        if info[1] != '</span>':
            return int(info[1][:-16])
        return 0

    def get_text_broadcast_stats(self) -> dict[str, int | dict[str, int]]:
        text_stats = self._soup.find_all('p', class_='e-action_txt')

        match_stats = self._get_stats_by_period(text_stats)
        stats = self._parse_stats_by_period(match_stats)

        if self.have_penalties():
            score = self._soup.find('dt', class_="b-total_score").h3.text.split('–')
            score[0] = int(score[0])
            score[1] = int(score[1][:-1])
            if score[0] > score[1]:
                stats['g_home']['b'] = 1
                stats['g_guest']['b'] = 0
            else:
                stats['g_home']['b'] = 0
                stats['g_guest']['b'] = 1

        return stats

    def get_additional_stats(self, stat_dict: dict[str, str]) -> dict[str, dict]:
        team_stats = self._soup.find_all('div', class_="table-responsive")
        head = [x.find_all('th') for x in team_stats][0]
        body = [x.find_all('td') for x in team_stats][0]
        return self._parse_table_stats(head, body, stat_dict)

    def update_date(self, date: datetime.datetime) -> datetime:
        date_info = self._soup.find('li', class_="b-match_add_info_item")
        info = date_info.find_all('span')[1]
        info = str(info).split('<br/>')
        time = info[1][:5]
        hours, minutes = time.split(':')
        msk_delta = datetime.timedelta(hours=3)
        _date = date + msk_delta
        new_date = datetime.datetime(
            year=_date.year,
            month=_date.month,
            day=_date.day,
            hour=int(hours),
            minute=int(minutes)
        )
        msk = pytz.timezone('Europe/Moscow')
        return msk.localize(new_date)

    def have_penalties(self) -> bool:
        return 'Б' in self._soup.find('dt', class_="b-total_score").h3.text

    def have_overtime(self) -> bool:
        return 'ОТ' in self._soup.find('dt', class_="b-total_score").h3.text


def _get_parser(soup) -> _LocalParser | None:
    extra_info = soup.find_all('li', class_="b-match_add_info_item")
    if extra_info:
        return _OldDesignParser(soup)
    extra_info = soup.find_all('div', class_="card-infos__item-info")
    if extra_info:
        return _NewDesignParser(soup)
    return
