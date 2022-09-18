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

START_DATE = dt.datetime(year=2018, month=1, day=1)
END_DATE = dt.datetime.today()

datelist = pd.date_range(start=START_DATE, end=END_DATE, freq="M")

starting_month = st.selectbox("Select month to start analyzing from", 
                            options=datelist.strftime("%b-%Y"), key="start_month")


monthly_result, balace_over_time, detailed_month = st.tabs(["Monthly Savings/Loss", "Total Balance over Time", "Detailed Month View"])
with monthly_result:
    #Starting month is temp until SQL-selection is done.
    st.plotly_chart(utils.bar_plot(df, starting_month))
    #Find a way to make negative values red and positive green.
    #Bonus if greener if higher values and more red if lower negative nums

with balace_over_time:

    balance_df = df.resample(on="Transaktionsdatum", rule="M").agg({"Saldo": "last"})
    balance_df["Saldo"] = balance_df["Saldo"].apply(lambda row: float(row.replace(" ", "").replace(",", ".")))

    st.plotly_chart(px.line(balance_df, markers=True))

with detailed_month:

    df["month"] = df["Transaktionsdatum"].dt.strftime("%b-%Y")

    selected_month = st.selectbox(label="Select which month to analyze",
                                    options=df["month"].unique(), key="selected_month")

    st.plotly_chart(utils.horizontal_barplot(df, selected_month=selected_month))


selected_cats = st.multiselect(label="Select which categories you want to visualize",
                options=df["Kategori"].unique(), key="selected_categories")



st.plotly_chart(utils.line_plot(df, selected_cats))


#Show occurance per category

single_category = st.selectbox(label="Select category to analyze", 
                                options=df["Kategori"].unique(), key="single_category")

single_df = df[df["Kategori"] == single_category]

st.write(single_df.groupby("Text").agg({"Belopp":"sum", "Text":"count"}).sort_values(by="Belopp"))


