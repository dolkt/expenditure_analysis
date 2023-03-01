"""
Module for creating the database"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np
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




def check_latest_date(user_id: int, db = engine):
    """
    Pulls the latest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the latest date
    """

    #Changes the current working directory to the database folder.

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
    
    #Closes the connection with the sqlite database.
    db_connection.close()

    if len(df) == 0:
        return pd.to_datetime(0)

    return df["Transaktionsdatum"].iloc[0]


def check_earliest_date(user_id: int, db = engine):
    """
    Pulls the earliest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the earliest date
    """

    #Establishes connection the postgres database.
    db_connection = db.connect()

    query = f'''
    SELECT "Transaktionsdatum" from expenditures
    WHERE user_id = {user_id}
    ORDER BY "Transaktionsdatum" ASC
    '''

    #Reads the earliest (oldest) date from the database
    df = pd.read_sql(sql=text(query), con=db_connection)

    if len(df) == 0:
        return pd.to_datetime(0)
    
    #Closes the connection with the sqlite database.
    db_connection.close()

    return df["Transaktionsdatum"].iloc[0]


def get_uncategorized(user_id: int, db = engine) -> pd.DataFrame:


    db_connection = db.connect()

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


def get_user_categories(user_id: int, usage: str, db = engine):


    db_connection = db.connect()

    query = f'''
    SELECT name, text FROM categories
    WHERE user_id = {user_id}
    '''

    df = pd.read_sql(sql=text(query), con=db_connection)

    db_connection.close()

    if usage == "display":
        df["name"] = df["name"].str.capitalize()
        df.columns = df.columns.str.capitalize()
        return df
    
    if usage == "cost_categorization":
        df = df.replace("", np.nan).dropna(subset=["text"])
        return df

