from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import time
import pprint

class Team:
    def _init_(self, link, img, name, league):
        self.link = link
        self.img = img
        self.name = name
        self.league = league

baseURL = "https://www.fifaindex.com"
teamsPage = "/es/teams/"
teams = []

while True:
    req = requests.get(baseURL + teamsPage)
    html = req.content
    soup = BeautifulSoup(html.decode("utf-8", "replace"), 'html.parser')

    rows = soup.select('table.table-teams tbody tr')
    for tr in rows:
        try:
            link = tr.select_one('td a.link-team')
            img = tr.select_one('td a.link-team img')
            name = tr.select_one('td[data-title="Nombre"] a')
            if name is None:
                print("_")
            else:
                print(name.attrs['title'])
            print('----')
            league = tr.select_one('td[data-title="Liga"] a')
            team = Team(baseURL + link["href"], img["data-src"], name.text.lstrip().rstrip(), league.text)
            teams.append(team)
        except TypeError:
            pass

    nextBtn = soup.select_one('ul.pagination li.ml-auto a')
    if nextBtn == None:
        break
    else:
        teamsPage = nextBtn['href']

pprint.pprint(teams)

now = datetime.now()
json_data = json.dumps(teams, default=lambda o: o._dict_, indent=4)

with open('fifaindex_teams_'+now.strftime("%m%d%Y_%H%M%S")+'.json', 'a') as f:
    f.write(json_data)
