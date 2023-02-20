"""
Module for creating the database"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import pandas as pd
import os


def connect_db(key):
    """
    Returns the database url from the enviroment files.
    Will work on local as well as cloud solutions"""

    load_dotenv()

    return os.getenv(key)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()

    
DATABASE_URL = connect_db("db_url")

engine = create_engine(url=DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()




def check_latest_date(db = engine):
    """
    Pulls the latest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the latest date
    """

    #Changes the current working directory to the database folder.

    #Establishes connection the postgres database.
    db_connection = db.connect()

    query = "SELECT * FROM expenditures"

    #Reads the latest (newest) date from the database
    df = pd.read_sql(sql=text(query), con=db_connection)
    
    #Closes the connection with the sqlite database.
    db_connection.close()

    if len(df) == 0:
        return pd.to_datetime(0)

    return df["Transaktionsdatum"].iloc[0]


def check_earliest_date(db = engine):

    """
    Pulls the earliest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the earliest date
    """

    #Establishes connection the postgres database.
    db_conn = db.connect()

     #Reads the earliest (oldest) date from the database
    df = pd.read_sql(f"""SELECT Transaktionsdatum FROM Transactions
                        #ORDER BY Transaktionsdatum LIMIT 1""", con=db_conn)
    
    #Closes the connection with the sqlite database.
    db_conn.close()

    return df["Transaktionsdatum"].iloc[0]


