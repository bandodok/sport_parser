import datetime
import json
import tempfile

import pytz

from sport_parser.khl.data_analysis.formatter import Formatter
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


class Parser:
    def __init__(self, config):
        self.formatter = Formatter(config)

    def parse_teams(self, season):
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
            teams.extend(self._get_division_team_list(division_soup, division, conference, season))
        return teams

    def parse_calendar(self, season, *, webdriver=None):
        """Загружает базовую информацию по матчам в базу данных"""
        if not webdriver:
            webdriver = self._calendar_request_content

        output = []

        url = f'https://www.khl.ru/calendar/{season.external_id}/00/'
        soup = webdriver(url)
        match_soup = soup.find('div', id='tab-calendar-all')
        if not match_soup:
            match_soup = soup.find('div', id='tab-calendar-last')

        dates = match_soup.find_all('div', class_='b-final_cup_date')
        dates = [date.b.text for date in dates]

        matches = match_soup.find_all('div', class_='m-future')
        match_dict = {}
        for date, match_soup in zip(dates, matches):
            if date in match_dict:
                date = f'{date}_1'
            match_dict[date] = match_soup

        for date, matches in match_dict.items():
            if date.endswith('_1'):
                date = date[:-2]

            match_list = matches.find_all('li', class_='b-wide_tile_item')

            string_date = self.formatter.date_format(date)
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
                match_info = {
                    'match_id': match_id,
                    'date': date_msk,
                    'home_team': home_team,
                    'guest_team': guest_team,
                    'season': season
                }

                match_extra_info = {
                    'penalties': False,
                    'overtime': False
                }
                score = match.find('dl', class_='b-score')
                if '+' in score.dt.h3.text:
                    status = 'postponed'
                elif '—' in score.dt.h3.text:
                    status = 'finished'
                else:
                    status = 'scheduled'
                    time = score.dt.h3.text.split(' ')[0]
                    hours, minutes = time.split(':')
                    timedelta = datetime.timedelta(hours=int(hours), minutes=int(minutes))
                    match_info['date'] = date_msk + timedelta
                    city = score.dd.p.text
                    match_extra_info = {
                        'city': city,
                    }

                match_info.update(match_extra_info)
                match_info.update({
                    'status': status,
                })
                output.append(match_info)
        return output

    def parse_match(self, match):
        url = f'https://text.khl.ru/text/{match.id}.html'
        soup = self.get_request_content(url)

        extra_info = soup.find_all('li', class_="b-match_add_info_item")
        if not extra_info:
            return self.parse_unfinished_match(match)

        match_status = soup.find('dd', class_="b-period_score").text
        if match_status != 'матч завершен':
            return self.parse_unfinished_match(match)

        return self.parse_finished_match(match, soup)

    def parse_unfinished_match(self, match):
        return {
            'match_id': match.id,
            'season': match.season,
        }

    def parse_finished_match(self, match, match_data):
        soup = match_data

        penalties = False
        overtime = False
        score_status = soup.find('dt', class_="b-total_score").h3
        if 'Б' in score_status.text:
            penalties = True
        if 'ОТ' in score_status.text:
            overtime = True

        extra_info = soup.find_all('li', class_="b-match_add_info_item")
        date_info = extra_info[0]
        arena_info = extra_info[1]

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
        date_msk = msk.localize(new_date)

        info = arena_info.find_all('span')[1]

        info = str(info).split('<br/>')
        arena_city = info[0][6:]
        arena, city = arena_city.split('(')
        arena = arena[:-1]
        city = city[:-1]
        city = city.strip()

        if info[1] == '</span>':
            viewers = 0
        else:
            viewers = info[1][:-16]

        return {
            'match_id': match.id,
            'season': match.season,
            'arena': arena,
            'city': city,
            'date': date_msk,
            'viewers': viewers,
            'penalties': penalties,
            'overtime': overtime,
            'status': 'finished'
        }

    def parse_protocol(self, match):
        """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
        url = f"https://text.khl.ru/text/{match.id}.html"
        soup = self.get_request_content(url)
        match_status = soup.find('dd', class_="b-period_score")
        if not match_status or match_status.text != 'матч завершен':
            return f'match not found {match.id}'

        # Общего количества бросков нет в протоколе, берется отдельно из текстовой трансляции
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
        g_home = {}
        g_guest = {}

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

        row_home = {stat_dict[stat]: value for stat, value in zip(columns, rows)}
        row_guest = {stat_dict[stat]: value for stat, value in zip(columns, rows[len(columns):])}

        row_home.update({
            'match_id': match.id,
            'sh': sh_home,
            'g_1': g_home.get('p1'),
            'g_2': g_home.get('p2'),
            'g_3': g_home.get('p3'),
            'g_ot': g_home.get('ot'),
            'g_b': g_home.get('b'),
        })
        row_guest.update({
            'match_id': match.id,
            'sh': sh_guest,
            'g_1': g_guest.get('p1'),
            'g_2': g_guest.get('p2'),
            'g_3': g_guest.get('p3'),
            'g_ot': g_guest.get('ot'),
            'g_b': g_guest.get('b'),
        })

        return self._row_update_type(row_home), self._row_update_type(row_guest)

    def _row_update_type(self, row):
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

    def _get_division_team_list(self, division_soup, division, conference, season):
        """Возвращает """
        teams = []
        for team in division_soup.find_all('a'):
            team_src = f"https://www.khl.ru{team['href']}arena/"
            soup = self.get_request_content(team_src)
            city_table = soup.find('div', class_='b-blocks_cover')

            name = team.text
            img = f"https://www.khl.ru{city_table.find('img')['src']}"
            city = city_table.find('p').text
            arena = soup.find_all('div', class_='b-short_block').pop().find('h4').text

            teams.append({
                'name': name,
                'img': img,
                'city': city,
                'arena': arena,
                'division': division,
                'conference': conference,
                'season': season
            })

        return teams

    @staticmethod
    def get_request_content(url):
        r = requests.get(url)
        return BeautifulSoup(r.content, 'html.parser')

    @staticmethod
    def get_api_request_content(url):
        r = requests.get(url).content
        return json.loads(r)

    @staticmethod
    def get_selenium_content(url):
        loc = os.getenv('CHROMEDRIVER')
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument('ignore-certificate-errors')
        capabilities = webdriver.DesiredCapabilities().CHROME
        capabilities['acceptSslCerts'] = True
        driver = webdriver.Chrome(loc, options=op)
        driver.get(url)
        r = driver.page_source
        driver.close()
        return BeautifulSoup(r, 'html.parser')

    @staticmethod
    def _calendar_request_content(url):
        r = requests.get(url)
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(f'{tmpdirname}/file1.txt', 'w', encoding='utf-8') as f:
                a = r.text.replace('<!--div align="center" style="margin-top: 1em;">', ' ')
                f.write(a)
            with open(f'{tmpdirname}/file1.txt', 'rb') as f:
                soup = BeautifulSoup(f, 'html.parser')
            return soup
