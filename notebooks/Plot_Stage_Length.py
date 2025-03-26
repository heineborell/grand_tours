# import pandas as pd
# import numpy as np
# import sqlite3
# #
# import matplotlib.pyplot as plt
# from matplotlib import style
# plt.style.use('bmh')

# def plot_from_sqlite(db_path,table_name):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT DISTINCT stage_num FROM {table_name}")
#     unique_stage_nums = [row[0] for row in cursor.fetchall()]
#     #
#     if table_name == "tdf_results":
#         tour_name = "tdf"
#     elif table_name == "giro_results":
#         tour_name = "giro"
#     elif table_name == "vuelta_results":
#         tour_name = "vuelta"
#     else:
#         raise ValueError("Invalid table name.")
#     #
#     for stage in unique_stage_nums:
#         cursor.execute(f"SELECT year, distance, ITT FROM {table_name} WHERE stage_num = ?", (stage,))
#         data = cursor.fetchall()
#         if not data:
#             continue
#         #
#         # sort the copied data by year to avoiod randomly connected lines
#         sorted_data = sorted(data, key=lambda x: x[0])  
#         tour_year, distance_km, time_trials = zip(*sorted_data)
#         #-----------------------------------#
#         fig, ax = plt.subplots(figsize=(12, 6))
#         stage_marker = "o"
#         ITT_stage_marker = "o"
#         #
#         ax.plot(tour_year, distance_km, label=f"Stage-{stage}", marker=stage_marker)
#         #
#         # mark points where ITT == 1 differently
#         for i in range(len(tour_year)):
#             if time_trials[i] == 1:
#                 plt.plot(tour_year[i], distance_km[i], marker=ITT_stage_marker, markerfacecolor='none', 
#                          markeredgecolor='red', markersize=10, linestyle='None')
#         # 
#         ax.set_xlabel("year")
#         ax.set_ylabel("distance (km)")
#         ax.legend()
#         ax.set_title(f"year vs. stage distance for {tour_name}")
#         fig.tight_layout()
#         plt.show()
#         plt.close(fig)
#         #-----------------------------------#
#     # Close connection
#     conn.close()
# ## 
# db_path = "data/grand_tours.db"
# table_name = "giro_results"
# plot_from_sqlite(db_path,table_name)



# '''
# Using pandas
# '''

# import pandas as pd
# import numpy as np
# import sqlite3
# #
# import matplotlib.pyplot as plt
# from matplotlib import style
# plt.style.use('bmh')
# #
# def plot_from_sqlite(db_path,table_name):
#     conn = sqlite3.connect(db_path)
#     query = f"SELECT year, distance, stage_num, ITT, winner_avg_speed  FROM {table_name}"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     #
#     if table_name == "tdf_results":
#         tour_name = "tdf"
#         xvalues = np.linspace(1910,2030,13, dtype=int)
#     elif table_name == "giro_results":
#         tour_name = "giro"
#         xvalues = np.linspace(1910,2030,13, dtype=int)
#     elif table_name == "vuelta_results":
#         tour_name = "vuelta"
#         xvalues = np.linspace(1930,2030,11, dtype=int)
#     else:
#         raise ValueError("Invalid table name.")
#     #
#     # Create a {tour:color} dictionary/map 
#     tour_colors = {"tdf":"yellow", "giro": "pink", "vuelta":"red"}
#     #
#     # Sort the data by year
#     df = df.sort_values(by=['year'])
#     #
#     # Get unique stage numbers
#     unique_stage_nums = df['stage_num'].unique()
#     #
#     for stage in unique_stage_nums:
#         df_subset = df[df['stage_num'] == stage]
#         #-----------------------------------#
#         fig, ax1 = plt.subplots(figsize=(12, 6)) 
#         # ax2 = ax1.twinx()  # Create a secondary y-axis
#         if not df_subset.empty:
#             ax1.plot(df_subset['year'], df_subset['distance'], color=tour_colors[tour_name], marker='o', ls='-', ms=6, mec='k', label=f"Stage-{stage}")
#             # mark points where ITT == 1 differently
#             highlighted = df_subset[df_subset['ITT'] == 1]
#             ax1.plot(highlighted['year'], highlighted['distance'], marker='o', mfc='none', mec='k', ms=10, ls='None')
#             #
#             # ax2.plot(df_subset['year'], df_subset['winner_avg_speed'], color=tour_colors[tour_name], marker='s', ls='None', ms=6, mec='b')
#         #
#         # Labels and legend
#         ax1.set_xlabel("year")
#         ax1.set_ylabel("distance (km)")
#         # ax2.set_ylabel("Winner average speed (km/h)")
#         ax1.set_title(f"stage distance and and winner average speed for {tour_name}")
#         plt.xticks(xvalues, [str(x) for x in xvalues], rotation=0) 
#         ax1.legend(loc='upper right')
#         fig.tight_layout()
#         plt.savefig("Plots/"+tour_name + "/Stage_" +str(stage) +"_length_by_year.png", bbox_inches='tight')
#         # plt.show()
#         # plt.close(fig)
#         #-----------------------------------#
# ## 
# db_path = "data/grand_tours.db"
# table_name = "vuelta_results"
# plot_from_sqlite(db_path,table_name)






# import pandas as pd
# import numpy as np
# import sqlite3
# #
# import matplotlib.pyplot as plt
# from matplotlib import style
# plt.style.use('bmh')
# import seaborn as sns
# sns.set_style("whitegrid")
# #
# def plot_year_vs_segment_distance(db_path,table_name):
#     #---------------#
#     # Dictionary of tour-specific attributes
#     tour_attributes = {
#         "tdf_results":{"name":"tdf", "color":"yellow", "xvalues": np.linspace(1910,2030,13,dtype=int)},
#         "giro_results":{"name":"giro", "color":"pink", "xvalues": np.linspace(1910,2030,13,dtype=int)},
#         "vuelta_results":{"name":"vuelta", "color":"red", "xvalues": np.linspace(1930,2030,11,dtype=int)}
#     }
#     # Validate table_name and get attributes
#     if table_name not in tour_attributes:
#         raise ValueError("Invalid table name.")
#     #
#     tour_name = tour_attributes[table_name]["name"]
#     plot_color = tour_attributes[table_name]["color"]
#     xvalues = tour_attributes[table_name]["xvalues"]
#     #---------------#
#     conn = sqlite3.connect(db_path)
#     query = f"SELECT year, distance, stage_num, ITT, winner_avg_speed  FROM {table_name}"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     #
#     # Sort the data by year
#     df = df.sort_values(by=['year'])
#     #
#     # Get unique stage numbers
#     unique_stage_nums = df['stage_num'].unique()
#     #
#     for stage in unique_stage_nums:
#         df_subset = df[df['stage_num'] == stage]
#         #-----------------------------------#
#         fig, ax1 = plt.subplots(figsize=(12, 6)) 
#         # ax2 = ax1.twinx() 
#         if not df_subset.empty:
#             ax1.plot(df_subset['year'], df_subset['distance'], color=plot_color, marker='o', ls='-', ms=6, mec='k', label=f"Stage-{stage}")
#             # mark points where ITT == 1 differently
#             highlighted = df_subset[df_subset['ITT'] == 1]
#             ax1.plot(highlighted['year'], highlighted['distance'], marker='o', mfc='none', mec='b', ms=12, ls='None')
#             #
#             # # Display winner_avg_speed as text annotations
#             # for i, txt in enumerate(df_subset['winner_avg_speed']):
#             #     ax1.annotate(f'{txt:.2f}', (df_subset['year'].iloc[i], df_subset['distance'].iloc[i]), 
#             #                  textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color='blue')
#             # ax2.plot(df_subset['year'], df_subset['winner_avg_speed'], color=plot_color, marker='s', ls='None', ms=6, mec='b')
#         #
#         ax1.set_xlabel("year")
#         ax1.set_ylabel("distance (km)")
#         # ax2.set_ylabel("Winner average speed (km/h)")
#         ax1.set_title(f"year vs. stage distance for {tour_name}")
#         plt.xticks(xvalues, [str(x) for x in xvalues], rotation=0) 
#         ax1.legend(loc='upper right')
#         fig.tight_layout()
#         plt.savefig("Plots/"+tour_name + "/Stage_" +str(stage) +"_length_by_year.png", bbox_inches='tight')
#         # plt.show()
#         plt.close()
#         #-----------------------------------#
# ## 
# db_path = "data/grand_tours.db"
# plot_year_vs_segment_distance(db_path, "tdf_results")
# plot_year_vs_segment_distance(db_path, "giro_results")
# plot_year_vs_segment_distance(db_path, "vuelta_results")












import pandas as pd
import numpy as np
import sqlite3
#
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')

## Function that contains dictionary of tour-specific attributes
def get_tour_attributes():
    return {
        "tdf_results": {"name": "tdf", "color": "yellow", "xvalues": np.linspace(1910, 2030, 13, dtype=int)},
        "giro_results": {"name": "giro", "color": "pink", "xvalues": np.linspace(1910, 2030, 13, dtype=int)},
        "vuelta_results": {"name": "vuelta", "color": "red", "xvalues": np.linspace(1930, 2030, 11, dtype=int)}
    }

## Function to plot the stage-distane and the average-winning-speed for a specific stage
def plot_year_vs_distance_and_speed(db_path,table_name):
    #---------------#
    tour_attributes = get_tour_attributes()
    # Validate table_name and get attributes
    if table_name not in tour_attributes:
        raise ValueError("Invalid table name.")
    tour_name = tour_attributes[table_name]["name"]
    plot_color = tour_attributes[table_name]["color"]
    xvalues = tour_attributes[table_name]["xvalues"]
    #---------------#
    # Compute midpoints between xvalues for dashed vertical lines
    x_midpoints = [(xvalues[i] + xvalues[i+1]) / 2 for i in range(len(xvalues) - 1)]
    #
    conn = sqlite3.connect(db_path)
    query = f"SELECT year, distance, stage_num, ITT, winner_avg_speed  FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    #
    # Sort the data by year
    df = df.sort_values(by=['year'])
    # Get unique stage numbers
    unique_stage_nums = df['stage_num'].unique()
    #
    for stage in unique_stage_nums:
        #-----------------------------------#
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
        df_subset = df[df['stage_num'] == stage]
        highlighted = df_subset[df_subset['ITT'] == 1]
        if not df_subset.empty:
            ## Plot year vs distance
            ax1.plot(df_subset['year'], df_subset['distance'], color=plot_color, marker='o', ls='-', ms=6, mec='k', label=f"Stage-{stage}")
            ax1.plot(highlighted['year'], highlighted['distance'], marker='o', mfc='none', mec='b', ms=10, ls='None', label="ITT")
            ax1.set_ylabel("distance (km)", color='k')
            ax1.set_title(f"Distance and winning average speed for Stage-" + str(stage) + " of " + f"{tour_name}")
            ax1.set_ylim(1, 600)  # Adjusted for log scale
            ax1.set_yscale("log") 
            ax1.yaxis.set_major_locator(FixedLocator([1, 10, 20, 50, 100, 200, 300, 400, 500, 600]))
            #
            ## Plot year vs winning-average-speed
            ax2.plot(df_subset['year'], df_subset['winner_avg_speed'], color=plot_color, marker='o', ls='-', ms=6, mec='k', label=f"Stage-{stage}")
            ax2.plot(highlighted['year'], highlighted['winner_avg_speed'], marker='o', mfc='none', mec='b', ms=10, ls='None', label="ITT")
            ax2.set_ylabel("Winner average speed (km/h)", color='k')
            ax2.set_xlabel("year")
            #
            # Compute and display average values
            avg_distance = df_subset['distance'].mean()
            avg_avg_speed = df_subset['winner_avg_speed'].mean()
            ax1.axhline(avg_distance, color='k', ls='dashed', lw=1, label=f'Avg Distance: {avg_distance:.2f}')
            ax2.axhline(avg_avg_speed,color='k', ls='dashed', lw=1, label=f'Avg of Speed Averages: {avg_avg_speed:.2f}')
            #
            plt.xticks(xvalues, [str(x) for x in xvalues], rotation=0) 
            for x in x_midpoints:
                ax1.axvline(x, linestyle='dashed', color='gray', alpha=0.5, lw=0.5)
                ax2.axvline(x, linestyle='dashed', color='gray', alpha=0.5, lw =0.5)
            ax1.legend(loc='best')
            ax2.legend(loc='best')
        #
        fig.tight_layout()
        plt.savefig("Plots/"+tour_name + "/by_stage/Stage_" +str(stage) +"_distance_and_speed.png", bbox_inches='tight')
        ## plt.show()
        plt.close()
        #-----------------------------------#
## 
db_path = "data/grand_tours.db"
plot_year_vs_distance_and_speed(db_path, "tdf_results")
plot_year_vs_distance_and_speed(db_path, "giro_results") 
plot_year_vs_distance_and_speed(db_path, "vuelta_results")




# import numpy as np

# x = np.linspace(1930,2030,11)
# print(x)