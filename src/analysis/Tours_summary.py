import pandas as pd
import numpy as np
import sqlite3
import seaborn as sns
import re
# For plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import style
plt.style.use('ggplot')

##
#import os
import pathlib
file = pathlib.Path(__file__).parent.resolve()
#
def basic_database_summary(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #
    newline_indent = '\n   '
    conn.text_factory = str
    #
    result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = sorted(list(zip(*result))[0])
    print ("\ntables are:"+newline_indent+newline_indent.join(table_names))
    #
    for table_name in table_names:
        result = cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        #print (("\ncolumn names for %s:" % table_name) +newline_indent +(newline_indent.join(column_names)))
        #
        print (("\n\nColumn schema for table %s:" % table_name))
        for row in cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall():
            print(row)
    #
    cursor.close()
    conn.close()

def get_max_stage_from_year(db_path, table_name, year_num):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #
    cursor.execute(f"""SELECT stage FROM "{table_name}" WHERE year = "{year_num}" """)
    rows = cursor.fetchall()
    # Extract stage numbers and count frequencies
    stage_counts = {}
    for row in rows:
        stage_text = row[0]
        match = re.search(r'\d+', stage_text)
        if match:
            stage_number = int(match.group()) if match else None
            stage_counts[stage_number] = stage_counts.get(stage_number, 0) + 1
    #
    conn.close()
    return max(stage_counts) 

def get_yearly_summary(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #
    if table_name == "tdf_results":
        tour_name = "TDF"
    elif table_name == "giro_results":
        tour_name = "GRO"
    elif table_name == "vuelta_results":
        tour_name = "LAV"
    elif table_name == "segments_data":
        tour_name = "SEG"
    elif table_name == "strava_table":
        tour_name = "STRV"
    else:
        raise ValueError("Invalid table name.")
    #
    # Retrieve unique years and their counts
    cursor.execute(f"""SELECT year, COUNT(*) FROM "{table_name}" GROUP BY year""")
    rows = cursor.fetchall()
    #
    # Print the result to console
    print("Year,Frequency,Stages")
    years = []
    freqs = []
    max_stages =[]
    for year, freq in rows:
        max_stage = get_max_stage_from_year(db_path, table_name, year)  
        print(f"{year},{freq},{max_stage}")
        #
        if max_stage is not None:
            years.append(year)
            freqs.append(freq)
            max_stages.append(max_stage)
    #
    #-----------------------------------#
    # Create histogram
    fig, ax1 = plt.subplots(figsize=(7.5,2.5), dpi=200)
    #
    ax1.bar(years, freqs, color='b', alpha=0.6, label='Frequency')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Frequency (no. of rows)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    xvalues = np.linspace(1900,2020,13, dtype=int)
    plt.xticks(xvalues, [str(x) for x in xvalues], rotation=45) 
    #
    # Create secondary y-axis
    ax2 = ax1.twinx()
    ax2.plot(years,max_stages, color='r', marker='.', linestyle='-', label='Max Stage')
    ax2.set_ylabel('Number of Stages', color='r', fontsize=10)
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    #
    # Show the plot
    plt.title( tour_name + " data summary", fontsize=10)
    plt.savefig("Plots/"+ tour_name + "/" + tour_name + "_"+ "yearly_summary.png", bbox_inches='tight')
    fig.tight_layout()
    plt.show()
    #-----------------------------------#
    #
    cursor.close()
    conn.close()
    return years,freqs,max_stages


def get_summary_of_a_year(db_path, table_name, year_num):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #
    if table_name == "tdf_results":
        tour_name = "TDF"
    elif table_name == "giro_results":
        tour_name = "GRO"
    elif table_name == "vuelta_results":
        tour_name = "LAV"
    elif table_name == "segments_data":
        tour_name = "SEG"
    elif table_name == "strava_table":
        tour_name = "STRV"
    else:
        raise ValueError("Invalid table name.")
    #
    cursor.execute(f"""SELECT stage FROM "{table_name}" WHERE year = "{year_num}" """)
    rows = cursor.fetchall()
    # get stage numbers and their frequencies
    stage_counts = {}
    for row in rows:
        stage_text = row[0]
        match = re.search(r'\d+', stage_text)
        if match:
            stage_number = int(match.group())
            stage_counts[stage_number] = stage_counts.get(stage_number, 0) + 1

    # Print the results to console and create arrays for plot
    print(tour_name + " Year:",year_num)
    print("Stage,Riders")
    stages = []
    rider_freqs = []
    for stage, freq in sorted(stage_counts.items()):
        print(f"{stage}   {freq}")
        #
        if rider_freqs is not None:
            stages.append(stage)
            rider_freqs.append(freq)
    #
    #-----------------------------------#
    # Create histogram
    fig, ax1 = plt.subplots(figsize=(4.25,2.5), dpi=100)
    #
    ax1.bar(stages, rider_freqs, color='b', alpha=0.6, label="GRO-"+ str(year_num))
    ax1.set_xlabel('Stage')
    ax1.set_ylabel('No. of riders', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    xvalues = np.linspace(1,max(stage_counts), dtype=int)
    plt.xticks(xvalues, [str(x) for x in xvalues]) 
    #
    # Show the plot
    plt.title(tour_name + "-"+ str(year_num),fontsize=12)
    plt.savefig("Plots/"+ tour_name + "/" + tour_name + "_"+ str(year_num) + "_summary.png", bbox_inches='tight')
    fig.tight_layout()
    plt.show()
    #-----------------------------------#
    # 
    cursor.close()
    conn.close()
#
'''
Tables in grand_tours.db
#     tdf_results
#     giro_results
#     vuelta_results
#     strava_names
#     segments_data
#     stats_data
#     strava_table
'''
## choose database and table 
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#db_path = os.path.join(BASE_DIR, "grand_tours.db")
db_path = "grand_tours.db"
table_name = "giro_results"
#
#
## Basic summary of entire data base
# basic_database_summary(db_path)
#
#
## yearly summary of one of the three tours
# get_yearly_summary(db_path, table_name)
#
#
## Specific year summary of one of the three tours
# get_summary_of_a_year(db_path, table_name,2001)
#
#
## Read sqlite query results into a pandas DataFrame
conn = sqlite3.connect(db_path)
df = pd.read_sql_query(f"""SELECT * from "{table_name}" """, conn)

# Verify that result of SQL query is stored in the dataframe
print(df.head())