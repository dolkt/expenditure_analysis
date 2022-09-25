"""The module that handles querying from the project's sqlite database
"""
from pathlib import Path
import os
import sqlite3
import pandas as pd


def pull_data(start_date, end_date):
    """Pulls data from the project's sqlite database from a chosen date interval. 
    
    Keyword arguments:
    start_date -- The starting date for the date interval
    end_date -- The ending date for the date interval
    
    Returns a DataFrame with all the data for that date interval"""
    
    #Changes the current working directory to the database folder.
    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")
    
    #Populates a DataFrame with data from the provided SQL-query to the project's sqlite database.
    df = pd.read_sql(f"""SELECT * FROM Transactions
                        WHERE strftime('%Y-%m', Transaktionsdatum) 
                        BETWEEN '{start_date}' AND '{end_date}'
                        """, con=conn)
    
    #Changes format of the Transaktionsdatum column to datetime
    df["Transaktionsdatum"] = df["Transaktionsdatum"].apply(pd.to_datetime)
    
    #Closes the connection with the sqlite database.
    conn.close()


    return df


def check_data():

    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")

    df = pd.read_sql(f"""SELECT Transaktionsdatum FROM Transactions
                        ORDER BY Transaktionsdatum DESC LIMIT 1""", con=conn)
    
    conn.close()

    return df["Transaktionsdatum"].iloc[0]