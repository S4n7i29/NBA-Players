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
        
        #SET TEAMS LIST, DICTS AND ROWS
        teams = []
        active_teams_wr_dict = {}
        active_teams_names_dict = {}
        current_team = None
        active_teams_rows = active_teams_table.find_all('tr', class_=['full_table', 'partial_table'])

        for row in active_teams_rows:
            if 'full_table' in row['class']:
                
                #GET TEAM AND RINGS
                current_team = row.find('th').text.strip()
                rings = int(row.find('td', {'data-stat': 'years_league_champion'}).text.strip())
                
                teams.append((current_team, True))
                active_teams_names_dict[current_team] = []
                active_teams_wr_dict[current_team] = rings
            
            elif 'partial_table' in row['class'] and current_team:
                
                #GET TEAM'S RELATED NAME/S
                related_name = row.find('th').text.strip()

                teams.append((related_name, False))
                active_teams_names_dict[current_team].append(related_name)

    #CLEAN TEAMS LIST
    tracked_names = set()
    aux_teams = []
    for t in teams:
        name = t[0]
        if name not in tracked_names:
            tracked_names.add(name)  # Agregar el nombre al conjunto
            aux_teams.append(t)
    
    teams = aux_teams

    #GET DIVISIONS & CONFERENCES
    divisions = soup.select('div#footer_general div#site_menu li div.division')
    if divisions is not None:
        
        #SET CONFERENCE/DIVISION DICT
        conference_division = {
            'East' : ['Atlantic', 'Central', 'Southeast'],
            'West' : ['Northwest', 'Pacific', 'Southwest']
        }

        #SET DIVISION/TEAMS DICT
        division_team = {}
        for d in divisions:
            division = d.find('strong').text.strip()
            ts = []
            for t in d.find_all('a'):
                t = t.text.strip()
                for team in teams:
                    if team[1] == True:
                        if t in team[0]:
                            ts.append(team[0])
                            break
            division_team[division] = ts

        #CREATE TEAMS / CONFERENCE & DIVISION DICT
        active_teams_wcd_dict = {}
        for t in teams:
            if t[1] == True:
                for c, ds in conference_division.items():
                    for d in ds:
                        if t[0] in division_team[d]:
                            active_teams_wcd_dict[t[0]] = {'Conf': c, 'Div': d}
    '''
    #PRINTS (Para chequear)        
    
    for t in teams:
        if t[1] == True:
            print(f'\n{t[0].upper()} - Rings: {active_teams_wr_dict[t[0]]}, Conference: {active_teams_wcd_dict[t[0]]["Conf"]}, Division: {active_teams_wcd_dict[t[0]]["Div"]}')

    print('\n\n')
    
    for t, n in active_teams_names_dict.items():
        print(f'{t.upper()}: {n}\n')
    '''
    
    return teams, active_teams_wr_dict, active_teams_wcd_dict