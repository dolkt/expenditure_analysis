from logging import exception
import streamlit as st
import pandas as pd
import utils
import database


st.set_page_config(page_title="Upload Data", page_icon="💾")

st.subheader("Upload Transaction Data")

chosen_file = st.file_uploader(label="Choose a file", help="Select a transactionfile from Handelsbanken",
                                type="xls")

if not chosen_file:
    st.stop()
df = pd.read_html(chosen_file)[3] 

df = utils.categorization(df)


st.write("Sample from the data to upload:", df.head())

upload_prompt = st.button("Upload to database?")


if upload_prompt:

    date_checker = database.check_latest_date()
    
    df = df[df["Transaktionsdatum"] > date_checker]

    if len(df) > 1:
        database.upload_data(df)
        st.success("Data was uploaded", icon="✔")
    else:
         st.exception("All that data is already in the database")

