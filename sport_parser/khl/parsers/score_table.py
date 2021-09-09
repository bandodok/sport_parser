import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_score_table():
    """корректно работает на вкладке stats, не работает в standings"""
    url = 'https://www.khl.ru/stat/teams/1045/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    column_tags = soup.find('thead')
    columns = column_tags.find_all('th')
    columns = [x.text for x in columns]

    rows = []
    a = soup.find_all('tr')
    b = [x for x in a if x.find_all(class_='e-club_name')]
    for v in b:
        tr = v.find_all('td')
        stats = [td.text.strip() for td in tr]
        rows.append(stats)

    total_team_stats = pd.DataFrame(rows, columns=columns)
    return total_team_stats
