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

# chose the athlete_id and activity_id
athlete_id = 2542098  
activity_id = 6939068797 

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query to retrieve data for the given athlete_id and activity_id
query = f"""
    SELECT segment_distance_km, segment_time_seconds, segment_speed_kph, power_watt,
           heart_rate_bpm, vertical_ascent_m
    FROM {table_name}
    WHERE athlete_id = ? AND activity_id = ?
"""
cursor.execute(query, (athlete_id, activity_id))
data = cursor.fetchall()
conn.close()

# Check if data is available
if not data:
    print(f"No data found for athlete_id {athlete_id} and activity_id {activity_id}")
else:
    # Convert data to structured lists
    segment_distance_km, segment_time_seconds, segment_speed_kph, power_watt, \
    heart_rate_bpm, vertical_ascent_m = zip(*data)

    # Create a 2-row, 3-column figure
    fig, axs = plt.subplots(2, 3, figsize=(14, 8))

    # Define the plots with axis range controls (set None to auto-scale)
    plot_configs = [
        (axs[0, 0], segment_distance_km, segment_time_seconds, "Segment Distance (km)", "Segment Time (sec)", "Distance vs Time", (0, 5), (None, None)),
        (axs[0, 1], segment_distance_km, segment_speed_kph, "Segment Distance (km)", "Speed (kph)", "Distance vs Speed", (0,5), (None, None)),
        (axs[0, 2], segment_distance_km, power_watt, "Segment Distance (km)", "Power (W)", "Distance vs Power", (0,5), (None, None)),
        (axs[1, 0], segment_distance_km, heart_rate_bpm, "Segment Distance (km)", "Heart Rate (bpm)", "Distance vs HR", (0,5), (None, None)),
        (axs[1, 1], vertical_ascent_m, segment_time_seconds, "Vertical Ascent (m)", "Segment Time (sec)", "Ascent vs Time", (0, 3000), (None, None)),
        (axs[1, 2], vertical_ascent_m, segment_speed_kph, "Vertical Ascent (m)", "Speed (kph)", "Ascent vs Speed", (0, 3000), (None, None)),
    ]

    # Plot data
    for ax, x_data, y_data, x_label, y_label, title, x_range, y_range in plot_configs:
        ax.scatter(x_data, y_data, color='blue', marker='o', label=f'Activity {activity_id}', s=7, alpha=0.7)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(title)
        ax.grid(True)

        # Apply user-defined axis ranges
        if x_range[0] is not None and x_range[1] is not None:
            ax.set_xlim(x_range)
        if y_range[0] is not None and y_range[1] is not None:
            ax.set_ylim(y_range)

    #
    fig.suptitle(f'athlete {athlete_id} performance analysis', fontsize=12)

    # Add a legend
    fig.legend([f'{activity_id}'], loc='lower center', bbox_to_anchor=(0.90, 0.5), title="activity_ID")

    plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Adjust layout to fit title and legend
    plt.show()
