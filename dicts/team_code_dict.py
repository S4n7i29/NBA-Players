from bs4 import BeautifulSoup
import requests as r

#SET SOUP
url = 'https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations'
page = r.get(url)
soup = BeautifulSoup(page.text, 'lxml') 

#SET TEAM/CODE TABLE
team_code_table = soup.find('table').find('tbody')
team_code_rows = team_code_table.find_all('tr')[1:]

#CREATE TEAM/CODE DICT
team_code_dict = {}
for row in team_code_rows:
    team_code = row.find_all('td')
    team = team_code[1].text.rstrip('\n')
    code = team_code[0].text.rstrip('\n')
    team_code_dict[code] = team

'''
#PRINTS (Para chequear)
for t, c in team_code_dict.items():
    print(f'{t}: {c}\n')
'''