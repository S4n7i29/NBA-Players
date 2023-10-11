from bs4 import BeautifulSoup
import requests

def access_field(fields, condition, before_next):
    if type(condition) != list:
        condition = [condition]
    
    x_field = None
    
    for c in condition:
        for f in enumerate(fields):
            if c in fields[f[0]].text:
                x_field = fields[f[0] + before_next]
                break
        return x_field


player_data = {}

url = ''
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')

player_info = soup.find('div', id='meta').find('div', class_=lambda x: x != 'media-item')
player_info_fields = player_info.find_all('p')

stats_per_game_tables_div = soup.find('div', id='switcher_per_game-playoffs_per_game')

rs_stats_per_game_table = stats_per_game_tables_div.find_all('table')[0].find('tbody')
rs_stats_per_game_rows = rs_stats_per_game_table.find_all('tr')

po_stats_per_game_table = stats_per_game_tables_div.find_all('table')[1].find('tbody')
po_stats_per_game_rows = po_stats_per_game_table.find_all('tr')

name = player_info.find('h1').find('span').text
separated_name = name.split(' ')
first_name = separated_name[0].strip()
last_name = " ".join(separated_name[1:]).strip()

birth_field = access_field(player_info_fields, 'Born:', 0)
if birth_field is not None:
    date_of_birth = birth_field.find_all('span')[0]['data-birth'].rstrip()
    birth_place = birth_field.find_all('span')[1].text[8:].rstrip()
    separated_birth_place = birth_place.split(',')
    place_of_birth = separated_birth_place[0].rstrip()
    state_of_birth = " ".join(separated_birth_place[1:])[1:].rstrip()
    country_of_birth = birth_field.find_all('span')[2].text.rstrip()      # Falta cambiar los códigos por el país!!!
positions_shoots_field = access_field(player_info_fields, 'Position:', 0)
if positions_shoots_field is not None:
    separated_positions_shoots = positions_shoots_field.text.split('▪')
    shoots = separated_positions_shoots[1][22:].rstrip()
    positions = separated_positions_shoots[0][19:].rstrip().replace(' and ', ', ').split(', ')
    for n in enumerate(positions):
        positions[n[0]] = positions[n[0]].strip(',')
height_weight_field = access_field(player_info_fields, ['lb', 'cm', 'kg'], 0)     # O podría pasarle como condition sólo 'Position:' y darle de before_next un 1
if height_weight_field is not None:
    separated_height_weight = height_weight_field.text.split('(')[1].rstrip()[:-1].split(',')
    height = separated_height_weight[0][:-2]
    weight = separated_height_weight[1][1:][:-2]
college_field = access_field(player_info_fields, 'College:', 0)
if college_field is not None:
    college = college_field.text.strip()[19:]
else:
    college = None


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
