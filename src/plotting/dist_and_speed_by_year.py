# src/plotting/dist_and_sped_by_year.py
from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3
#
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')

## Function that contains dictionary of tour-specific attributes
def get_tour_color_attributes():
    return {
        "tdf_results": {"name": "tdf", "color": "yellow"},
        "giro_results": {"name": "giro", "color": "pink"},
        "vuelta_results": {"name": "vuelta", "color": "red"}
    }

def get_max_stage_from_year_pd(db_path, table_name, year_num):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f""" SELECT stage_num FROM {table_name} WHERE year = ?"""
    cursor.execute(query, (year_num,))
    results = cursor.fetchall()
    conn.commit()
    conn.close()

    if not results:
        print("Empty df")
        return None
    # Extract values and find the largest one
    Stage_values = [row[0] for row in results]
    print("Max found", max(Stage_values))
    return max(Stage_values)

def get_max_stage_from_year_pd(conn, table_name, year_num):
    cursor = conn.cursor()
    query = f""" SELECT stage_num FROM {table_name} WHERE year = ?"""
    cursor.execute(query, (year_num,))
    results = cursor.fetchall()
    if not results:
        return None
    # Extract values and find the largest one
    Stage_values = [row[0] for row in results]
    return max(Stage_values)

# ## Function to get the maximum stage number for a given tour
# def get_max_stage_from_year(db_path, table_name, year_val):
#     conn = sqlite3.connect(db_path)
#     query = f"SELECT year, stage_num FROM {table_name} WHERE year = ? "
#     df = pd.read_sql_query(query, conn, params=(year_val,))
#     conn.close()
    
#     df.head(5)
#     if df.empty:
#         print("empty dataframe")
#         return None
    
#     max_stage = df['stage_num'].max()
#     return max_stage if pd.notna(max_stage) else None


## Function to plot the stage-distane and the average-winning-speed for a specific year
def plot_stage_vs_distance_and_speed(db_path,table_name):
    #---------------#
    tour_attributes = get_tour_color_attributes()
    # Validate table_name and get attributes
    if table_name not in tour_attributes:
        raise ValueError("Invalid table name.")
    tour_name = tour_attributes[table_name]["name"]
    plot_color = tour_attributes[table_name]["color"]
    #---------------#
    conn = sqlite3.connect(db_path)
    query = f"SELECT year, distance, stage_num, ITT, winner_avg_speed  FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    #
    # Sort the data by stage number
    df = df.sort_values(by=['stage_num'])
    # Get year values
    unique_year = df['year'].unique()
    #
    for year_val in unique_year:
        #-----------------------------------#
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
        df_subset = df[df['year'] == year_val]
        highlighted = df_subset[df_subset['ITT'] == 1]
        if not df_subset.empty:
            ## Plot stage_num vs distance
            ax1.plot(df_subset['stage_num'], df_subset['distance'], color=plot_color, marker='o', ls='-', ms=6, mec='k', label=f"Year-{year_val}")
            ax1.plot(highlighted['stage_num'], highlighted['distance'], marker='o', mfc='none', mec='b', ms=10, ls='None', label="ITT")
            ax1.set_ylabel("distance (km)", color='k')
            ax1.set_title(f"Distance and winning average speed for Stage-" + str(year_val) + " of " + f"{tour_name}")
            # ax1.set_ylim(1, 600)  # Adjusted for log scale
            # ax1.set_yscale("log") 
            # ax1.yaxis.set_major_locator(FixedLocator([1, 10, 20, 50, 100, 200, 300, 400, 500, 600]))
            #
            ## Plot stage_num vs winning-average-speed
            ax2.plot(df_subset['stage_num'], df_subset['winner_avg_speed'], color=plot_color, marker='o', ls='-', ms=6, mec='k', label=f"Year-{year_val}")
            ax2.plot(highlighted['stage_num'], highlighted['winner_avg_speed'], marker='o', mfc='none', mec='b', ms=10, ls='None', label="ITT")
            ax2.set_ylabel("Winner average speed (km/h)", color='k')
            ax2.set_xlabel("Stage")
            #
            unique_Stage_nums = sorted(df_subset['stage_num'].dropna().astype(int).unique())
            plt.xticks(unique_Stage_nums, [str(x) for x in unique_Stage_nums], rotation=0)
            
            # # Compute and display average values
            # avg_distance = df_subset['distance'].mean()
            # avg_avg_speed = df_subset['winner_avg_speed'].mean()
            # ax1.axhline(avg_distance, color='k', ls='dashed', lw=1, label=f'Avg Distance: {avg_distance:.2f}')
            # ax2.axhline(avg_avg_speed,color='k', ls='dashed', lw=1, label=f'Avg of Speed Averages: {avg_avg_speed:.2f}')
            # #
            # max_stage = get_max_stage_from_year_pd(db_path, table_name, year_val)  
            # print("Year = ", year_val, " max stage = ", max_stage, "\n")
            # x_Stage_vals = np.linspace(1,max_stage_num, dtype=int)
            # plt.xticks(x_Stage_vals, [str(x) for x in x_Stage_vals]) 
            #
            ax1.legend(loc='best')
            ax2.legend(loc='best')
        #
        fig.tight_layout()
        plt.savefig("Plots/"+tour_name + "/by_year/Year_" +str(year_val) +"_distance_and_speed.png", bbox_inches='tight')
        ## plt.show()
        plt.close()
        #-----------------------------------#
## 
db_path = "data/grand_tours.db"
plot_stage_vs_distance_and_speed(db_path, "tdf_results")
plot_stage_vs_distance_and_speed(db_path, "giro_results") 
plot_stage_vs_distance_and_speed(db_path, "vuelta_results")