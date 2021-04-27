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

def pop_table(cur, conn, pop_dict, date, count): 
    """ this function takes in cursor and connection variables to database, state, year and number of US Population for that state. It creates a table in the database if it doesn't exist and inserts the state, date and number of population. Returns nothing """

    cur.execute('CREATE TABLE IF NOT EXISTS Population ("id" INTEGER PRIMARY KEY, "state" TEXT, "population" INTEGER)')

    # Inserting 50 states at a time into Population Database
    for x in pop_dict:
       
        cur.execute('INSERT INTO Population (id, state, population) VALUES (?, ?, ?)', (count, x + ":" + str(date), pop_dict[x]))
        count += 1
       
    conn.commit()

def population_chart(cur, conn):
    
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:

    label = []
    population = []

    # Grabbing Populations and States from the Database
    cursor = cur.execute("SELECT state, population FROM Population")
    for row in cursor:
        if row[0].split(":")[1] == "2020":
            label.append(row[0].split(":")[0])
            num = row[1]
            num = int(num.replace(',', ''))
            population.append(num)

    clearLabels = label[:8]
    for x in label[8:]:
        clearLabels.append("")

    fig1, ax1 = plt.subplots()
    ax1.pie(population, labels=clearLabels, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Total 2020 US Population by State")

    plt.show()

def percent_changes(cur, conn):

    labels2020 = []
    pop2020 = []

    # Grabbing Populations and States from the Database
    cursor = cur.execute("SELECT state, population FROM Population")
    for row in cursor:
        if row[0].split(":")[1] == "2020":
            labels2020.append(row[0].split(":")[0])
            num = row[1]
            num = int(num.replace(',', ''))
            pop2020.append(num)

    labels2010 = []
    pop2010 = []

    cursor = cur.execute("SELECT state, population FROM Population")
    for row in cursor:
        if row[0].split(":")[1] == "2010":
            labels2010.append(row[0].split(":")[0])
            num = row[1]
            num = int(num.replace(',', ''))
            pop2010.append(num)

    f = open("calculations.txt", "w+")
    for x in range(len(labels2010)):

        f.write(labels2010[x] + " has had a " + str(pop2020[x]/pop2010[x]) + " change in population\n")

    f.close()
        
        

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
    pop_2020 = get_pop_2020(soup)
    pop_2010 = get_pop_2010(soup)

    cur, conn = setUpDatabase("finalProject.db")
    # pop_table(cur, conn, pop_2020, "2020", 51)

    percent_changes(cur, conn)
    population_chart(cur, conn)
    

if __name__ == "__main__":
    main()
      