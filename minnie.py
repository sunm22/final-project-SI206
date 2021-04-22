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

def covid_table(cur, conn, state, date, positive):
    #STATE MUST BE LOWERCASE
    '''This function takes in cursor and connection variables to database, state,
    date, and number of positive COVID cases for that state. It creates a table in the database
    if it doesn't exist and inserts the state, date, and number of positive cases. Returns nothing.'''

    cur.execute('CREATE TABLE IF NOT EXISTS CovidData ("id" INTEGER PRIMARY KEY, "state" TEXT, "date" NUMBER, "number_of_cases" NUMBER)')
    cur.execute('INSERT INTO CovidData (state, date, number_of_cases) VALUES (?, ?, ?)', (state, date, positive))
    conn.commit()

def percent_change_table(cur, conn, state, percent):
    #STATE MUST BE LOWERCASE
    '''This function takes in cursor and connection variables to database, state,
    and percent change calculated from percent_change. It creates a table in the database
    if it doesn't exist and inserts the state and percent change. Returns nothing.'''

    cur.execute('CREATE TABLE IF NOT EXISTS PercentChange ("state" TEXT, "percent_change" NUMBER)')
    cur.execute('INSERT INTO PercentChange (state, percent_change) VALUES (?, ?)', (state, percent))
    conn.commit()

def covid_table_length(cur, conn):
    '''This function calculates the number of rows in the CovidData table to help with extracting
    25 lines at a time. Returns the number of rows in the table as an int.'''
    cur.execute('CREATE TABLE IF NOT EXISTS CovidData ("id" INTEGER PRIMARY KEY, "state" TEXT, "date" NUMBER, "number_of_cases" NUMBER)')
    cur.execute('SELECT id FROM CovidData')
    data = cur.fetchall()
    num = len(data)

    return num
    

##################################################################

def get_mar_data(cur, conn, state):
    '''This function takes in the cursor and connection variables, and the lowercase state abbreviation.
    It sends requests to COVID Tracking Project API for the latest data for the given state (mostly March 7th 2021, as that's when
    the project ended). Uses json to extract date and number of positive cases. Calls covid_table to create and add to table.
    Returns nothing.'''
    
    url_2021 = f"https://api.covidtracking.com/v1/states/{state}/current.json"
    req = requests.get(url_2021)
    curr_info = json.loads(req.text)

    #extract date and positive cases
    curr_date = curr_info["date"]
    curr_positive = curr_info["positive"]

    if curr_positive == 'null':
        print("2021 info not found")

    #add to table
    covid_table(cur, conn, state, curr_date, curr_positive)

def get_feb_data(cur, conn, state):
    '''This function takes in the cursor and connection variables, and the lowercase state abbreviation.
    It sends requests to COVID Tracking Project API for February 7th, 2021 data for the given state.
    Uses json to extract date and number of positive cases. Calls covid_table to create and add to table.
    Returns nothing.'''
    url = f"https://api.covidtracking.com/v1/states/{state}/daily.json"
    req = requests.get(url)
    curr_info = json.loads(req.text)
    curr_info.reverse()

    feb_7_2021 = 20210207
    positive = 0

    #extract positive cases
    for day in curr_info:
        if day["date"] == feb_7_2021:
            positive = day["positive"]

    if positive == 'null':
        print("Feb info not found")

    #add to table
    covid_table(cur, conn, state, feb_7_2021, positive)

def percent_change(cur, conn, state):
    '''This function takes in cursor and connection variables, and the lowercase state abbreviation.
    It calculates the percent change from Feb 2021 to Mar 2021 in number of COVID cases for the given state.
    It adds the information to the PercentChange table by calling percent_change_table().
    Returns nothing.'''
    cur.execute('SELECT number_of_cases FROM CovidData WHERE state=?', [state])

    row_count = 1
    positive_feb = 0
    positive_mar = 0
    for row in cur:
        if row_count == 1:
            positive_feb = row[0]
        if row_count == 2:
            positive_mar = row[0]
        row_count = row_count + 1
            
    percent = (positive_mar - positive_feb) / positive_feb * 100
    percent_change_table(cur, conn, state, percent)

def percent_change_viz(cur, conn):
    '''This function takes in the cursor and connection variables. It uses matplotlib to create a bar graph
    of the 10 states with highest % increase in COVID cases from Feb 2021 to Mar 2021 by using the PercentChange table.
    Output is the creation of the graph.'''
    percent_list = []
    cur.execute('SELECT state, percent_change FROM PercentChange')
    for row in cur:
        percent_list.append(row)
    percent_list = sorted(percent_list, key = lambda x: x[1], reverse=True)

    top_ten = percent_list[:10]

    x = []
    y = []

    for item in top_ten:
        x.append(item[0])
        y.append(item[1])

    x_pos = [i for i, _ in enumerate(x)]

    plt.bar(x_pos, y, color='green')
    plt.xlabel('State')
    plt.ylabel('Percent Change (%)')
    plt.title('Highest percent changes in COVID cases from Feb 2021 to Mar 2021')

    plt.xticks(x_pos, x)

    plt.show()

def highest_positives_viz(cur, conn):
    '''This function takes in the cursor and connection variables. It uses matplotlib to create a bar graph
    of the 10 states with highest # of COVID cases in Mar 2021 by using the CovidData table.
    Output is the creation of the graph.'''
    positives_list = []
    cur.execute('SELECT state, number_of_cases FROM CovidData WHERE date = 20210307')
    for row in cur:
        positives_list.append(row)
    positives_list = sorted(positives_list, key = lambda x: x[1], reverse=True)

    top_ten = positives_list[:10]

    x = []
    y = []

    for item in top_ten:
        x.append(item[0])
        y.append(item[1])

    x_pos = [i for i, _ in enumerate(x)]

    plt.bar(x_pos, y, color='blue')
    plt.xlabel('State')
    plt.ylabel('Positive Cases on Mar 7, 2021 (millions)')
    plt.title('Highest positive cases by state in Mar 2021')

    plt.xticks(x_pos, x)

    plt.show()

def main():
    '''Main includes two state abbreviation lists with 25 states in each. It calls covid_table_length() and
    uses the results to determine what set of data to collect, storing 25 rows each time until CovidData is
    populated with 100 rows. Then calcuates and populates PercentChange. Creates all visualizations.
    Returns nothing.'''
    cur, conn = setUpDatabase("finalProject.db")

    states_list_1 = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo']
    states_list_2 = ['mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy']

    num = covid_table_length(cur, conn)
    if num == 0:
        print("1")
        for state in states_list_1:
            get_feb_data(cur, conn, state)
        return

    elif num <= 25:
        print("2")
        for state in states_list_2:
            get_feb_data(cur, conn, state)
        return

    elif num <= 50:
        print("3")
        for state in states_list_1:
            get_mar_data(cur, conn, state)
        return
    
    elif num <= 75:
        print("4")
        for state in states_list_2:
            get_mar_data(cur, conn, state)
    
    print("percent 1")
    for state in states_list_1:
        percent_change(cur, conn, state)

    print("percent 2")
    for state in states_list_2:
        percent_change(cur, conn, state)
    
    highest_positives_viz(cur, conn)
    percent_change_viz(cur, conn)

    cur.close()

if __name__ == '__main__':
    main()