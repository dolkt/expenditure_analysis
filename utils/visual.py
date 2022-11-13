"""Module containing the visualization tools used on the provided DataFrame"""
import plotly.express as px
import numpy as np


def line_plot(df, selected_categories):
    """
    Masks the provided pandas.DataFrame given the provided categories.
    Plots the costs of the selected categories over time
    
    --------
    Parameters
    df - pandas.DataFrame of transaction data
    selected_categories - list of str containing the user provided categories
    
    ---------
    Returns
    plotly.express.line figure
    """

    #Groups per category and performs monthly-resample on the data
    df = df.groupby("Kategori").resample(on="Transaktionsdatum", rule="M").sum().reset_index()

    #Masks the data based on the categories and where belopp is less than 0 (it's costs only)
    df = df[(df["Kategori"].isin(selected_categories)) & (df["Belopp"] < 0)]
    
    #For prettifying the line plot all the costs are converted into a positive float.
    df["Belopp"] = df["Belopp"] * -1

    #Dates on x-axis and costs on y-axis
    px_line = px.line(data_frame=df, x="Transaktionsdatum", y="Belopp", 
                        color="Kategori", markers=True)

    #Updates the layout of the plot.
    px_line.update_layout(xaxis={"title_text": None, "tickvals": df["Transaktionsdatum"], "ticktext": df["Transaktionsdatum"].dt.strftime("%b-%Y")},
                            yaxis={"title_text": "Amount (kr)"},
                            title={"text": "Spending per Category over Time", "font_size": 15.5})

    return px_line


def monthly_balance(df):
    """
    Line plot on the monthly-resample of the provided pandas.DataFrame and takes the latest record of user's balance for each month
    
    --------
    Parameters
    df - pandas.DataFrame of transaction data
    
    --------
    Returns
    plotly-express.line figure
    """
    
    #Monthly-resample of the data and takes the latest entry of balance (saldo)
    df = df.resample(on="Transaktionsdatum", rule="M").agg({"Saldo": "last"}).reset_index()

    #Data cleaning of the Saldo values.
    df["Saldo"] = df["Saldo"].apply(lambda row: float(row.replace(" ", "").replace(",", ".")))

    #Date on x-axis and balance on y-axis.
    px_line = px.line(data_frame=df, x="Transaktionsdatum", y="Saldo", markers=True)

    #Updates the layout of the plot
    px_line.update_layout(xaxis={"title_text": None, "tickvals": df["Transaktionsdatum"], "ticktext": df["Transaktionsdatum"].dt.strftime("%b-%Y")},
                        yaxis={"title_text": "Savings (kr)"},
                        title={"text": "Total Deposit Savings (kr)","font_size": 15.5},
                        showlegend=False)

    return px_line

def bar_plot(df):
    """
    Monthly resamples the data and provides a bar plot of the profit/loss per month
    
    --------
    Parameters
    df - pandas.DataFrame of transaction data
    
    --------
    Returns
    plotly.express.bar figure
    """

    #Monthly-resample of the data
    df = df.resample(rule="M", on="Transaktionsdatum").sum().reset_index()

    #Sets a color indicator column for the bar plot
    df["color"] = np.where(df["Belopp"] > 0, "green", "red")
    
    #Provides a bar plot of the profit/loss, where profit is green and loss is red.
    px_bar = px.bar(data_frame=df, x="Transaktionsdatum", y="Belopp",
                        text_auto=".1f",
                        color="color",
                        color_discrete_map={"green":"lawngreen", "red":"red"},
                        title="Savings / Loss per Month (kr)")

    #Updates the traces (the bar text) of the plot
    px_bar.update_traces(textposition="outside")

    #Updates the layout of the plot
    px_bar.update_layout(title={"font_size":15.5},
                        xaxis={"title_text": None, "tickvals": df["Transaktionsdatum"], "ticktext": df["Transaktionsdatum"].dt.strftime("%b-%Y")},
                        yaxis={"title_text": "Amount (kr)"},
                        showlegend=False)


    return px_bar


def horizontal_barplot(df, selected_month):
    """
    Masks the data on a specific month and provides an horizontal bar plot of the costs
    
    
    --------
    Parameters
    df - pandas.DataFrame of transaction data
    selected_month - str containing the month name
    
    --------
    Returns
    plotly.express.bar figure"""

    #Masks the df based on the provided month and only including costs.
    df = df[(df["month"] == selected_month) & (df["Typ"] == "Kostnad")]

    #Groups the df based on category and sums the values and sorts them.
    df = df.groupby("Kategori").sum().sort_values(by="Belopp", ascending=False)

    #For prettifying the plot it puts the costs as positives instead
    df["Belopp"] = df["Belopp"] * -1

    #Horizontal bar chart of the data.
    px_hbar = px.bar(data_frame=df, orientation="h", text_auto=".2s", title="Spending per Category (kr)")

    #Updates the layout of the plot
    px_hbar.update_layout(yaxis={"title_text": None},
                        xaxis={"title_text":"Spending (kr)"},
                         showlegend=False,
                         title={"font_size": 15.5, "x":0.5, "y":0.85, "xanchor":"center", "yanchor":"top"})

    return px_hbar
