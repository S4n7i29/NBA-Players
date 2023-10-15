from bs4 import BeautifulSoup
import requests as r
from urllib.parse import urljoin
from player import insert_player_data

#SET SOUP
url = 'https://www.basketball-reference.com/players'
page = r.get(url)
soup = BeautifulSoup(page.text, 'lxml')

#SET ALL LETTERS LINKS LIST
all_a = soup.find_all('a')
all_href = [a['href'] for a in all_a if len(a.text) == 1]
all_letters_url_list = [urljoin('https://www.basketball-reference.com', href) for href in all_href]

#SCRAP AND PUT ALL PLAYERS IN THE DATABASE
for letter_url in all_letters_url_list:
    letter_page = r.get(letter_url)
    letter_soup = BeautifulSoup(letter_page.text, 'lxml')

    players_table = letter_soup.find('table', id='players').find('tbody')
    all_tr = players_table.find_all('tr')
    
    for tr in all_tr:
        player_href = tr.find('th').find('a')['href']
        player_url = urljoin('https://www.basketball-reference.com', player_href)
        insert_player_data(player_url)


'''
#TEST WITH ONE PLAYER
op_url = 'https://www.basketball-reference.com/players/j/jordami01.html'
insert_player_data(op_url)
'''