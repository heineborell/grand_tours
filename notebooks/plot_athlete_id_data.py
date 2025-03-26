# import sqlite3
# import matplotlib.pyplot as plt
# import numpy as np

# # Database details
# db_path = 'data/strava_segments.db'
# table_name = 'segment_activity'
# # athlete_id = 1821678
# athlete_id = 3905720

# # Connect to the SQLite database
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# # Query to retrieve data for the given athlete_id
# query = f"""
#     SELECT segment_distance_km, segment_time_seconds, segment_speed_kph, power_watt,
#            heart_rate_bpm, vertical_ascent_m, activity_id
#     FROM {table_name}
#     WHERE athlete_id = ?
# """
# cursor.execute(query, (athlete_id,))
# data = cursor.fetchall()
# conn.close()

# if not data:
#     print(f"No data found for athlete_id {athlete_id}")
# else:
#     # Convert data to a structured format
#     segment_distance_km, segment_time_seconds, segment_speed_kph, power_watt, \
#     heart_rate_bpm, vertical_ascent_m, activity_ids = zip(*data)

#     # Find unique activity_ids
#     unique_activity_ids = list(set(activity_ids))

#     # Define a color and marker for each activity_id
#     colors = plt.cm.get_cmap("tab10", len(unique_activity_ids)).colors  # Use a colormap for distinct colors
#     markers = ['o', 's', 'D', '^', 'v', 'P', '*', 'x', '+', 'h']  # Marker styles

#     activity_color_map = {activity: colors[i % len(colors)] for i, activity in enumerate(unique_activity_ids)}
#     activity_marker_map = {activity: markers[i % len(markers)] for i, activity in enumerate(unique_activity_ids)}

#     # Create a 2-row, 3-column figure
#     fig, axs = plt.subplots(2, 3, figsize=(14, 8))

#     # Define the plots
#     plot_configs = [
#         (axs[0, 0], segment_distance_km, segment_time_seconds, "Segment Distance (km)", "Segment Time (sec)", "Distance vs Time"),
#         (axs[0, 1], segment_distance_km, segment_speed_kph, "Segment Distance (km)", "Speed (kph)", "Distance vs Speed"),
#         (axs[0, 2], segment_distance_km, power_watt, "Segment Distance (km)", "Power (W)", "Distance vs Power"),
#         (axs[1, 0], segment_distance_km, heart_rate_bpm, "Segment Distance (km)", "Heart Rate (bpm)", "Distance vs HR"),
#         (axs[1, 1], vertical_ascent_m, segment_time_seconds, "Vertical Ascent (m)", "Segment Time (sec)", "Ascent vs Time"),
#         (axs[1, 2], vertical_ascent_m, segment_speed_kph, "Vertical Ascent (m)", "Speed (kph)", "Ascent vs Speed"),
#     ]

#     # Plot data, grouping by activity_id
#     for ax, x_data, y_data, x_label, y_label, title in plot_configs:
#         for activity in unique_activity_ids:
#             indices = [i for i, act in enumerate(activity_ids) if act == activity]
#             ax.scatter(
#                 [x_data[i] for i in indices],
#                 [y_data[i] for i in indices],
#                 color=activity_color_map[activity],
#                 marker=activity_marker_map[activity], s=3,
#                 label=f"Activity {activity}",
#                 alpha=0.7
#             )
#         ax.set_xlabel(x_label)
#         ax.set_ylabel(y_label)
#         ax.set_title(title)
#         ax.grid(True)

#     # Add a single legend outside the plots
#     handles = [plt.Line2D([0], [0], marker=activity_marker_map[act], color='w',
#                           markerfacecolor=activity_color_map[act], markersize=8, label=f"Activity {act}")
#                for act in unique_activity_ids]

#     fig.legend(handles=handles, loc='right', bbox_to_anchor=(0.5, 1.02), ncol=len(unique_activity_ids)//2+1)
#     plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Leave space for legend and title
#     plt.show()





import sqlite3
import pandas as pd
import numpy as np
import os
#
import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('bmh')

# Database details
db_path = 'data/strava_segments.db'
table_name = 'segment_activity'
athlete_id = 1821678
# athlete_id = 3905720  
conn = sqlite3.connect(db_path)
query = f"""
    SELECT activity_id, segment_distance_km, segment_time_seconds, segment_speed_kph, 
           power_watt, heart_rate_bpm, vertical_ascent_m
    FROM {table_name}
    WHERE athlete_id = ?
"""
df = pd.read_sql_query(query, conn, params=(athlete_id,))
conn.close()

# Check if data exists
if df.empty:
    print(f"No data found for athlete_id {athlete_id}")
    exit()

# Create figure with 2 rows and 3 columns
fig, axs = plt.subplots(2, 3, figsize=(14, 6))

# Define unique markers and colors for different activities
markers = ['o', 's', 'D', '^', 'v', 'p', 'X', '*', '<', '>']
colors = plt.cm.tab10.colors  # 10 distinct colors

# Create a legend handle for each activity_id
legend_handles = []

# Manually set axis limits (Modify these as needed)
axis_limits = {
    (0, 0): {'xlim': (0, 30), 'ylim': (0, 5000)},  # segment_distance_km vs segment_time_seconds
    (0, 1): {'xlim': (0, 30), 'ylim': (0, 80)},    # segment_distance_km vs segment_speed_kph
    (0, 2): {'xlim': (0, 30), 'ylim': (0, 800)},   # segment_distance_km vs power_watt
    (1, 0): {'xlim': (0, 30), 'ylim': (0, 300)},   # segment_distance_km vs heart_rate_bpm
    (1, 1): {'xlim': (0, 3000), 'ylim': (0, 5000)},# vertical_ascent_m vs segment_time_seconds
    (1, 2): {'xlim': (0, 3000), 'ylim': (0, 60)}   # vertical_ascent_m vs segment_speed_kph
}

# Group data by activity_id and plot
for i, (activity_id, group) in enumerate(df.groupby('activity_id')):
    color = colors[i % len(colors)]
    marker = markers[i % len(markers)]
    
    # Scatter plots with matching colors, markers, and marker size = 5
    axs[0, 0].scatter(group['segment_distance_km'], group['segment_time_seconds'], color=color, marker=marker, s=5)
    axs[0, 1].scatter(group['segment_distance_km'], group['segment_speed_kph'], color=color, marker=marker, s=5)
    axs[0, 2].scatter(group['segment_distance_km'], group['power_watt'], color=color, marker=marker, s=5)
    axs[1, 0].scatter(group['segment_distance_km'], group['heart_rate_bpm'], color=color, marker=marker, s=5)
    axs[1, 1].scatter(group['vertical_ascent_m'], group['segment_time_seconds'],  color=color, marker=marker, s=5)
    axs[1, 2].scatter(group['vertical_ascent_m'], group['segment_speed_kph'], color=color, marker=marker, s=5)

    # Add to legend handles only once per activity_id
    legend_handles.append(plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color, markersize=5, label=f'Activity {activity_id}'))

# Add dashed reference lines to segment_distance_km vs segment_time_seconds plot
seg_dist_x = np.linspace(0, 30, 100) 
seg_time_slow = 60 * seg_dist_x  
seg_time_fast = 240 * seg_dist_x  
axs[0, 0].plot(seg_dist_x, seg_time_slow, linestyle='dashed', lw = 1.5, color='g')
axs[0, 0].plot(seg_dist_x, seg_time_fast, linestyle='dashed', lw = 1.5, color='r')
#
VAM_x = np.linspace(0, 3000, 500) 
seg_speed_slow = (30/1000) * VAM_x  
seg_speed_fast = (10/2500) * VAM_x  
axs[1, 2].plot(VAM_x, seg_speed_slow, linestyle='dashed', lw = 1.5, color='g')
axs[1, 2].plot(VAM_x, seg_speed_fast, linestyle='dashed', lw=1.5, color='r')
#
with np.errstate(divide='ignore'):
    seg_time = np.where(VAM_x != 0., 1000000/(4*VAM_x), -2)
axs[1, 1].plot(VAM_x, seg_time, linestyle='dashed', lw = 1.5, color='b')

# Set labels and titles for each subplot
plot_labels = [
    ("Segment Distance (km)", "Segment Time (seconds)", "Segment Distance vs Time"),
    ("Segment Distance (km)", "Segment Speed (kph)", "Segment Distance vs Speed"),
    ("Segment Distance (km)", "Power (Watt)", "Segment Distance vs Power"),
    ("Segment Distance (km)", "Heart Rate (bpm)", "Segment Distance vs Heart Rate"),
    ("Vertical Ascent (m)", "Segment Time (seconds)", "Vertical Ascent vs Time"),
    ("Vertical Ascent (m)", "Segment Speed (kph)", "Vertical Ascent vs Speed")
]

for (i, j), (xlabel, ylabel, title) in zip(axis_limits.keys(), plot_labels):
    axs[i, j].set_xlabel(xlabel, fontsize=10)
    axs[i, j].set_ylabel(ylabel, fontsize=10)
    axs[i, j].set_title(title, fontsize=10)
    # Apply custom x and y limits
    axs[i, j].set_xlim(axis_limits[(i, j)]['xlim'])
    axs[i, j].set_ylim(axis_limits[(i, j)]['ylim'])

# Set a global title above all subplots
fig.suptitle(f'Athlete {athlete_id} Segment Analysis', fontsize=10)

# Add a single legend for all activity IDs (Right-aligned, single column)
#fig.legend(handles=legend_handles, loc='lower right', bbox_to_anchor=(1.0, 0), title="Activity IDs", frameon=False, ncol=5)

# Adjust layout for clarity
plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Leave space for legend and title
plt.show()








# import sqlite3
# import pandas as pd
# import numpy as np
# import os
# #
# import matplotlib.pyplot as plt
# from matplotlib import style
# plt.style.use('bmh')

# # 
# db_path = 'data/strava_segments.db'
# table_name = 'segment_activity'
# #
# # Connect to SQLite and fetch unique athlete_ids
# conn = sqlite3.connect(db_path)
# athlete_ids = pd.read_sql_query(f"SELECT DISTINCT athlete_id FROM {table_name}", conn)['athlete_id'].tolist()

# # Ensure directory exists for saving plots
# output_dir = "Plots/athlete/"
# os.makedirs(output_dir, exist_ok=True)

# ## ----- Eqs. for reference lines 
# seg_dist_x = np.linspace(0, 30, 100) 
# VAM_x = np.linspace(0, 3000, 500) 
# #
# seg_time_slow = 60 * seg_dist_x  
# seg_time_fast = 240 * seg_dist_x  
# #
# seg_speed_slow = (10/2500) * VAM_x  
# seg_speed_fast = (30/1000) * VAM_x  
# #
# with np.errstate(divide='ignore'):
#     seg_time = np.where(VAM_x != 0., 1000000/(4*VAM_x), -2)
# ## -----
# #
# # Loop through each athlete_id
# for athlete_id in athlete_ids:
#     print(f"Processing athlete_id {athlete_id}...")

#     # Fetch data for the current athlete_id
#     query = f"""
#         SELECT activity_id, segment_distance_km, segment_time_seconds, segment_speed_kph, 
#                power_watt, heart_rate_bpm, vertical_ascent_m
#         FROM {table_name}
#         WHERE athlete_id = ?
#     """
#     df = pd.read_sql_query(query, conn, params=(athlete_id,))

#     # Skip if no data for this athlete
#     if df.empty:
#         print(f"No data found for athlete_id {athlete_id}, skipping...")
#         continue

#     # Create figure with 2 rows and 3 columns
#     fig, axs = plt.subplots(2, 3, figsize=(15, 8))
#     plt.subplots_adjust(hspace=0.4)

#     # Define unique markers and colors for different activities
#     markers = ['o', 's', 'D', '^', 'v', 'p', 'X', '*', '<', '>']
#     colors = plt.cm.tab10.colors  # 10 distinct colors

#     # Create a legend handle for each activity_id
#     legend_handles = []
#     axis_limits = {
#         (0, 0): {'xlim': (0, 30), 'ylim': (0, 5000)},  # segment_distance_km vs segment_time_seconds
#         (0, 1): {'xlim': (0, 30), 'ylim': (0, 80)},    # segment_distance_km vs segment_speed_kph
#         (0, 2): {'xlim': (0, 30), 'ylim': (0, 800)},   # segment_distance_km vs power_watt
#         (1, 0): {'xlim': (0, 30), 'ylim': (0, 200)},   # segment_distance_km vs heart_rate_bpm
#         (1, 1): {'xlim': (0, 3000), 'ylim': (0, 5000)},# vertical_ascent_m vs segment_time_seconds
#         (1, 2): {'xlim': (0, 3000), 'ylim': (0, 60)}   # vertical_ascent_m vs segment_speed_kph
#     }

#     # Group data by activity_id and plot
#     for i, (activity_id, group) in enumerate(df.groupby('activity_id')):
#         color = colors[i % len(colors)]
#         marker = markers[i % len(markers)]
#         mSize = 4
#         # Scatter plots
#         axs[0, 0].scatter(group['segment_distance_km'], group['segment_time_seconds'], color=color, marker=marker, s=mSize)
#         axs[0, 1].scatter(group['segment_distance_km'], group['segment_speed_kph'], color=color, marker=marker, s=mSize)
#         axs[0, 2].scatter(group['segment_distance_km'], group['power_watt'], color=color, marker=marker, s=mSize)
#         axs[1, 0].scatter(group['segment_distance_km'], group['heart_rate_bpm'], color=color, marker=marker, s=mSize)
#         axs[1, 1].scatter(group['vertical_ascent_m'], group['segment_time_seconds'], color=color, marker=marker, s=mSize)
#         axs[1, 2].scatter(group['vertical_ascent_m'], group['segment_speed_kph'], color=color, marker=marker, s=mSize)

#         # Add to legend handles only once per activity_id
#         #legend_handles.append(plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color, markersize=8, label=f'Activity {activity_id}'))

#     # Add dashed reference lines 
#     axs[0, 0].plot(seg_dist_x, seg_time_slow, linestyle='dashed', lw = 1, color='r')
#     axs[0, 0].plot(seg_dist_x, seg_time_fast, linestyle='dashed', lw = 1, color='gray')
#     #
#     axs[1, 2].plot(VAM_x, seg_speed_slow, linestyle='dashed', lw = 1, color='r')
#     axs[1, 2].plot(VAM_x, seg_speed_fast, linestyle='dashed', lw=1, color='gray')
#     #
#     axs[1, 1].plot(VAM_x, seg_time, linestyle='dashed', lw = 1, color='r')
      
#     # Set labels and titles for each subplot
#     plot_labels = [
#         ("Segment Distance (km)", "Segment Time (seconds)", "Segment Distance vs Time"),
#         ("Segment Distance (km)", "Segment Speed (kph)", "Segment Distance vs Speed"),
#         ("Segment Distance (km)", "Power (Watt)", "Segment Distance vs Power"),
#         ("Segment Distance (km)", "Heart Rate (bpm)", "Segment Distance vs Heart Rate"),
#         ("Vertical Ascent (m)", "Segment Time (seconds)", "Vertical Ascent vs Time"),
#         ("Vertical Ascent (m)", "Segment Speed (kph)", "Vertical Ascent vs Speed")
#     ]
#     #
#     for (i, j), (xlabel, ylabel, title) in zip(axis_limits.keys(), plot_labels):
#         axs[i, j].set_xlabel(xlabel, fontsize=10)
#         axs[i, j].set_ylabel(ylabel, fontsize=10)
#         axs[i, j].set_title(title)
#         # Apply custom x and y limits
#         axs[i, j].set_xlim(axis_limits[(i, j)]['xlim'])
#         axs[i, j].set_ylim(axis_limits[(i, j)]['ylim'])
#     # 
#     fig.suptitle(f'athlete {athlete_id} all activities', fontsize=12)
#     fig.tight_layout()
#     plt.savefig(os.path.join(output_dir, f"id_{athlete_id}_summary.png"), bbox_inches='tight')
#     #
#     print(f"Saved plot for athlete_id {athlete_id} \n")
#     # fig.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 0.5), title="Activity IDs", frameon=False, ncol=1)
#     # plt.show()
#     plt.close(fig)  
# #
# conn.close()
# print("\nProcessing complete for all athletes.")




# import sqlite3
# import pandas as pd
# import numpy as np
# import os
# #
# import matplotlib.pyplot as plt
# from matplotlib import style
# plt.style.use('bmh')

# # 
# db_path = 'data/strava_segments.db'
# table_name = 'segment_activity'

# #
# conn = sqlite3.connect(db_path)
# athlete_query = f"SELECT DISTINCT athlete_id FROM {table_name}"
# athlete_ids = pd.read_sql_query(athlete_query, conn)['athlete_id'].tolist()

# # Ensure directory exists for saving plots
# output_dir = "Plots/athlete_avg_2/"
# os.makedirs(output_dir, exist_ok=True)

# ## ----- Eqs. for reference lines 
# seg_dist_x = np.linspace(0, 30, 100) 
# VAM_x = np.linspace(0, 3000, 500) 
# #
# seg_time_slow = 60 * seg_dist_x  
# seg_time_fast = 240 * seg_dist_x  
# #
# seg_speed_slow = (10/2500) * VAM_x  
# seg_speed_fast = (30/1000) * VAM_x  
# #
# with np.errstate(divide='ignore'):
#     seg_time = np.where(VAM_x != 0., 1000000/(4*VAM_x), -2)
# ## -----
# # Loop through each athlete_id
# for athlete_id in athlete_ids:
#     print(f"Processing athlete_id {athlete_id}...")

#     # Fetch data for the current athlete_id
#     query = f"""
#         SELECT activity_id, segment_distance_km, segment_time_seconds, segment_speed_kph, 
#                power_watt, heart_rate_bpm, vertical_ascent_m
#         FROM {table_name}
#         WHERE athlete_id = ?
#     """

#     df = pd.read_sql_query(query, conn, params=(athlete_id,))

#     # Skip if no data for this athlete
#     if df.empty:
#         print(f"No data found for athlete_id {athlete_id}, skipping...")
#         continue

#     # Groups the data by both activity_id and segment_distance_km then averages them
#     # df_avg = df.groupby(['activity_id', 'segment_distance_km'], as_index=False).agg({
#     #     'segment_time_seconds': 'mean',
#     #     'segment_speed_kph': 'mean',
#     #     'power_watt': 'mean',
#     #     'heart_rate_bpm': 'mean'
#     # }).rename(columns={
#     #     'segment_time_seconds': 'avg_segment_time_seconds',
#     #     'segment_speed_kph': 'avg_segment_speed_kph',
#     #     'power_watt': 'avg_power_watt',
#     #     'heart_rate_bpm': 'avg_heart_rate_bpm'
#     # })

#     df_avg = df.groupby(['segment_distance_km'], as_index=False).agg({
#         'segment_time_seconds': 'mean',
#         'segment_speed_kph': 'mean',
#         'power_watt': 'mean',
#         'heart_rate_bpm': 'mean'
#     }).rename(columns={
#         'segment_time_seconds': 'avg_segment_time_seconds',
#         'segment_speed_kph': 'avg_segment_speed_kph',
#         'power_watt': 'avg_power_watt',
#         'heart_rate_bpm': 'avg_heart_rate_bpm'
#     })


#     # Create figure with 2 rows and 3 columns and increase spacing
#     fig, axs = plt.subplots(2, 3, figsize=(15, 8))
#     plt.subplots_adjust(hspace=0.4)  # Increase spacing between rows by 15%

#     # Define unique markers and colors for different activities
#     markers = ['o', 's', 'D', '^', 'v', 'p', 'X', '*', '<', '>']
#     colors = plt.cm.tab10.colors  # 10 distinct colors

#     # Create a legend handle for each activity_id
#     legend_handles = []

#     # Manually set axis limits (Modify these as needed)
#     axis_limits = {
#         (0, 0): {'xlim': (0, 30), 'ylim': (0, 5000)},  # segment_distance_km vs segment_time_seconds
#         (0, 1): {'xlim': (0, 30), 'ylim': (0, 80)},    # segment_distance_km vs segment_speed_kph
#         (0, 2): {'xlim': (0, 30), 'ylim': (0, 800)},   # segment_distance_km vs power_watt
#         (1, 0): {'xlim': (0, 30), 'ylim': (0, 200)},   # segment_distance_km vs heart_rate_bpm
#         (1, 1): {'xlim': (0, 3000), 'ylim': (0, 5000)},# vertical_ascent_m vs segment_time_seconds
#         (1, 2): {'xlim': (0, 3000), 'ylim': (0, 60)}   # vertical_ascent_m vs segment_speed_kph
#     }
#     # Group data by activity_id and plot
#     # for i, (activity_id, group) in enumerate(df_avg.groupby('activity_id')):
#     #     color = colors[i % len(colors)]
#     #     marker = markers[i % len(markers)]
#     #     mSize = 4
#     #     # ** UPDATED: First four plots use averaged data **
#     #     axs[0, 0].scatter(group['segment_distance_km'], group['avg_segment_time_seconds'], color=color, marker=marker, s=mSize)
#     #     axs[0, 1].scatter(group['segment_distance_km'], group['avg_segment_speed_kph'], color=color, marker=marker, s=mSize)
#     #     axs[0, 2].scatter(group['segment_distance_km'], group['avg_power_watt'], color=color, marker=marker, s=mSize)
#     #     axs[1, 0].scatter(group['segment_distance_km'], group['avg_heart_rate_bpm'], color=color, marker=marker, s=mSize)

#     color = colors[0]  # Use a single color for the averaged data
#     marker = markers[0]
#     mSize = 4
#     # Plot averaged data (since we no longer have activity_id)
#     axs[0, 0].scatter(df_avg['segment_distance_km'], df_avg['avg_segment_time_seconds'], color=color, marker=marker, s=mSize)
#     axs[0, 1].scatter(df_avg['segment_distance_km'], df_avg['avg_segment_speed_kph'], color=color, marker=marker, s=mSize)
#     axs[0, 2].scatter(df_avg['segment_distance_km'], df_avg['avg_power_watt'], color=color, marker=marker, s=mSize)
#     axs[1, 0].scatter(df_avg['segment_distance_km'], df_avg['avg_heart_rate_bpm'], color=color, marker=marker, s=mSize)

#     # ** Last two plots (no averaging) **
#     for i, (activity_id, group) in enumerate(df.groupby('activity_id')):
#         color = colors[i % len(colors)]
#         marker = markers[i % len(markers)]
#         mSize = 4
#         axs[1, 1].scatter(group['vertical_ascent_m'], group['segment_time_seconds'], color=color, marker=marker, s=mSize)
#         axs[1, 2].scatter(group['vertical_ascent_m'], group['segment_speed_kph'], color=color, marker=marker, s=mSize)
#     #
#     # Add dashed reference lines 
#     axs[0, 0].plot(seg_dist_x, seg_time_slow, linestyle='dashed', lw = 1, color='r')
#     axs[0, 0].plot(seg_dist_x, seg_time_fast, linestyle='dashed', lw = 1, color='gray')
#     #
#     axs[1, 2].plot(VAM_x, seg_speed_slow, linestyle='dashed', lw = 1, color='r')
#     axs[1, 2].plot(VAM_x, seg_speed_fast, linestyle='dashed', lw=1, color='gray')
#     #
#     axs[1, 1].plot(VAM_x, seg_time, linestyle='dashed', lw = 1, color='r')

#     # Set labels and titles for each subplot
#     plot_labels = [
#         ("Segment Distance (km)", "Avg Segment Time (seconds)", "Segment Distance vs Avg Time"),
#         ("Segment Distance (km)", "Avg Segment Speed (kph)", "Segment Distance vs Avg Speed"),
#         ("Segment Distance (km)", "Avg Power (Watt)", "Segment Distance vs Avg Power"),
#         ("Segment Distance (km)", "Avg Heart Rate (bpm)", "Segment Distance vs Avg Heart Rate"),
#         ("Vertical Ascent (m)", "Segment Time (seconds)", "Vertical Ascent vs Time"),
#         ("Vertical Ascent (m)", "Segment Speed (kph)", "Vertical Ascent vs Speed")
#     ]

#     for (i, j), (xlabel, ylabel, title) in zip(axis_limits.keys(), plot_labels):
#         axs[i, j].set_xlabel(xlabel, fontsize=10)
#         axs[i, j].set_ylabel(ylabel, fontsize=10)
#         axs[i, j].set_title(title, fontsize=10)
#         # Apply custom x and y limits
#         axs[i, j].set_xlim(axis_limits[(i, j)]['xlim'])
#         axs[i, j].set_ylim(axis_limits[(i, j)]['ylim'])

#     # Set a global title above all subplots
#     fig.suptitle(f'Athlete {athlete_id} all activities (averaged)', fontsize=12)
#     fig.tight_layout()
#     # Save the figure as a PNG file
#     save_path = os.path.join(output_dir, f"id_{athlete_id}_summary.png")
#     plt.savefig(save_path, bbox_inches='tight')
#     print(f"Finished plot for athlete_id {athlete_id} \n")
#     plt.close(fig)  # Close the figure to free memory

# # Close database connection
# conn.close()
# print("\nProcessing complete for all athletes.")
