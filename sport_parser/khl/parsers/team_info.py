import requests
from bs4 import BeautifulSoup
from django.conf import settings

from sport_parser.khl.database_services.db_add import add_teams_to_database


def parse_teams():
    teams = []
    for season in settings.SEASONS.values():
        season_teams = parse_teams_in_season(season)
        teams.extend([team for team in season_teams])
    for team in teams:
        add_teams_to_database(team)


def parse_teams_in_season(season_id):
    url = f'https://www.khl.ru/standings/{season_id}/division/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    divisions = soup.find('div', id='tab-standings-division').find_all('div', class_='k-data_table')
    teams = []

    season = 0
    for s, id in settings.SEASONS.items():
        if id <= season_id:
            season = s
            break

    # Дивизион Боброва
    division_soup = divisions[0].find_all('a')
    division = 'Боброва'
    conference = 'Запад'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Тарасова
    division_soup = divisions[1].find_all('a')
    division = 'Тарасова'
    conference = 'Запад'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Харламова
    division_soup = divisions[2].find_all('a')
    division = 'Харламова'
    conference = 'Восток'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Чернышева
    division_soup = divisions[3].find_all('a')
    division = 'Чернышева'
    conference = 'Восток'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    return teams


def _get_division_team_list(division_soup, division, conference, season):
    """Возвращает """
    teams = []
    for i in division_soup:
        team_src = f"https://www.khl.ru{i['href']}arena/"
        r = requests.get(team_src)
        soup = BeautifulSoup(r.content, 'html.parser')
        city_table = soup.find('div', class_='b-blocks_cover')

        name = i.text
        img = f"https://www.khl.ru{city_table.find('img')['src']}"
        city = city_table.find('p').text
        arena = soup.find_all('div', class_='b-short_block').pop().find('h4').text

        teams.append([name, img, city, arena, division, conference, season])

    return teams