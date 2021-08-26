import requests
from bs4 import BeautifulSoup


url = 'https://www.khl.ru/stat/teams/1046/'

r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')
team_tags = soup.find_all('span', class_='e-club_name')
teams = [team.text for team in team_tags]
print(teams)

a = soup.find_all('tr')
b = [x for x in a if x.find_all(class_='e-club_name')]
for i, v in enumerate(b):
    #print(i.find(class_='e-club_name').text)
    tr = v.find_all('td')
    stats = [td.text for td in tr][1:]
    print(stats)




