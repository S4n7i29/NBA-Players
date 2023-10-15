from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re

#ACCESS FIELD FUNCTION (Busca en una lista de campos uno en específico, siguiendo una condición (contiene a), permitiendo acceder desde el campo encontrado al anterior, posterior, etc)
def access_field(fields, conditions, before_next, all_conditions=True):
    if type(conditions) != list:
        conditions = [conditions]
    
    x_field = None
    
    for index, field in enumerate(fields):
        if all_conditions:
            # Verificar si todas las condiciones se cumplen en el campo actual
            if all(condition in field.text for condition in conditions):
                x_field = fields[index + before_next]
                break
        else:
            # Verificar si al menos una de las condiciones se cumple en el campo actual
            if any(condition in field.text for condition in conditions):
                x_field = fields[index + before_next]
                break
    
    return x_field

#HANDLE GETTING DATA ISSUES FUNCTION (Realiza un manejo de posibles errores que puedan tener elementos tomados de un soup)
def get_data(data):
    try:
        return data
    except (ValueError, AttributeError, IndexError):
        return None

#MODIFY STAT TYPE FUNCTION (Valida si el stat está vacío y lo convierte en 'None'. Si no está vacío, lo convierte en el tipo pasado como argumento)
def modify_stat_type(stat, type):
    if stat.strip() == '':
        stat = None
    else:
        if type is int:
            return int(stat)
        if type is float:
            return float(stat)

def generate_player_data(url):

    #CREATE PLAYER DATA DICT
    player_data = {}

    #SET SOUP
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')

    #SET PLAYER INFO FIELDS
    player_info                 =   soup.find('div', id='meta').find_all('div')[1]
    player_info_fields          =   player_info.find_all('p')

    #SET STATS PER GAME TABLES
    stats_per_game_tables_div   =   soup.find('div', id='switcher_per_game-playoffs_per_game')
    stats_per_game_tables       =   stats_per_game_tables_div.find_all('table')
    #SET REGULAR SEASON TABLE
    rs_stats_per_game_table     =   stats_per_game_tables[0].find('tbody')
    rs_stats_per_game_rows      =   rs_stats_per_game_table.find_all('tr')
    #SET PLAYOFFS TABLE
    po_stats_per_game_table     =   stats_per_game_tables[1].find('tbody')
    po_stats_per_game_rows      =   po_stats_per_game_table.find_all('tr')

    #GET NAME
    name                        =   get_data(player_info.find('h1').text)
    separated_name              =   get_data(name.split(' '))
    first_name                  =   get_data(separated_name[0].strip())
                                    #Selecciona el nombre y elimina el '\n' a la izquierda
    last_name                   =   get_data(" ".join(separated_name[1:]).strip())
                                    #Selecciona todo lo que no sea el primer elemento (nombre) y elimina el '\n' a la derecha

    #GET BIRTH INFO
    birth_field                 =   access_field(player_info_fields, 'Born:', 0)
    birth_spans                 =   get_data(birth_field.find_all('span'))
    date_of_birth               =   get_data(birth_spans[0]['data-birth'])
    birth_place                 =   get_data(birth_spans[1].text[8:])
                                    #Saca el 'in' y los primeros caracteres raros
    separated_birth_place       =   get_data(birth_place.split(','))
    place_of_birth              =   get_data(separated_birth_place[0])
    state_of_birth              =   get_data(" ".join(separated_birth_place[1:])[1:])
                                    #Si no le pongo los dos ':1' sale toda bugueada la cadena
    country_of_birth            =   get_data(birth_spans[2].text)
                                    #Falta cambiar los códigos por el país!!!

    #GET POSITIONS/SHOOTS
    positions_shoots_field      =   access_field(player_info_fields, 'Position:', 0)
    separated_positions_shoots  =   get_data(positions_shoots_field.text.split('▪'))
    shoots                      =   get_data(separated_positions_shoots[1][22:].rstrip())
                                    #Saca los primeros caracteres raros más el 'Shoots: ' y último
    positions                   =   get_data(re.sub(r', and | and ', ', ' , separated_positions_shoots[0][19:].rstrip())).split(', ')
                                    #Busca los ', and ' y los ' and ' y normaliza reemplazando todos por una ',', para después usarla de separador en la lista (esto aplicado a la cadena sin los primeros caracteres raros y el 'Position: ')

    #GET PHYSICAL INFO
    height_weight_field         =   access_field(player_info_fields, ['lb', 'cm', 'kg'], 0)
                                    #O podría pasarle como condition sólo 'Position:' y darle de before_next un 1
    separated_height_weight     =   get_data(height_weight_field.text.split('(')[1].rstrip()[:-1].split(','))
                                    #Toma sólo lo que está después del paréntesis, saca el espacio del final, saca el paréntesis y separa por ','
    height                      =   get_data(separated_height_weight[0][:-2])
                                    #Saca los últimos dos dígitos (la unidad)
    weight                      =   get_data(separated_height_weight[1][1:][:-2])
                                    #Saca el primer caracter raro y los últimos dos dígitos (la unidad)

    #GET COLLEGE
    college_field               =   access_field(player_info_fields, 'College:', 0)
    college                     =   get_data(college_field.text.strip()[19:])
                                    #Saca el 'College: ' y los primeros caracteres raros

    #GET DRAFT
    draft_field                 =   access_field(player_info_fields, 'Draft:', 0)
    draft_as                    =   get_data(draft_field.find_all('a'))
                                    #Como todos los equipos y todos los años de draft tienen un link, accedo a estos a través de los 'a'
    draft_team                  =   get_data(draft_as[0].text)
    separated_round_pick        =   get_data(draft_field.text.split(',')[1].strip().split('('))
                                    #Separa por ',', tomando el segundo elemento, elimina los espacios anterior y posterior y separa con el paréntesis
    round                       =   get_data(separated_round_pick[0][0])
                                    #Toma sólo el número de la ronda (que es el primer caracter porque ya se eliminó el espacio)
    pick                        =   get_data(separated_round_pick[1][0])
                                    #Toma sólo el número del pick (que es el primer caracter)
    draft_year                  =   get_data(draft_as[1].text[:4])
                                    #Como los años son de 4 dígitos, toma sólo hasta el cuarto

    #GET REGULAR SEASON STATS
    rs_stats_per_game_list = []
    team_tl_code = None
    for row in rs_stats_per_game_rows:
        one_year_dict = {}
        
        #Le puse esto porque, en las temporadas que no jugó, el "th", que es donde está la "season" no existe, en cambio es un "td". El ".text" lo pongo después porque no me deja hacer un ".text" de un "None"
        season_cell = row.find('th')
        if season_cell is not None:
            #Season
            season = (season_cell.text[0:2] + season_cell.text[-2:])
            season = modify_stat_type(season,int)
            one_year_dict['Season'] = season
            #Team
            team_cell = row.find('td', {'data-stat' : 'team_id'})
            if team_tl_code != team_cell.text:
                team_tl_code = team_cell.text
                if team_cell.find('a') is not None:
                    team_url = urljoin('https://www.basketball-reference.com', team_cell.find('a')['href'])
                else:
                    continue
                team_page = requests.get(team_url)
                team_soup = BeautifulSoup(team_page.text, 'lxml')
                team = team_soup.find('h1').find_all('span')[1].text.strip()
            one_year_dict['Team'] = team
            #Games Played
            games_played = row.find('td', {'data-stat' : 'g'}).text
            games_played = modify_stat_type(games_played, int)
            one_year_dict['Games Played'] = games_played
            #Games Started
            games_started = row.find('td', {'data-stat' : 'gs'}).text
            games_started = modify_stat_type(games_started, int)
            one_year_dict['Games Started'] = games_started
            #Minutes Played
            minutes_played = row.find('td', {'data-stat' : 'mp_per_g'}).text
            minutes_played = modify_stat_type(minutes_played, float)
            one_year_dict['Minutes Played'] = minutes_played
            #Field Goals
            field_goals = row.find('td', {'data-stat' : 'fg_per_g'}).text
            field_goals = modify_stat_type(field_goals, float)
            one_year_dict['Field Goals'] = field_goals
            #Field Goal Attempts
            field_goal_attempts = row.find('td', {'data-stat' : 'fga_per_g'}).text
            field_goal_attempts = modify_stat_type(field_goal_attempts, float)
            one_year_dict['Field Goal Attempts'] = field_goal_attempts
            #Field Goal Percentage
            field_goal_percentage = ('0' + row.find('td', {'data-stat' : 'fg_pct'}).text)
            field_goal_percentage = modify_stat_type(field_goal_percentage, float)
            one_year_dict['Field Goal Percentage'] = field_goal_percentage
            #Three Points
            three_points = row.find('td', {'data-stat' : 'fg3_per_g'}).text
            three_points = modify_stat_type(three_points, float)
            one_year_dict['Three Points'] = three_points
            #Three Point Attempts
            three_point_attempts = row.find('td', {'data-stat' : 'fg3a_per_g'}).text
            three_point_attempts = modify_stat_type(three_point_attempts, float)
            one_year_dict['Three Point Attempts'] = three_point_attempts
            #Three Point Percentage
            three_point_percentage = ('0' + row.find('td', {'data-stat' : 'fg3_pct'}).text)
            three_point_percentage = modify_stat_type(three_point_percentage, float)
            one_year_dict['Three Point Percentage'] = three_point_percentage
            #Fhree Throws
            free_throws = row.find('td', {'data-stat' : 'ft_per_g'}).text
            free_throws = modify_stat_type(free_throws, float)
            one_year_dict['Free Throws'] = free_throws
            #Fhree Throw Attempts
            free_throws_attempts = row.find('td', {'data-stat' : 'fta_per_g'}).text
            free_throws_attempts = modify_stat_type(free_throws_attempts, float)
            one_year_dict['Free Throws Attempts'] = free_throws_attempts
            #Fhree Throw Percentage
            free_throws_percentage = ('0' + row.find('td', {'data-stat' : 'ft_pct'}).text)
            free_throws_percentage = modify_stat_type(free_throws_percentage, float)
            one_year_dict['Free Throws Percentage'] = free_throws_percentage
            #Rebounds
            rebounds = row.find('td', {'data-stat' : 'trb_per_g'}).text
            rebounds = modify_stat_type(rebounds, float)
            one_year_dict['Rebounds'] = rebounds
            #Assists
            assists = row.find('td', {'data-stat' : 'ast_per_g'}).text
            assists = modify_stat_type(assists, float)
            one_year_dict['Assists'] = assists
            #Steals
            steals = row.find('td', {'data-stat' : 'stl_per_g'}).text
            steals = modify_stat_type(steals, float)
            one_year_dict['Steals'] = steals
            #Blocks
            blocks = row.find('td', {'data-stat' : 'blk_per_g'}).text
            blocks = modify_stat_type(blocks, float)
            one_year_dict['Blocks'] = blocks
            #Turnovers
            turnovers = row.find('td', {'data-stat' : 'tov_per_g'}).text
            turnovers = modify_stat_type(turnovers, float)
            one_year_dict['Turnovers'] = turnovers
            #Personal Fouls
            personal_fouls = row.find('td', {'data-stat' : 'pf_per_g'}).text
            personal_fouls = modify_stat_type(personal_fouls, float)
            one_year_dict['Personal Fouls'] = personal_fouls
            #Points
            points = row.find('td', {'data-stat' : 'pts_per_g'}).text
            points = modify_stat_type(points, float)
            one_year_dict['Points'] = points

            rs_stats_per_game_list.append(one_year_dict)

    #GET PLAYOFFS STATS
    po_stats_per_game_list = []
    team_tl_code = None
    for row in po_stats_per_game_rows:
        one_year_dict = {}
        
        #Acá no hace falta lo del "th" que puse en los stats de regular season, pero lo dejo como validación
        season_cell = row.find('th')
        if season_cell is not None:
            #Season
            season = (season_cell.text[0:2] + season_cell.text[-2:])
            season = modify_stat_type(season,int)
            one_year_dict['Season'] = season
            #Team
            team_cell = row.find('td', {'data-stat' : 'team_id'})
            if team_tl_code != team_cell.text:
                team_tl_code = team_cell.text
                if team_cell.find('a') is not None:
                    team_url = urljoin('https://www.basketball-reference.com', team_cell.find('a')['href'])
                else:
                    continue
                team_page = requests.get(team_url)
                team_soup = BeautifulSoup(team_page.text, 'lxml')
                team = team_soup.find('h1').find_all('span')[1].text.strip()
            one_year_dict['Team'] = team
            #Games Played
            games_played = row.find('td', {'data-stat' : 'g'}).text
            games_played = modify_stat_type(games_played, int)
            one_year_dict['Games Played'] = games_played
            #Games Started
            games_started = row.find('td', {'data-stat' : 'gs'}).text
            games_started = modify_stat_type(games_started, int)
            one_year_dict['Games Started'] = games_started
            #Minutes Played
            minutes_played = row.find('td', {'data-stat' : 'mp_per_g'}).text
            minutes_played = modify_stat_type(minutes_played, float)
            one_year_dict['Minutes Played'] = minutes_played
            #Field Goals
            field_goals = row.find('td', {'data-stat' : 'fg_per_g'}).text
            field_goals = modify_stat_type(field_goals, float)
            one_year_dict['Field Goals'] = field_goals
            #Field Goal Attempts
            field_goal_attempts = row.find('td', {'data-stat' : 'fga_per_g'}).text
            field_goal_attempts = modify_stat_type(field_goal_attempts, float)
            one_year_dict['Field Goal Attempts'] = field_goal_attempts
            #Field Goal Percentage
            field_goal_percentage = ('0' + row.find('td', {'data-stat' : 'fg_pct'}).text)
            field_goal_percentage = modify_stat_type(field_goal_percentage, float)
            one_year_dict['Field Goal Percentage'] = field_goal_percentage
            #Three Points
            three_points = row.find('td', {'data-stat' : 'fg3_per_g'}).text
            three_points = modify_stat_type(three_points, float)
            one_year_dict['Three Points'] = three_points
            #Three Point Attempts
            three_point_attempts = row.find('td', {'data-stat' : 'fg3a_per_g'}).text
            three_point_attempts = modify_stat_type(three_point_attempts, float)
            one_year_dict['Three Point Attempts'] = three_point_attempts
            #Three Point Percentage
            three_point_percentage = ('0' + row.find('td', {'data-stat' : 'fg3_pct'}).text)
            three_point_percentage = modify_stat_type(three_point_percentage, float)
            one_year_dict['Three Point Percentage'] = three_point_percentage
            #Fhree Throws
            free_throws = row.find('td', {'data-stat' : 'ft_per_g'}).text
            free_throws = modify_stat_type(free_throws, float)
            one_year_dict['Free Throws'] = free_throws
            #Fhree Throw Attempts
            free_throws_attempts = row.find('td', {'data-stat' : 'fta_per_g'}).text
            free_throws_attempts = modify_stat_type(free_throws_attempts, float)
            one_year_dict['Free Throws Attempts'] = free_throws_attempts
            #Fhree Throw Percentage
            free_throws_percentage = ('0' + row.find('td', {'data-stat' : 'ft_pct'}).text)
            free_throws_percentage = modify_stat_type(free_throws_percentage, float)
            one_year_dict['Free Throws Percentage'] = free_throws_percentage
            #Rebounds
            rebounds = row.find('td', {'data-stat' : 'trb_per_g'}).text
            rebounds = modify_stat_type(rebounds, float)
            one_year_dict['Rebounds'] = rebounds
            #Assists
            assists = row.find('td', {'data-stat' : 'ast_per_g'}).text
            assists = modify_stat_type(assists, float)
            one_year_dict['Assists'] = assists
            #Steals
            steals = row.find('td', {'data-stat' : 'stl_per_g'}).text
            steals = modify_stat_type(steals, float)
            one_year_dict['Steals'] = steals
            #Blocks
            blocks = row.find('td', {'data-stat' : 'blk_per_g'}).text
            blocks = modify_stat_type(blocks, float)
            one_year_dict['Blocks'] = blocks
            #Turnovers
            turnovers = row.find('td', {'data-stat' : 'tov_per_g'}).text
            turnovers = modify_stat_type(turnovers, float)
            one_year_dict['Turnovers'] = turnovers
            #Personal Fouls
            personal_fouls = row.find('td', {'data-stat' : 'pf_per_g'}).text
            personal_fouls = modify_stat_type(personal_fouls, float)
            one_year_dict['Personal Fouls'] = personal_fouls
            #Points
            points = row.find('td', {'data-stat' : 'pts_per_g'}).text
            points = modify_stat_type(points, float)
            one_year_dict['Points'] = points

            po_stats_per_game_list.append(one_year_dict)

    #PRINTS (Para chequear)
    print("\nPLAYER INFO:")
    print("\nFirst Name: " + first_name)
    print("Last Name: " + last_name)
    print("\nDate of Birth: " + date_of_birth)
    print("Place of Birth: " + place_of_birth)
    print("State of Birth: " + state_of_birth)
    print("Country of Birth: " + country_of_birth)
    print("\nShoots: " + shoots)
    print("Position/s: " + ", ".join(positions))
    print("\nHeight: " + height)
    print("Weight: " + weight)
    if college is not None:
        print("\nCollege: " + college)
    else:
        print("\nNo College")
    print("\nDRAFT")
    print("Team: " + draft_team)
    print("Round: " + round)
    print("Pick: " + pick)
    print("Year: " + draft_year)

    print("\n\nREGULAR SEASON STATS:")
    for e in rs_stats_per_game_list:
        print(f'\nYEAR {rs_stats_per_game_list.index(e) + 1}:')
        print("----------------------")
        for c, v in e.items():
            print(f'{c.upper()}: {v}')

    print("\n\nPLAYOFFS STATS:")
    for e in po_stats_per_game_list:
        print(f'\nYEAR {po_stats_per_game_list.index(e) + 1}:')
        print("----------------------")
        for c, v in e.items():
            print(f'{c.upper()}: {v}')
    
    #SET PLAYER DATA DICT
    player_data['First Name'] = first_name
    player_data['Last Name'] = last_name
    player_data['Data of Birth'] = date_of_birth
    player_data['Place of Birth'] = place_of_birth
    player_data['State of Birth'] = state_of_birth
    player_data['Country of Birth'] = country_of_birth
    player_data['Shoots'] = shoots
    player_data['Positions'] = positions
    player_data['Height'] = height
    player_data['Weight'] = weight
    player_data['College'] = college
    player_data['Draft Team'] = draft_team
    player_data['Round'] = round
    player_data['Pick'] = pick
    player_data['Draft Year'] = draft_year
    player_data['Regular Season Stats'] = rs_stats_per_game_list
    player_data['Playoffs Stats'] = po_stats_per_game_list

    return player_data