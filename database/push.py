"""
The module that handles data uploads to the project's sqlite database
"""
import os
import sqlite3
import pandas as pd
from pathlib import Path


def upload_data(frame):
    """Uploads the data within the DataFrame to the project's sqlite database
    
    Keyword arguments:
    frame -- The provided DataFrame to upload to the sqlite database
    """

    #Changes the current working directory to the database folder.
    os.chdir(Path(__file__).parent)

    #Establishes connection the sqlite database.
    conn = sqlite3.connect("transactions_db.sqlite")
    
    #Uploads the provided DataFrame to the sqlite database.
    frame.to_sql("Transactions", #Transactions is the table name within the database transactions_db.sqlite
    con=conn,
    if_exists="replace", #Will replace current data if it is duplicate.
    index=False, #Does not use the index of the DataFrame as a seperate column in the sqlite database.
    dtype={"Transaktionsdatum": "Date", "Text": "Text", #Provides the datatype of each column of the DataFrame.
            "Belopp": "Float", "Typ": "Text",
            "Kategori": "Text"}
                )

    #Closes the connection with the sqlite database.
    conn.close()
