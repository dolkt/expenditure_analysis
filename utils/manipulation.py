"""Module for cleaning and categorizing data"""
import pandas as pd
import numpy as np
import regex as re



def categorization(frame):
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

    #Setting the d-types for the columns
    frame["Belopp"] = frame["Belopp"].astype(float)
    frame["Transaktionsdatum"] = frame["Transaktionsdatum"].apply(pd.to_datetime)

    #Sets a new column based on whether the transaction is income or cost.
    frame["Typ"] = np.where(frame["Belopp"] > 0, "Inkomst", "Kostnad")

    #Creating a dictionary containing the categories as keys.
    categories = {"Rent":["ga fastighet", "stenbackahus", "överf internet"],
                "Subscriptions":["hbo", "netflix", "rewell", "medium", "saga motion", "whoop", "disney"],
                "Food":["coop", "ica", "willys"],
                "Fast Food":["uber \*eats", "foodora", "subway", "mcdonalds"],
                "Travel":["sl", "ab storstockho", "ul kollektivtr", "uber \*trip", "taxi"],
                "Clothes":["massimo", "nk", "ahlens", "nk", "zalando"],
                "Health":["apotek"],
                "Installments": ["centrala"]}

    #Sets a new column for the categorization of the transactions.
    frame["Kategori"] = ""
    for key, value in categories.items():
        frame["Kategori"] = np.where((frame["Typ"] == "Kostnad") & (frame["Text"].str.contains("|".join(value), regex=True, flags=re.IGNORECASE)),
                            str(key), frame["Kategori"])

    #Sets the category column to "Other" if cost could not be categorized.
    frame["Kategori"] = np.where((frame["Typ"] == "Kostnad") & (frame["Kategori"] == ""), "Other", frame["Kategori"])

    return frame
