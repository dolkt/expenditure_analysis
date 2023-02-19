from logging import exception
import streamlit as st
import pandas as pd
import utils
import database
import models


#Setting the title for the page as well as the icon displayed in the browser tab
st.set_page_config(page_title="Upload Data", page_icon="💾")


#Header for the page
st.subheader("Upload Transaction Data")

#File upload functionality. Restricted to .xls.
chosen_file = st.file_uploader(label="Choose a file", help="Select a transactionfile from Handelsbanken",
                                type="xls")

#Stops the page if no file is uploaded
if not chosen_file:
    st.stop()

#Reads the user provided xls.
df = pd.read_html(chosen_file)[3] 

#Categorizes the costs based on the parameters in the categorization function
df = utils.categorization(df)

df["user_id"] = st.session_state["user_id"]

#Shows sample data from the provided xls.
st.write("Sample from the data to upload:", df.head())
st.write(df["Belopp"].dtype)

#Prompts the user whether they want to upload the data to the database
upload_prompt = st.button("Upload to database?")

#If upload is selected it checks db for the latest provided date and masks
#the provided file from that date.
if upload_prompt:

    date_checker = database.check_latest_date(user_id=st.session_state["user_id"])
    
    df = df[df["Transaktionsdatum"] > date_checker]

    if len(df) > 1:
        #database.upload_data(df)
        df.to_sql(con=database.engine, name=models.Expenditures.__tablename__, if_exists="append", index=False)
        st.success("Data was uploaded", icon="✔")
    else:
         st.error("All that data is already in the database")
         #st.stop()


st.session_state

st.write(database.check_earliest_date(user_id=st.session_state["user_id"]))
st.write(database.check_latest_date(user_id=st.session_state["user_id"]))


with st.form("expenditure_form"):

    st.number_input("Starting Balance within the month (Optional)", step=int(1))
    st.date_input("Date (Obligatory)")
    st.selectbox("Type", options=["Inkomst", "Kostnad"])
    st.number_input("Amount", step=int(1))