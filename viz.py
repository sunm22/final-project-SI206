import requests
import sqlite3
import json
import os
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import csv

def setUpDatabase(db_name):
    '''This function takes in the name of the database, makes a connection to server
    using name given, and returns cur and conn as the cursor and connection variable
    to allow database access.'''
    
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def percent_change_viz(cur, conn):
    '''This function takes in the cursor and connection variables. It uses matplotlib to create a bar graph
    of the 10 states with highest % increase in COVID cases from Dec 2020 to Mar 2021 by using the PercentChange table.
    Output is the creation of the graph.'''
    percent_list = []
    cur.execute('SELECT States.state, PercentChange.percent_change FROM PercentChange JOIN States ON PercentChange.state_id = States.state_id')
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
    plt.title('Highest percent changes in COVID cases from Dec 2020 to Mar 2021')

    plt.xticks(x_pos, x)

    plt.show()

def highest_positives_viz(cur, conn):
    '''This function takes in the cursor and connection variables. It uses matplotlib to create a bar graph
    of the 10 states with highest # of COVID cases in Mar 2021 by using the CovidData table.
    Output is the creation of the graph.'''
    positives_list = []
    cur.execute('SELECT States.state, Dates.date, CovidData.number_of_cases FROM CovidData JOIN States JOIN Dates ON CovidData.state_id = States.state_id and CovidData.date_id = Dates.date_id')
    for row in cur:
        if row[1] == '20210307':
            positives_list.append(row)
    positives_list = sorted(positives_list, key = lambda x: x[2], reverse=True)

    top_ten = positives_list[:10]

    x = []
    y = []

    for item in top_ten:
        x.append(item[0])
        y.append(item[2])

    x_pos = [i for i, _ in enumerate(x)]

    plt.bar(x_pos, y, color='blue')
    plt.xlabel('State')
    plt.ylabel('Positive Cases on Mar 7, 2021 (millions)')
    plt.title('Highest positive cases by state in Mar 2021')

    plt.xticks(x_pos, x)

    plt.show()

def main():
    cur, conn = setUpDatabase("finalProject.db")
    percent_change_viz(cur, conn)
    highest_positives_viz(cur, conn)

if __name__ == "__main__":
    main()