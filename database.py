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

<<<<<<< HEAD
    #The double quotation marks around the column name forces it to be case sensitive
    query = f'''
    SELECT "Transaktionsdatum" from expenditures
    WHERE user_id = {user_id}
    ORDER BY "Transaktionsdatum" DESC
    '''
=======
    query = "SELECT * FROM expenditures"
>>>>>>> cbe27471d72ec34f6f7b3846b885776a89aa130a

    #Reads the latest (newest) date from the database
    df = pd.read_sql(sql=text(query), con=db_connection)
    
    #Closes the connection with the sqlite database.
    db_connection.close()

    if len(df) == 0:
        return pd.to_datetime(0)

    return df["Transaktionsdatum"].iloc[0]


<<<<<<< HEAD
def check_earliest_date(user_id: int, db = engine):
=======
def check_earliest_date(db = engine):

>>>>>>> cbe27471d72ec34f6f7b3846b885776a89aa130a
    """
    Pulls the earliest date from the internal database
    
    -----
    Returns
    pandas.Series object containing the earliest date
    """

    #Establishes connection the postgres database.
<<<<<<< HEAD
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


def get_column_names(db = engine):


    db_connection = db.connect()

    query = '''
    SELECT * FROM expenditures
    WHERE  false
    '''
=======
    db_conn = db.connect()

     #Reads the earliest (oldest) date from the database
    df = pd.read_sql(f"""SELECT Transaktionsdatum FROM Transactions
                        #ORDER BY Transaktionsdatum LIMIT 1""", con=db_conn)
    
    #Closes the connection with the sqlite database.
    db_conn.close()

    return df["Transaktionsdatum"].iloc[0]
>>>>>>> cbe27471d72ec34f6f7b3846b885776a89aa130a

    df = pd.read_sql(sql=text(query), con=db_connection)

    db_connection.close()

<<<<<<< HEAD
    return df
=======
>>>>>>> cbe27471d72ec34f6f7b3846b885776a89aa130a
