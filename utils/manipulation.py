"""Module for cleaning and categorizing data"""
import pandas as pd
import numpy as np
import regex as re
import streamlit as st
import models
import datetime
from typing import Union, Dict, List
from database import get_db, SessionLocal, get_user_categories


def categorization(frame: pd.DataFrame, user_id: int) -> pd.DataFrame:
    """
    Cleans the data and places transactions in provided categories

    --------
    Parameters
    frame: pd.DataFrame
        The provided DataFrame to clean and perform categorization on.
    user_id: int
        The user_id to retrieve the categories for.

    --------    
    Returns
    frame: pd.DataFrame
        Containing the transactions with it's assigned categories.
    """

    #Cleans the DataFrame and puts the first entry as the column names.
    frame.rename(columns=frame.iloc[0], inplace=True)
    frame.drop(frame.index[0], inplace=True)

    #Drops uneccessary columns
    frame.drop(columns="Reskontradatum", inplace=True)
    frame.dropna(axis=1, inplace=True)


    #Data cleaning. Some values contain "," and " ". While others are incremented by 100.
    frame["Belopp"] = (frame["Belopp"].apply(lambda x: int(x)/100 if (" " not in x)
                        else (x.replace(",", ".").replace(" ", ""))
                                            )
                    )
    frame["Saldo"] = frame["Saldo"].str.replace(" ", "").str.replace(",", ".").astype(float)
    

    #Setting the d-types for the columns
    frame["Belopp"] = frame["Belopp"].astype(float)
    frame["Transaktionsdatum"] = frame["Transaktionsdatum"].apply(pd.to_datetime)

    #Sets a new column based on whether the transaction is income or cost.
    frame["Typ"] = np.where(frame["Belopp"] > 0, "Inkomst", "Kostnad")

    #Creating a dictionary containing the categories as keys.
    categories = categories_dict(user_id=user_id)

    #Sets a new column for the categorization of the transactions.
    frame["Kategori"] = ""
    for key, value in categories.items():
        frame["Kategori"] = np.where((frame["Typ"] == "Kostnad") & (frame["Text"].str.contains("|".join(value), regex=True, flags=re.IGNORECASE)),
                            str(key), frame["Kategori"])

    #Sets the category column to "Other" if cost could not be categorized.
    frame["Kategori"] = np.where((frame["Typ"] == "Kostnad") & (frame["Kategori"] == ""), "Other", frame["Kategori"])

    return frame


def add_expenditure(date: datetime.datetime, category: str, amount: float, user_id: int, text: Union[str, None] = None) -> pd.DataFrame:
    """
    Creates a dataframe of the user provided data and places it in the correct columns so that it can be uploaded to the database.

    --------
    Parameters
    date: datetime.datetime
        Containing the date when the transaction happened (according to the user)
    category: str
        Which category the transaction should belong to (according to the user)
    amount: float
        The amount of the transaction (according to the user)
    user_id: int
        The id of the current user
    text: Union[str, None]
        Optional entry of the user.

    --------    
    Returns
    new_table: pd.DataFrame
        Dataframe containing the fields provided by the user.
    """
    
    data = {
        "Transaktionsdatum": date,
        "Text": text,
        "Belopp": amount * -1 if amount > 0 else amount, #Automatically converts to negative amount.
        "Typ": "Kostnad",
        "Kategori": category,
        "user_id": user_id
    }

    new_table = pd.DataFrame([data])

    return new_table

def add_income(date: datetime.date, amount: float, user_id: int) -> pd.DataFrame:
    """
    Creates a dataframe of the user provided data and places it in the correct columns so that it can be uploaded to the database.

    --------
    Parameters
    date: datetime.datetime
        Containing the date when the transaction happened (according to the user)
    amount: float
        The amount of the transaction (according to the user)
    user_id: int
        The id of the current user
    
    --------
    Returns
    new_table: pd.DataFrame
        Dataframe containing the fields provided by the user.
    """

    data = {
        "Transaktionsdatum": date,
        "Belopp": amount * -1 if amount < 0 else amount, #Automatically converts to a positive amount.
        "Typ": "Inkomst",
        "user_id": user_id
    }

    return pd.DataFrame([data])

def add_category(category_name: str, category_text: str, user_id: int, db: SessionLocal = next(get_db())) -> None:
    """
    Function to add category for the given user
    
    --------
    Parameters
    category_name: str
        Name of the category (provided by the user)
    category_text: str
        Is an optional parameter in the application (provided by the user)
    user_id: int
        The id of the current user
    db: sqlalchemy.orm.sessionmaker
        Connects to the database and sets up a session.
    """

    #Removes whitespace leading and trailing whitespace
    category_name = category_name.rstrip().lstrip()
    category_text = category_text.rstrip().lstrip()

    #Checks whether a category with the name already exists
    existing_category = db.query(models.Categories).filter(models.Categories.user_id == user_id, models.Categories.name == category_name).first()

    if category_name.strip() is None:
        return st.warning("Please provide a name")

    if existing_category:
        return st.error("Category with that name already exist!")

    category_model = models.Categories()

    category_model.name = category_name
    category_model.text = category_text
    category_model.user_id = user_id

    db.add(category_model)

    db.commit()

    return st.success("Category was added!")

def update_category(category_name: str, category_text: str, user_id: int, db: SessionLocal = next(get_db())) -> None:
    """
    Updates a current category with texts (in the transaction file) that can identify it.
    This is only used for users who utilize the File Upload functionality.
    
    --------
    Parameters
    category_name: str
        Name of the category (provided by the user)
    category_text: str
        The text that can identify the given category (provided by the user)
    user_id: int
        The id of the current user.
    db: sqlalchemy.orm.sessionmaker
        Connects to the database and sets up a session.
    """

    #Removes leading and trailing whitespace.
    category_text = category_text.rstrip().lstrip()

    if category_name == None:
        return st.error("You need to add a category first.")

    #Checks if the current text already exists within the database for the given user.
    existing_text = db.query(models.Expenditures).filter(models.Expenditures.user_id == user_id, models.Expenditures.Text == category_text).all()

    #If the texts already exists it will update and place all the transactions (with this text) to the given category.
    if existing_text:
        db.query(models.Expenditures).filter(
            models.Expenditures.user_id == user_id, models.Expenditures.Text == category_text).update(
            {models.Expenditures.Kategori:category_name}, synchronize_session = False)
        
        db.commit()
        
        st.success(f"{len(existing_text)} expenditure(s) containing {category_text} were updated to {category_name}")
    
    category_model = models.Categories()

    category_model.name = category_name
    category_model.text = category_text
    category_model.user_id = user_id

    db.add(category_model)

    db.commit()

    return st.success("Category was successfully edited")


def delete_category(category_name: str, user_id: int, db: SessionLocal = next(get_db())) -> None:
    """
    Firstly it changes the existing expenditures (if any) to the category 'Other' from the category that is
    being deleted for the given user.
    Secondly it deletes the given category from the database
    
    --------
    Parameters
    category_name: str
        The category that is being deleted.
    user_id:
        The id of the current user.
     db: sqlalchemy.orm.sessionmaker
        Connects to the database and sets up a session.
    """
    
    #Recategorizes the expenditures currently within 'category_name' to 'Other' for the given user
    db.query(models.Expenditures).filter(
        models.Expenditures.Kategori == category_name, models.Expenditures.user_id == user_id
    ).update({models.Expenditures.Kategori:"Other"}, synchronize_session = False)

    st.warning(f"Expenditures catagorized as {category_name} are now recategorized as 'Other'")

    #Deletes 'category_name' from the database for the given user.
    db.query(models.Categories).filter(
        models.Categories.name == category_name, models.Categories.user_id == user_id
    ).delete()

    #Commits both the actions above
    db.commit()

    st.success(f"{category_name} was successfully deleted!")



def categories_dict(user_id: int) -> Dict[str, List[str]]:
    """
    Helper function used for the categorization of expenditures provided by a file.
    Adds all the categories and it's corresponding texts that identify it to a dictionary.
    The key in the dictionary will be the category and the values will be the texts
    that identify the given category within the key
    
    --------
    Parameters
    user_id:
        The id of the current user.

    --------
    Returns
    categories_dict: dict
        Key-value pair of the user's category (key) and each category's identifying texts (values).
    """

    #Calls the database and gets all the categories for the given user
    df = get_user_categories(user_id=user_id, usage="cost_categorization")

    #Iterates over the dataframe holding all the categories and corresponding texts and adds it to a dictionary.
    categories_dict = {}
    for _, row in df.iterrows():
        if row["name"] not in categories_dict:
            categories_dict[row["name"]] = [row["text"]]
        else:
            categories_dict[row["name"]].append(row["text"])

    return categories_dict

