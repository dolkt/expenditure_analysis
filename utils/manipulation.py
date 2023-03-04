"""Module for cleaning and categorizing data"""
import pandas as pd
import numpy as np
import regex as re
import streamlit as st
import models
from typing import Union
from database import get_db, SessionLocal, get_user_categories


def categorization(frame, user_id: int) -> pd.DataFrame:
    """Cleans the data and places transactions in provided categories

    Keyword arguments:
    frame -- The provided DataFrame to clean and perform categorization on

    Returns DataFrame
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


def add_expenditure(date, category: str, amount: float, user_id: int, text: Union[str, None] = None):

    data = {
        "Transaktionsdatum": date,
        "Text": text,
        "Belopp": amount * -1 if amount > 0 else amount,
        "Typ": "Kostnad",
        "Kategori": category,
        "user_id": user_id
    }

    new_table = pd.DataFrame([data])

    return new_table

def add_category(category_name: str, category_text: str, user_id: int, db: SessionLocal = next(get_db()), customized: bool = False):

    category_name = category_name.lower().rstrip().lstrip()
    category_text = category_text.lower().rstrip().lstrip()

    existing_category = db.query(models.Categories).filter(models.Categories.user_id == user_id, models.Categories.name == category_name).first()

    if category_name.strip() is None:
        return st.warning("Please provide a name")

    if existing_category and not customized:
        return st.error("Category with that name already exist!")

    
    category_model = models.Categories()

    category_model.name = category_name
    category_model.text = category_text
    category_model.user_id = user_id

    db.add(category_model)

    db.commit()

    return st.success("Category was added!")

def update_category(category_name: str, category_text: str, user_id: int, db: SessionLocal = next(get_db())):

    category_text = category_text.rstrip()

    existing_text = db.query(models.Expenditures).filter(models.Expenditures.user_id == user_id, models.Expenditures.Text == category_text).all()

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


def categories_dict(user_id: int) -> dict:

    df = get_user_categories(user_id=user_id, usage="cost_categorization")

    categories_dict = {}

    for _, row in df.iterrows():
        if row["name"] not in categories_dict:
            categories_dict[row["name"]] = [row["text"]]
        else:
            categories_dict[row["name"]].append(row["text"])

    return categories_dict

