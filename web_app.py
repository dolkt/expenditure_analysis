import numpy as np
import streamlit as st
import utils
import pandas as pd
import plotly.express as px
import datetime as dt


st.subheader("Upload Transaction Data")

chosen_file = st.file_uploader(label="Choose a file", help="Select a transactionfile from Handelsbanken",
                                type="xls")

if not chosen_file:
    st.stop()
df = pd.read_html(chosen_file)[3] 

df = utils.categorization(df)

st.subheader("Select Data")
st.markdown("Select a starting month to start the analysis from.")

START_DATE = dt.datetime(year=2018, month=1, day=1)
END_DATE = dt.datetime.today()

datelist = pd.date_range(start=START_DATE, end=END_DATE, freq="M")

starting_month = st.selectbox("Select month to start analyzing from", 
                            options=datelist.strftime("%b-%Y"), key="start_month")

st.subheader("Overview Level")
st.markdown("The overview level will visualize what the spending were on an aggregate level, month-by-month.  \n"
            "The page consists of three sub-pages  \n"
            "* **Monthly Savings/Loss** - This shows the profit / loss made within each month.  \n"
            "* **Total Balance over Time** - This shows the total savings over time in the given deposit account.  \n"
            "* **Detailed Month View** - This allows you to choose a month and get a detailed view of the spending.")

monthly_result, balace_over_time, detailed_month = st.tabs(["Monthly Savings/Loss", "Total Balance over Time", "Detailed Month View"])
with monthly_result:
    #Starting month is temp until SQL-selection is done.
    st.plotly_chart(utils.bar_plot(df, starting_month))
    #Find a way to make negative values red and positive green.
    #Bonus if greener if higher values and more red if lower negative nums

with balace_over_time:

    balance_df = df.resample(on="Transaktionsdatum", rule="M").agg({"Saldo": "last"})
    balance_df["Saldo"] = balance_df["Saldo"].apply(lambda row: float(row.replace(" ", "").replace(",", ".")))

    st.plotly_chart(utils.monthly_balance(df))

with detailed_month:

    df["month"] = df["Transaktionsdatum"].dt.strftime("%b-%Y")

    selected_month = st.selectbox(label="Select which month to analyze",
                                    options=df["month"].unique(), key="selected_month")

    st.plotly_chart(utils.horizontal_barplot(df, selected_month=selected_month))



st.subheader("Category Level")
st.markdown("The category level visualizes what the spending was on a more granular level.  \n"
            "The page consists of two sub-pages:  \n"
            "* **Categories over Time** - Lets you choose multiselect categories you want to analyze over time.  \n"
            "* **Details per Category** - Allows you to choose one category and analyze all the payments within it.")

categories_over_time, detailed_category = st.tabs(["Categories over Time", "Details per Category"])

with categories_over_time:
    selected_cats = st.multiselect(label="Select which categories you want to visualize",
                options=df["Kategori"].unique(), default=["Food", "Other"], key="selected_categories")
    
    st.plotly_chart(utils.line_plot(df, selected_cats))

with detailed_category:
    single_category = st.selectbox(label="Select category to analyze", 
                                options=df[df["Typ"] == "Kostnad"]["Kategori"].unique(), key="single_category")

    single_df = df[df["Kategori"] == single_category]

    st.write(single_df.groupby("Text").agg(Amount=("Belopp", "sum"), Occurance=("Text","count")).sort_values(by="Amount"))


