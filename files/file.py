"""Module for handling files that are eligible for uploading to the database"""
from pathlib import Path
import os
import pandas as pd


def chosen_file():
    """Lists all the files with .xls extension in the directory.
    Then let's the user choose which .xls file.
    Finally, the chosen file is populated into a DataFrame
    
    Returns a DataFrame
    """

    #Changed the current working directory to the folder holding the files.
    os.chdir(Path(__file__).parent)

    #Puts all the files with .xls extension and populates it into a dictionary.
    file_dict = {}
    for num, file in enumerate(os.listdir()):
        if file.endswith(".xls"):
            file_dict[str(num)] = file

    #Lists the files in the dictionary for the user
    print("Eligible files for analysis:")
    for key, value in file_dict.items():
        print(f"{[key]}: {value}")

    #Lets the user choose which file to upload to the sqlite database.
    chosen_key = input("Press the numeric [x] key for the data you want to upload: ")
    user_input = file_dict.get(chosen_key)

    #Reads the chosen file and populates it into a DataFrame.
    df = pd.read_html(user_input)[3] #3 is used since that slice holds all data.

    return df
    