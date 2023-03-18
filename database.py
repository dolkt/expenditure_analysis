from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import os


def connect_db(key: str) -> str:
    """
    Returns the database url from the enviroment files.
    Will work on local as well as cloud solutions
    
    --------
    Parameters
    key: str
        The key in the key-value pair of the .env file that you want to return the value for

    --------
    Returns
    os.getenv(): str
        Value of the provided key.
    
    """

    load_dotenv()

    return os.getenv(key)

def get_db():
    """
    Helper function for some of the functions calling the database.
    Connects to the database and creates a session. Closes the session when the call to the database is done
    """

    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()

#Retrieves the database url from the enviroment variables.
DATABASE_URL = connect_db("db_url")

#Connects to the database
engine = create_engine(url=DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Sets up a boilerplate for the ORM to be used.
Base = declarative_base()




def check_latest_date(user_id: int, db = engine) -> pd.Series:
    """
    Pulls the latest date from the internal database

    --------
    Parameters
    user_id: int
        int of the current user within the application
    db: sqlalchemy.engine
        The database for the application
    
    --------
    Returns
    pandas.Series 
        Object containing the latest transactional date for the given user
    """

    #Establishes connection the postgres database.
    db_connection = db.connect()

    #The double quotation marks around the column name forces it to be case sensitive
    query = f'''
    SELECT "Transaktionsdatum" from expenditures
    WHERE user_id = {user_id}
    ORDER BY "Transaktionsdatum" DESC
    '''

    #Reads the latest (newest) date from the database
    df = pd.read_sql(sql=text(query), con=db_connection)
    
    #Closes the connection with the database.
    db_connection.close()

    #Returns 1970-01-01 if there is no entry in the database.
    if len(df) == 0:
        return pd.to_datetime(0)

    return df["Transaktionsdatum"].iloc[0]


def check_earliest_date(user_id: int, db = engine) -> pd.Series:
    """
    Pulls the earliest date from the internal database
    
    --------
    Parameters
    user_id: int
        int of the current user within the application
    db: sqlalchemy.engine
        The database for the application
    
    -------
    Returns
    pandas.Series
        Object containing the earliest transactional date for the given user
    """

    #Establishes connection the postgres database.
    db_connection = db.connect()

    #The double quotation marks around the column name forces it to be case sensitive
    query = f'''
    SELECT "Transaktionsdatum" from expenditures
    WHERE user_id = {user_id}
    ORDER BY "Transaktionsdatum" ASC
    '''

    #Reads the earliest (oldest) date from the database
    df = pd.read_sql(sql=text(query), con=db_connection)

    if len(df) == 0:
        return None
    
    #Closes the connection with the database.
    db_connection.close()

    return df["Transaktionsdatum"].iloc[0]


def get_cash_data(user_id: int, start_month: datetime, db = engine) -> pd.DataFrame:
    """
    Gets all the transactional data for the given user where the date condition is fulfilled.

    --------
    Parameters
    user_id: int
        int of the current user within the application
    start_month: datetime
        datetime formated as %Y-%m-%d
    db: sqlalchemy.engine
        The database for the application

    -------
    Returns
    pandas.DataFrame
        Containing all transactional data for the given user where the date condition is fulfilled.
    """

    #Connects to the database
    db_connection = db.connect()

    query = f'''
    SELECT * FROM expenditures
    WHERE "Transaktionsdatum" >= '{start_month}' AND user_id = {user_id}
    '''

    df = pd.read_sql(sql=text(query), con=db_connection)

    db_connection.close()

    return df


def get_uncategorized(user_id: int, db = engine) -> pd.DataFrame:
    """
    Gets all transactions which could not be categorized. Works for users who are using the File Upload functionality.

    --------
    Parameters
    user_id: int
        int of the current user within the application
    db: sqlalchemy.engine
        The database for the application

    --------
    Returns
    pandas.DataFrame
        Containing all transactional data for the given user where the category = 'Other'.
    """


    db_connection = db.connect()

    #Counts all occurances for a given text and summarizes the amount
    query = f'''
    SELECT COUNT(user_id) AS "Occurances", SUM("Belopp") AS "Spent", "Text"
    FROM expenditures
    WHERE  "Kategori" = 'Other' AND user_id = {user_id}
    GROUP BY "Text"
    ORDER BY "Occurances" DESC
    '''

    df = pd.read_sql(sql=text(query), con=db_connection)

    db_connection.close()

    return df


def get_user_categories(user_id: int, db = engine, usage: str = "cost_categorization") -> pd.DataFrame:
    """
    Retrieves all categories and the corresponding identifying text that a user has.
    
    ---------
    Parameters
    
    user_id: int
        The user_id to retrieve the categories for
    db: sqlalchemy.engine
        Connection to the database by using engine.connect()
    usage: str {'cost_categorization' or 'display} default 'cost_categorization'
        'cost_categorization' is used for the categorizing expenditures in a file
        'display' is used for displaying the expenditure categories without excluding
        the categories that do not have any identifying texts attached to them

    --------
    Returns
    df: pandas.DataFrame
        Containing all categories for the given user.
    """


    db_connection = db.connect()

    query = f'''
    SELECT name, text FROM categories
    WHERE user_id = {user_id}
    '''

    df = pd.read_sql(sql=text(query), con=db_connection)

    db_connection.close()

    #This is used for when the categories should be displayed to the user.
    if usage == "display":
        df.columns = df.columns.str.capitalize()
        return df
    
    #This is used in the automatic categorization within File Upload. Excludes categories with empty identifying texts.
    if usage == "cost_categorization":
        df = df.replace("", np.nan).dropna(subset=["text"])
        return df

