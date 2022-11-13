import streamlit as st
import utils
import database
import pandas as pd
import datetime as dt

#Setting the title for the page as well as the icon displayed in the browser tab
st.set_page_config(page_title="Expenditure Visualization", page_icon="📊")

#First section of the application
st.header("Expenditure Visualization")
st.markdown("Select a starting month to start the analysis from.")

#Checking the earliest and the latest date in the db in order to give the user a date range from the prompt
START_DATE = database.check_earliest_date()
END_DATE = database.check_latest_date()

#Divide the provided dates into monthly sections
datelist = pd.date_range(start=START_DATE, end=END_DATE, freq="M")

#User prompt regarding where to start the analysis from
starting_month = st.selectbox("Select month to start analyzing from", 
                            options=datelist.strftime("%b-%Y"), key="start_month",
                            index=len(datelist)-6)


#Pulls data from the database given the date input from the user
df = database.pull_data(dt.datetime.strptime(starting_month, "%b-%Y"))

#Second section regarding the overview level of the analysis
st.subheader("Overview Level")
st.markdown("The overview level will visualize what the spending were on an aggregate level, month-by-month.  \n"
            "The page consists of three sub-pages  \n"
            "* **Monthly Savings/Loss** - This shows the profit / loss made within each month.  \n"
            "* **Total Balance over Time** - This shows the total savings over time in the given deposit account.  \n"
            "* **Detailed Month View** - This allows you to choose a month and get a detailed view of the spending.")

#Diving the overview level into 3 tabs
monthly_result, balace_over_time, detailed_month = st.tabs(["Monthly Savings/Loss", "Total Balance over Time", "Detailed Month View"])

#Plots the profit/loss per month
with monthly_result:
    st.plotly_chart(utils.bar_plot(df))

#Plots the ending balance per month
with balace_over_time:
    st.plotly_chart(utils.monthly_balance(df))

#Allows the user to select a specific month to analyze the cost per category for the given month.
with detailed_month:

    df["month"] = df["Transaktionsdatum"].dt.strftime("%b-%Y")

    selected_month = st.selectbox(label="Select which month to analyze",
                                    options=df["month"].unique(), key="selected_month")

    st.plotly_chart(utils.horizontal_barplot(df, selected_month=selected_month))


#Third section regarding the category level
st.subheader("Category Level")
st.markdown("The category level visualizes what the spending was on a more granular level.  \n"
            "The page consists of two sub-pages:  \n"
            "* **Categories over Time** - Lets you choose multiselect categories you want to analyze over time.  \n"
            "* **Details per Category** - Allows you to choose one category and analyze all the payments within it.")

#Diving the Category level into 2 tabs.
categories_over_time, detailed_category = st.tabs(["Categories over Time", "Details per Category"])

#Allows the user to multi-select categories to show costs over time.
with categories_over_time:
    selected_cats = st.multiselect(label="Select which categories you want to visualize",
                options=df[df["Typ"] == "Kostnad"]["Kategori"].unique(), default=["Food", "Other"], key="selected_categories")
    
    st.plotly_chart(utils.line_plot(df, selected_cats))

#Allows the user to get detailed transaction information for all transactions within a specified category.
with detailed_category:
    single_category = st.selectbox(label="Select category to analyze", 
                                options=df[df["Typ"] == "Kostnad"]["Kategori"].unique(), key="single_category")

    single_df = df[df["Kategori"] == single_category]

    st.write(single_df.groupby("Text").agg(Amount=("Belopp", "sum"), Occurance=("Text","count")).sort_values(by="Amount"))


