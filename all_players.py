from bs4 import BeautifulSoup
import requests as r
from player import insert_player_data

#SET SOUP
url = 'https://www.basketball-reference.com/players'
page = r.get(url)
soup = BeautifulSoup(page.text, 'lxml')

#SET ALL LETTERS LINKS LIST
all_a = soup.find_all('a')
all_letters_href = [a['href'] for a in all_a if len(a.text) == 1]

'''
#TEST WITH ONE PLAYER
op_url = 'https://www.basketball-reference.com/players/j/jordami01.html'
insert_player_data(op_url)
'''