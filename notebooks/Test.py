import sqlite3
import pandas as pd
import numpy as np
#
import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('bmh')

## Function that contains dictionary of tour-color attributes 
def get_tour_color_attributes():
    tour_color_attributes = {
        "tdf_results": {"name": "TDF", "color": "yellow"},
        "giro_results": {"name": "Giro", "color": "pink"},
        "vuelta_results": {"name": "Vuelta", "color": "red"}
    }
    return tour_color_attributes

def convert_time_to_seconds(time_str):
    """
    Convert a time string in HH:MM:SS or MM:SS format into total seconds.
    Input:
        time_str (str): A string representing time in either "HH:MM:SS" or "MM:SS" format.
    Returns:
        int or float: The total time in seconds. If input is invalid, returns NaN.
    """
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return np.nan
    except:
        return np.nan
    

def seconds_to_hms(seconds):
    """
    Convert a total number of seconds into a formatted HH:MM:SS string.
    Input:
        seconds (int or float): The total number in seconds.
    Returns:
        str: A string representing the time in "HH:MM:SS" format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def fetch_and_plot_data(db_path, table_name, fit_params):
    ##
    tour_attributes = get_tour_color_attributes()
    plot_color = tour_attributes[table_name]['color']
    tour_name = tour_attributes[table_name]['name']
    ##
    conn = sqlite3.connect(db_path)
    query = f"""SELECT year, stage_num, distance, time, ITT FROM {table_name} WHERE time IS NOT NULL """
    if not fit_params['Include ITT']:
        query += " AND ITT = 0"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if fit_params['Winners only']:
        df = df.sort_values(by=['year', 'stage_num']).groupby(['year', 'stage_num']).first().reset_index()
        df['time'] = df['time'].apply(convert_time_to_seconds)
    df = df.dropna()
    
    outliers = df[df['time'] / 60 > 1200]
    if not outliers.empty:
        print("Outlier data detected from year:", outliers['year'].unique())
    df = df[df['time'] / 60 <= 1200]
    
    X = df[['distance']].values
    y = df['time'].values / 60

    #-------------------
    fig, ax = plt.subplots(figsize=(10, 6.5))
    # plot data
    ax.scatter(X, y, color=plot_color, edgecolors='k', s=15, label=f"{tour_name} Data")
    ax.set_xlabel('Distance (km)', fontsize=14)
    ax.set_ylabel('Time (minutes)', fontsize=14)
    ax.set_title(f'distance vs time for {tour_name}',fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    ax.legend(fontsize=12)
    fig.tight_layout()
    # plt.savefig(f"Plots/Test/{tour_name}_Linear_Regression.pdf", bbox_inches='tight')
    plt.show()
    #-------------------


def main():
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    include_itt = True
    normalize = False
    winners_only = False
    ##-----------------------
    fit_params = {"Include ITT": include_itt, "Normalize": normalize, "Winners only": winners_only}

    fetch_and_plot_data(gt_db_path, table_name,fit_params)

if __name__ == '__main__':
    main()
