"""Module containing the visualization tools used on the provided DataFrame"""
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import dates as mpl_dates
import pandas as pd
import numpy as np
import os
import sys




def line_plot(frame):
    """Wrangles the data from the provided DataFrame. 
    Summarizes income and cost on a monthly level.
    Then performs a line plot to show progression of income/costs.
    
    Keyword arguments:
    frame -- The provded DataFrame to wrangle and plot
    
    Returns Figure Object"""

    #Groups and summarizes the amount for each category.
    frame = frame.groupby("Typ").resample("M", on="Transaktionsdatum").sum()

    #Adjust the transactions to be positive for the line plot
    frame.loc["Kostnad"]["Belopp"] = frame.loc["Kostnad"]["Belopp"] * -1

    #Unstacks the GroupBy DataFrame.
    frame = frame.unstack(level=0)

    #Splits the DataFrame on Income and Cost.
    cost = frame["Belopp"]["Kostnad"]
    income = frame["Belopp"]["Inkomst"]

    #Initiates the figure and the axes object.
    line_fig, ax = plt.subplots(figsize=(10,10))

    #Creates a line plot for Income and Cost.
    ax.plot(frame.index, cost, label="Cost", marker="o", color="r", ms=4)
    ax.plot(frame.index, income, label="Income", marker="o", color="g", ms=4)
    
    #Initates a legend and sets coloring for the labels.
    ax.legend(labelcolor=["r", "g"])

    #Formats the y-axis to show as <amount> kr.
    ax.yaxis.set_major_formatter("{x:.0f}kr")

    #Uses dateformatting on the x-axis.
    format_dates = mpl_dates.DateFormatter("%Y-%b")
    ax.xaxis.set_major_formatter(format_dates)

    #Sets the ticks on x-axis to only show the values from the DataFrame.
    ax.xaxis.set_ticks(frame.index)
    
    #Sets grid from the y-axis for readability of the plot.
    ax.yaxis.grid(True, alpha=0.4)
    
    #Figure cleaning. Removing bar junk
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(left=False)

    #Last fixes of the figure to make it more readable.
    line_fig.autofmt_xdate()
    line_fig.tight_layout()

    return line_fig

def bar_plot(frame):
    """Takes data from DataFrame and wrangles the data into three quartiles.
    The wrangled data will be used in the sub-function for conducting a grouped bar plot
    
    Keyword arguments:
    frame -- The provided DataFrame to clean and perform categorization on
    
    Returns Figure Object for each quartile
    """
    
    #Initializing the quartile names
    cost_labels = ["High", "Medium", "Low"]
    
    #Divides the cost categories into three quartiles.
    quartiles = pd.qcut(frame[frame["Typ"] == "Kostnad"].groupby("Kategori")["Belopp"].sum(),
                        q=3, labels=cost_labels)

    #Inserts the quartile as a new column in the DataFrame
    frame["cost_class"] = ""
    for cat, value in zip(quartiles.index, quartiles):
        frame["cost_class"] = np.where(frame["Kategori"] == cat, value, frame["cost_class"])

    #Resamples the data into quarterly for each category.
    frame = frame[frame["Typ"] == "Kostnad"].groupby(["Kategori", "cost_class"]).resample("Q", on="Transaktionsdatum").sum()

    #Prepares the data for visualization
    frame["Belopp"] = frame["Belopp"] * -1
    frame = frame.unstack(level=0)

    #Drops columns containing all NaN values. Replacing potential 0 values for each quartile with 0.
    high_cost = frame.loc["High"].dropna(how="all", axis=1).fillna(0)
    medium_cost = frame.loc["Medium"].dropna(how="all", axis=1).fillna(0)
    low_cost = frame.loc["Low"].dropna(how="all", axis=1).fillna(0)


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


def month_hbarplot(frame):
    """Wrangles the data from the provided DataFrame.
    Summarizes the cost per category on a monthly level.
    Then performs a h-bar plot on the categories.
    
    Keyword arguments:
    frame -- The provded DataFrame to wrangle and plot

    Returns Figure Object"""

    #Groups per category and inverts it to a positive float.
    frame = frame[frame["Typ"] == "Kostnad"].groupby("Kategori")["Belopp"].sum() * - 1

    #Sorting the values in order to make the bar plot prettier.
    frame = frame.sort_values(ascending=False)
    
    #Initiates the figure.
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(frame.index, frame)

    #Uses the Set2 colormap and plots each bar as a different color.
    color_map = cm.Set2(np.linspace(0, 1, len(frame.index)))
    for color, bar in zip(color_map, ax.patches):
        bar.set_color(color)

    #Removing bar junk.
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_visible(False)

    #Annotates the amount of each bar.
    for bar in ax.patches:
        ax.annotate(format(bar.get_width(), ".0f")+" kr", 
        (bar.get_width(), bar.get_y() + bar.get_height() / 2.25),
        xytext = (5, 0),
        textcoords = "offset points"
        )

    return fig
