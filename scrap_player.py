from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re

from prints import print_player_data

#ACCESS FIELD FUNCTION (Busca en una lista de campos uno en específico, siguiendo una condición (contiene a), permitiendo acceder desde el campo encontrado al anterior, posterior, etc)
def access_field(fields, conditions, before_next, all_conditions=True):
    if type(conditions) != list:
        conditions = [conditions]
    
    x_field = None
    
    for index, field in enumerate(fields):
        if all_conditions:
            # Verifica si todas las condiciones se cumplen en el campo actual
            if all(condition in field.text for condition in conditions):
                x_field = fields[index + before_next]
                break
        else:
            # Verifica si al menos una de las condiciones se cumple en el campo actual
            if any(condition in field.text for condition in conditions):
                x_field = fields[index + before_next]
                break
    
    return x_field

#HANDLE GETTING DATA ISSUES FUNCTION (Ataja el error que se genera al pretender el 'text' de un 'None')
def get_text_data(data):
    try:
        return data.text
    except AttributeError:
        return None

#FIND STAT FUNCTION (Dada una fila de stats en una temporada, obtiene el stat, buscando su celda a través del 'data-stat' (Si 'simple_stat' es False, lo toma como 'pct_stat'))
def find_stat(season_row, stat_name, simple_stat):
    stat = get_text_data(season_row.find('td', {'data-stat' : stat_name}))
    if not simple_stat and stat is not None:
        stat = ('0' + stat)
    return stat

#MODIFY STAT TYPE FUNCTION (Valida si el stat está vacío y lo convierte en 'None'. Si no está vacío, lo convierte en el tipo pasado como argumento)
def modify_stat_type(stat, type):
    if stat.strip() == '':
        return None
    else:
        if type is int:
            return int(stat)
        if type is float:
            return float(stat)

#GET STAT FUNCTION (Obtiene el stat y modifica su tipo)
def get_stat(season_row, stat_name, type, simple_stat=True):
    stat = find_stat(season_row, stat_name, simple_stat)
    if stat is not None:
        stat = modify_stat_type(stat, type)
    return stat

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
    name                        =   player_info.find('h1')
    separated_name              =   name.text.split(' ')
    first_name                  =   separated_name[0].strip()
                                    #Selecciona el nombre y elimina el '\n' a la izquierda
    last_name                   =   " ".join(separated_name[1:]).strip()
                                    #Selecciona todo lo que no sea el primer elemento (nombre) y elimina el '\n' a la derecha

    #GET BIRTH INFO
    birth_field                 =   access_field(player_info_fields, 'Born:', 0)
    birth_spans                 =   birth_field.find_all('span')
    date_of_birth               =   birth_spans[0]['data-birth']
    birth_place                 =   birth_spans[1].text[8:]
                                    #Saca el 'in' y los primeros caracteres raros
    separated_birth_place       =   birth_place.split(',')
    place_of_birth              =   separated_birth_place[0]
    state_of_birth              =   " ".join(separated_birth_place[1:])[1:]
                                    #Si no le pongo los dos ':1' sale toda bugueada la cadena
    country_of_birth            =   birth_spans[2].text
                                    #Falta cambiar los códigos por el país!!!

    #GET POSITIONS/SHOOTS
    positions_shoots_field      =   access_field(player_info_fields, 'Position:', 0)
    separated_positions_shoots  =   positions_shoots_field.text.split('▪')
    shoots                      =   separated_positions_shoots[1][22:].rstrip()
                                    #Saca los primeros caracteres raros más el 'Shoots: ' y último
    positions                   =   re.sub(r' and |, and |/', ', ', separated_positions_shoots[0][19:].rstrip()).split(', ')
                                    #Busca los ' and ', los ', and ' y los '/'  y normaliza reemplazando todos por ', ', para después usarla de separador en la lista (esto aplicado a la cadena sin los primeros caracteres raros y el 'Position: ')

    #GET PHYSICAL INFO
    height_weight_field         =   access_field(player_info_fields, ['lb', 'cm', 'kg'], 0)
                                    #O podría pasarle como condition sólo 'Position:' y darle de before_next un 1
    separated_height_weight     =   height_weight_field.text.split('(')[1].rstrip()[:-1].split(',')
                                    #Toma sólo lo que está después del paréntesis, saca el espacio del final, saca el paréntesis y separa por ','
    height                      =   separated_height_weight[0][:-2]
                                    #Saca los últimos dos dígitos (la unidad)
    weight                      =   separated_height_weight[1][1:][:-2]
                                    #Saca el primer caracter raro y los últimos dos dígitos (la unidad)

    #GET COLLEGE
    college_field               =   access_field(player_info_fields, 'College:', 0)
    if college_field is not None:
        college                 =   college_field.text.strip()[19:]
                                    #Saca el 'College: ' y los primeros caracteres raros
    else:
        college = None

    #GET DRAFT
    draft_field                 =   access_field(player_info_fields, 'Draft:', 0)
    if draft_field is not None:
        draft_as                =   draft_field.find_all('a')
                                    #Como todos los equipos y todos los años de draft tienen un link, accedo a estos a través de los 'a'
        draft_team              =   draft_as[0].text
        separated_round_pick    =   draft_field.text.split(',')[1].strip().split('(')
                                    #Separa por ',', tomando el segundo elemento, elimina los espacios anterior y posterior y separa con el paréntesis
        round                   =   separated_round_pick[0][0]
                                    #Toma sólo el número de la ronda (que es el primer caracter porque ya se eliminó el espacio)
        pick                    =   separated_round_pick[1][0]
                                    #Toma sólo el número del pick (que es el primer caracter)
        draft_year              =   draft_as[1].text[:4]
                                    #Como los años son de 4 dígitos, toma sólo hasta el cuarto
    else:
        draft_team, round, pick, draft_year = None

    #GET REGULAR SEASON STATS
    rs_stats_per_game_list = []
    team_tl_code = None
    
    for row in rs_stats_per_game_rows:
        one_year_dict = {}
        
        #Le puse esto porque, en las temporadas que no jugó, el "th", que es donde está la "season" no existe, en cambio es un "td". El ".text" lo pongo después porque no me deja hacer un ".text" de un "None"
        season_cell = row.find('th')
        if season_cell is not None:
            #Season
            season                                      =   (season_cell.text[0:2] + season_cell.text[-2:])
            season                                      =   modify_stat_type(season,int)
            one_year_dict['Season']                     =   season
            
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
            one_year_dict['Games Played']               =   get_stat(row, 'g', int)
            #Games Started  
            one_year_dict['Games Started']              =   get_stat(row, 'gs', int)
            #Minutes Played 
            one_year_dict['Minutes Played']             =   get_stat(row, 'mp_per_g', float)
            #Field Goals    
            one_year_dict['Field Goals']                =   get_stat(row, 'fg_per_g', float)
            #Field Goal Attempts    
            one_year_dict['Field Goal Attempts']        =   get_stat(row, 'fga_per_g', float)
            #Field Goal Percentage  
            one_year_dict['Field Goal Percentage']      =   get_stat(row, 'fg_pct', float, False)
            #Three Points   
            one_year_dict['Three Points']               =   get_stat(row, 'fg3_per_g', float)
            #Three Point Attempts   
            one_year_dict['Three Point Attempts']       =   get_stat(row, 'fg3a_per_g', float)
            #Three Point Percentage 
            one_year_dict['Three Point Percentage']     =   get_stat(row, 'fg3_pct', float, False)
            #Fhree Throws   
            one_year_dict['Free Throws']                =   get_stat(row, 'ft_per_g', float)
            #Fhree Throw Attempts   
            one_year_dict['Free Throws Attempts']       =   get_stat(row, 'fta_per_g', float)
            #Fhree Throw Percentage 
            one_year_dict['Free Throws Percentage']     =   get_stat(row, 'ft_pct', float, False)
            #Rebounds   
            one_year_dict['Rebounds']                   =   get_stat(row, 'trb_per_g', float)
            #Assists    
            one_year_dict['Assists']                    =   get_stat(row, 'ast_per_g', float)
            #Steals 
            one_year_dict['Steals']                     =   get_stat(row, 'stl_per_g', float)
            #Blocks 
            one_year_dict['Blocks']                     =   get_stat(row, 'blk_per_g', float)
            #Turnovers  
            one_year_dict['Turnovers']                  =   get_stat(row, 'tov_per_g', float)
            #Personal Fouls 
            one_year_dict['Personal Fouls']             =   get_stat(row, 'pf_per_g', float)
            #Points 
            one_year_dict['Points']                     =   get_stat(row, 'pts_per_g', float)

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
            season                                      =   (season_cell.text[0:2] + season_cell.text[-2:])
            season                                      =   modify_stat_type(season,int)
            one_year_dict['Season']                     =   season
            
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
            one_year_dict['Games Played']               =   get_stat(row, 'g', int)
            #Games Started  
            one_year_dict['Games Started']              =   get_stat(row, 'gs', int)
            #Minutes Played 
            one_year_dict['Minutes Played']             =   get_stat(row, 'mp_per_g', float)
            #Field Goals    
            one_year_dict['Field Goals']                =   get_stat(row, 'fg_per_g', float)
            #Field Goal Attempts    
            one_year_dict['Field Goal Attempts']        =   get_stat(row, 'fga_per_g', float)
            #Field Goal Percentage  
            one_year_dict['Field Goal Percentage']      =   get_stat(row, 'fg_pct', float, False)
            #Three Points   
            one_year_dict['Three Points']               =   get_stat(row, 'fg3_per_g', float)
            #Three Point Attempts   
            one_year_dict['Three Point Attempts']       =   get_stat(row, 'fg3a_per_g', float)
            #Three Point Percentage 
            one_year_dict['Three Point Percentage']     =   get_stat(row, 'fg3_pct', float, False)
            #Fhree Throws   
            one_year_dict['Free Throws']                =   get_stat(row, 'ft_per_g', float)
            #Fhree Throw Attempts   
            one_year_dict['Free Throws Attempts']       =   get_stat(row, 'fta_per_g', float)
            #Fhree Throw Percentage 
            one_year_dict['Free Throws Percentage']     =   get_stat(row, 'ft_pct', float, False)
            #Rebounds   
            one_year_dict['Rebounds']                   =   get_stat(row, 'trb_per_g', float)
            #Assists    
            one_year_dict['Assists']                    =   get_stat(row, 'ast_per_g', float)
            #Steals 
            one_year_dict['Steals']                     =   get_stat(row, 'stl_per_g', float)
            #Blocks 
            one_year_dict['Blocks']                     =   get_stat(row, 'blk_per_g', float)
            #Turnovers  
            one_year_dict['Turnovers']                  =   get_stat(row, 'tov_per_g', float)
            #Personal Fouls 
            one_year_dict['Personal Fouls']             =   get_stat(row, 'pf_per_g', float)
            #Points 
            one_year_dict['Points']                     =   get_stat(row, 'pts_per_g', float)

            po_stats_per_game_list.append(one_year_dict)    

    #PRINTS (Para chequear)
    print_player_data(first_name,
                      last_name,
                      date_of_birth,
                      place_of_birth,
                      state_of_birth,
                      country_of_birth,
                      shoots,
                      positions,
                      height,
                      weight,
                      college,
                      draft_team,
                      round,
                      pick,
                      draft_year,
                      rs_stats_per_game_list,
                      po_stats_per_game_list)
    
    #SET PLAYER DATA DICT
    player_data['First Name']           =   first_name
    player_data['Last Name']            =   last_name
    player_data['Data of Birth']        =   date_of_birth
    player_data['Place of Birth']       =   place_of_birth
    player_data['State of Birth']       =   state_of_birth
    player_data['Country of Birth']     =   country_of_birth
    player_data['Shoots']               =   shoots
    player_data['Positions']            =   positions
    player_data['Height']               =   height
    player_data['Weight']               =   weight
    player_data['College']              =   college
    player_data['Draft Team']           =   draft_team
    player_data['Round']                =   round
    player_data['Pick']                 =   pick
    player_data['Draft Year']           =   draft_year
    player_data['Regular Season Stats'] =   rs_stats_per_game_list
    player_data['Playoffs Stats']       =   po_stats_per_game_list

    return player_data