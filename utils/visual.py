"""Module containing the visualization tools used on the provided DataFrame"""
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import dates as mpl_dates
import plotly.express as px
import pandas as pd
import numpy as np
import os
import sys




def line_plot(df, selected_categories):

    df = df.groupby("Kategori").resample(on="Transaktionsdatum", rule="M").sum().reset_index()

    df = df[(df["Kategori"].isin(selected_categories)) & (df["Belopp"] < 0)]
    
    df["Belopp"] = df["Belopp"] * -1

    px_line = px.line(data_frame=df, x="Transaktionsdatum", y="Belopp", 
                        color="Kategori", markers=True)

    px_line.update_layout(xaxis={"title_text": None},
                            yaxis={"title_text": "Amount (kr)"},
                            title={"text": "Spending per Category over Time", "font_size": 15.5})

    return px_line


def monthly_balance(df):

    df = df.resample(on="Transaktionsdatum", rule="M").agg({"Saldo": "last"})

    df["Saldo"] = df["Saldo"].apply(lambda row: float(row.replace(" ", "").replace(",", ".")))

    px_line = px.line(data_frame=df, markers=True)

    px_line.update_layout(xaxis={"title_text": None},
                        yaxis={"title_text": "Savings (kr)"},
                        title={"text": "Total Deposit Savings (kr)","font_size": 15.5},
                        showlegend=False)

    return px_line

def bar_plot(df):
    

    df = df.resample(rule="M", on="Transaktionsdatum").sum().reset_index()

    #To do make it masked by from date!
    
    px_bar = px.bar(data_frame=df.iloc[-12:], x="Transaktionsdatum", y="Belopp",
                        text_auto=".1f",
                        title="Savings / Loss per Month (kr)")

    px_bar.update_traces(textposition="outside")

    px_bar.update_layout(title={"font_size":15.5},
                        xaxis={"title_text": None},
                        yaxis={"title_text": "Amount (kr)"})


    return px_bar

    def group_barplot(frame):
        """Takes a DataFrame and conducts a grouped bar plot.
        
        Keyword arguments:
        frame -- The provided DataFrame to clean and perform categorization on
        
        Returns Figure Object
        """
        
        #Initializes the Figure and Axis Objects.
        fig, ax = plt.subplots(figsize=(15,10))

        #Sets a variable for the bar width of each grouped bar plot.
        bar_width = 8

        #Performs a bar plot for each column in the DataFrame.
        #Timedelta is used to be able to plot the bars next to each other.
        for num, col in enumerate(frame["Belopp"].columns):
            if num == 0:
                ax.bar(frame.index, frame["Belopp"][col], width=bar_width, label=col)
                fig.suptitle("Cost by Category in Class: "+ (quartiles.loc[col])) #Sets the title according to which quartile it belongs.
            elif num == 1:
                ax.bar(frame.index + pd.to_timedelta(str(bar_width)+"D"), frame["Belopp"][col], width=bar_width, label=col)
            elif num == 2:
                ax.bar(frame.index - pd.to_timedelta(str(bar_width)+"D"), frame["Belopp"][col], width=bar_width, label=col)
            else:
                ax.bar(frame.index + pd.to_timedelta(str(bar_width + num)+"D"), frame["Belopp"][col], width=bar_width, label=col)

        #Sets the legend for the bar plot
        ax.legend(title="Categories")

        #Removing bar junk and adjusting the layout.
        ax.set_xticks(frame.index)
        ax.yaxis.set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        
        #Annotates the amount of each bar, rounded and formated.
        for p in ax.patches:
            ax.annotate(format(round(p.get_height()/1000), ".0f")+"K",
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha = "center", va = "center",
            size=10,
            xytext = (0, -12),
            textcoords = "offset points"
            )

        return fig


    #Applies the sub-function grouped barplot on each quartile to get the data visualization.
    high_fig = group_barplot(high_cost)
    medium_fig = group_barplot(medium_cost)
    low_fig = group_barplot(low_cost)

    return high_fig, medium_fig, low_fig


def horizontal_barplot(df, selected_month):

    df = df[(df["month"] == selected_month) & (df["Typ"] == "Kostnad")]

    df = df.groupby("Kategori").sum().sort_values(by="Belopp", ascending=False)

    df["Belopp"] = df["Belopp"] * -1

    px_hbar = px.bar(data_frame=df, orientation="h", text_auto=".2s", title="Spending per Category (kr)")

    px_hbar.update_layout(yaxis={"title_text": None},
                        xaxis={"title_text":"Spending (kr)"},
                         showlegend=False,
                         title={"font_size": 15.5, "x":0.5, "y":0.85, "xanchor":"center", "yanchor":"top"})

    return px_hbar
