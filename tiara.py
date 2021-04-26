import requests
import sqlite3
import json
import os 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt 

#
# Name: Mingxuan Sun
# Who did you work with: Tiara Amadia
#


def setUpDatabase(db_name):
    '''This function takes in the name of the database, makes a connection to server
    using nane given, and returns cur and conn as the cursor and connection variable
    to allow database access.'''
    
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def pop_table(cur, conn, state, population): 
    """ this function takes in cursor and connection variables to database, state, year and number of US Population for that state. It creates a table in the database if it doesn't exist and inserts the state, date and number of population. Returns nothing """
   
    cur.execute('CREATE TABLE IF NOT EXISTS Population Data (2020/2010) ("id" INTEGER PRIMARY KEY, "state" TEXT, "population" NUMBER)')
    cur.execute('INSERT INTO Population Data (state, population) VALUES (?, ?)', (state, population))
    conn.commit()


############################################################

 
def get_pop_2020(soup): 
    table = soup.find('table',{'class':'wikitable sortable'})
    body = table.find('tbody')
    all_rows = body.find_all('tr')

    key_pop_2020_dict = {}

    for row in all_rows[2:53]: 
        row_cells = row.find_all('td')
        key = row_cells[2].text.strip()
        value = row_cells[3].text.strip()
        key_pop_2020_dict[key] = value

    return key_pop_2020_dict

def get_pop_2010(soup): 
    table = soup.find('table',{'class':'wikitable sortable'})
    body = table.find('tbody')
    all_rows = body.find_all('tr')

    key_pop_2010_dict = {}

    for row in all_rows[2:53]: 
        row_cells = row.find_all('td')
        key = row_cells[2].text.strip()
        value = row_cells[4].text.strip()
        key_pop_2010_dict[key] = value

    return key_pop_2010_dict


def main(): 
    soup = BeautifulSoup(requests.get('https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States_by_population').text, 'html.parser')
    get_pop_2020(soup)
    get_pop_2010(soup)

if __name__ == "__main__":
    main()
      