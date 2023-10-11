from bs4 import BeautifulSoup
import requests

def generate_teams_data():

    #SET SOUP
    url = 'https://www.basketball-reference.com/teams'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')

    #GET TEAMS, RINGS AND RELATED NAMES
    active_teams_table = soup.find('div', id='div_teams_active').find('tbody')
    if active_teams_table is not None:
        #SET DICTS AND ROWS
        active_teams_wr_dict = {}
        active_teams_names_dict = {}
        current_team = None
        active_teams_rows = active_teams_table.find_all('tr', class_=['full_table', 'partial_table'])

        for row in active_teams_rows:
            if 'full_table' in row['class']:
                #GET TEAM AND RINGS
                current_team = row.find('th').text.strip()
                rings = int(row.find('td', {'data-stat': 'years_league_champion'}).text.strip())
                active_teams_names_dict[current_team] = []
                active_teams_wr_dict[current_team] = rings
            elif 'partial_table' in row['class'] and current_team:
                #GET TEAM'S RELATED NAME/S
                related_name = row.find('th').text.strip()
                active_teams_names_dict[current_team].append(related_name)

    #GET DIVISIONS & CONFERENCES
    divisions = soup.select('div#footer_general div#site_menu li div.division')
    if divisions is not None:
        
        #SET CONFERENCE/DIVISION DICT
        conference_division = {
            'East' : ['Atlantic', 'Central', 'Southeast'],
            'West' : ['Northwest', 'Pacific', 'Southwest']
        }

        #CREATE TEAMS LIST
        active_teams = []
        for t, r in active_teams_wr_dict.items():
            active_teams.append(t)

        #GET DIVISIONS
        division_team = {}
        for d in divisions:
            division = d.find('strong').text.strip()
            teams = []
            for t in d.find_all('a'):
                t_ = t.text.strip()
                for t__ in active_teams:
                    if t_ in t__:
                        teams.append(t__)
                        break
            division_team[division] = teams

        #CREATE TEAMS INFO DICT
        active_teams_wcd_dict = {}
        for t in active_teams:
            for c, ds in conference_division.items():
                for d in ds:
                    if t in division_team[d]:
                        active_teams_wcd_dict[t] = {'Conf': c, 'Div': d}

    #PRINTS (Para chequear)
    for t in active_teams:
        print(f'{t.upper()} - Rings: {active_teams_wr_dict[t]}, Conference: {active_teams_wcd_dict[t]["Conf"]}, Division: {active_teams_wcd_dict[t]["Div"]}\n')

    print('\n')

    for t, n in active_teams_names_dict.items():
        print(f'{t.upper()}: {n}\n')
    
    return active_teams, active_teams_wr_dict, active_teams_wcd_dict
