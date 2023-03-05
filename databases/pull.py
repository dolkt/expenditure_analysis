"""The module that handles querying from the project's sqlite database
"""
from pathlib import Path
import os
import sqlite3
import pandas as pd


def pull_data(start_month):
    """Pulls data from the project's sqlite database from a chosen date interval. 
    
    Keyword arguments:
    start_,month - datetime object formated as %b-%Y
    
    Returns a DataFrame with all the data for that date interval"""
    
    #Changes the current working directory to the database folder.
    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")
    
    #Populates a DataFrame with data from the provided SQL-query to the project's sqlite database.
    df = pd.read_sql(f"""SELECT * FROM Transactions
                        WHERE Transaktionsdatum 
                        >= '{start_month}':: date
                        """, con=conn)
    
    #Changes format of the Transaktionsdatum column to datetime
    df["Transaktionsdatum"] = df["Transaktionsdatum"].apply(pd.to_datetime)
    
    #Closes the connection with the sqlite database.
    conn.close()


    return df


def check_latest_date():
    """
    Pulls the latest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the latest date
    """

    #Changes the current working directory to the database folder.
    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")

    #Reads the latest (newest) date from the database
    df = pd.read_sql(f"""SELECT Transaktionsdatum FROM Transactions
                        ORDER BY Transaktionsdatum DESC LIMIT 1""", con=conn)
    
    #Closes the connection with the sqlite database.
    conn.close()

    return df["Transaktionsdatum"].iloc[0]


def check_earliest_date():
    """
    Pulls the earliest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the earliest date
    """

    #Changes the current working directory to the database folder.
    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")

     #Reads the earliest (oldest) date from the database
    df = pd.read_sql(f"""SELECT Transaktionsdatum FROM Transactions
                        ORDER BY Transaktionsdatum LIMIT 1""", con=conn)
    
    #Closes the connection with the sqlite database.
    conn.close()

    return df["Transaktionsdatum"].iloc[0]