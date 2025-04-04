from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
##
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib import style
plt.style.use('bmh')

## Function that contains dictionary of tour-color attributes 
def get_tour_attributes():
    tour_color_attributes = {
        "tdf_results": {"name": "tdf", "FullName": "Tour de France", "color": "yellow"},
        "giro_results": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink"},
        "giro_results_plus": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink"},
        "vuelta_results": {"name": "vuelta", "FullName": "Vuelta a España","color": "red"}
    }
    return tour_color_attributes

# --- Data Fetching ---
def fetch_data(db_path, table_name, include_itt):
    conn = sqlite3.connect(db_path)
    query = f"""
        SELECT year, stage_num, distance, Stage_time_s, ITT, PCS_Rank, time_group, time_group_size
        FROM {table_name}
        WHERE Stage_time_s IS NOT NULL
    """
    if not include_itt:
        query += " AND ITT = 0"
    df = pd.read_sql_query(query, conn)

    # drop time values more than 24 hours (1440 minutes, 86400 seconds)
    outliers = df[df['Stage_time_s']  > 86400]
    # if not outliers.empty:
    #     print("Large time outlier data removed from year(s):", outliers['year'].unique())
    if not outliers.empty:
        print("The following outlier data of large time values were removed:")
        counts = outliers['year'].value_counts().sort_index()
        for year, count in counts.items():
            print(f"{year}\t{count}")
    #
    df = df[df['Stage_time_s'] <= 86400]

    # Convert to minutes
    df['Stage_time_s'] = df['Stage_time_s'] / 60

    conn.close()
    return df

# # --- Data Fetching ---
# def fetch_data(db_path, table_name, include_itt):
#     conn = sqlite3.connect(db_path)
#     query = f"""
#         SELECT year, stage_num, distance, Stage_time_s, ITT, PCS_Rank, time_group, time_group_size
#         FROM {table_name}
#         WHERE Stage_time_s IS NOT NULL
#     """
#     if not include_itt:
#         query += " AND ITT = 0"
#     df = pd.read_sql_query(query, conn)
#     #
#     outliers = df[df['Stage_time_s'] / 60 > 1200]
#     if not outliers.empty:
#         print("The following outlier data of large time values were removed:")
#         counts = outliers['year'].value_counts().sort_index()
#         for year, count in counts.items():
#             print(f"{year}\t{count}")
#     df = df[df['Stage_time_s'] / 60 <= 1200]
#     #
#     df['Stage_time_min'] = df['Stage_time_s'] / 60
#     df.drop(columns='Stage_time_s', inplace=True)
#     conn.close()
#     return df


def apply_outlier_filter(df, outlier_path, table_name):
    tour_attributes = get_tour_attributes()
    tour_name = tour_attributes[table_name]["name"]

    outlier_df = pd.read_csv(outlier_path)
    outlier_df = outlier_df[outlier_df['tour_name'] == tour_name]

    print("\nRemoved data from:")

    for _, row in outlier_df.iterrows():
        mask = (df['year'] == row['year']) & (df['stage_num'] == row['stage_num'])

        if pd.notna(row.get('rider_name')) and row['rider_name'].strip():
            mask &= (df['name'] == row['rider_name'])

        if mask.any():
            print(f"{tour_name}, {row['year']}, Stage-{row['stage_num']}")
            df = df[~mask]
    return df

def plot_time_group_averages(df,table_name,color_by,by_time_group):
    ##
    tour_attributes = get_tour_attributes()
    tour_color = tour_attributes[table_name]['color']
    tour_name = tour_attributes[table_name]['name']
    full_name = tour_attributes[table_name]['FullName']
    ##
    grouped = df.groupby(['year', 'stage_num', 'time_group']).agg({
        'distance': 'mean',
        'Stage_time_s': 'mean',
        'time_group_size': 'first'
    }).reset_index()
    #
    # #-------------------
    # fig, ax = plt.subplots(figsize=(12, 7))
    # if color_by and color_by in grouped.columns:
    #     unique_vals = grouped[color_by].unique()
    #     palette = sns.color_palette("Set2", len(unique_vals))
    #     color_map = dict(zip(unique_vals, palette))

    #     for val in unique_vals:
    #         subset = grouped[grouped[color_by] == val]
    #         ax.scatter(
    #             subset['distance'],
    #             subset['Stage_time_s'],
    #             s=subset['time_group_size'] * 3,
    #             alpha=0.6,
    #             edgecolors='black',
    #             label=str(val),
    #             color=color_map[val]
    #         )
    #     ax.legend(title=color_by)
    # else:
    #     ax.scatter(
    #         grouped['distance'],
    #         grouped['Stage_time_s'],
    #         s=grouped['time_group_size'] * 3,
    #         alpha=0.6,
    #         edgecolors='black',
    #         color=plot_color
    #     )

    # ax.set_title('Avg Stage Time per Time Group (Size = Group Size)')
    # ax.set_xlabel('Stage Distance (km)')
    # ax.set_ylabel('Stage Time (minutes)')
    # fig.tight_layout()
    # plt.savefig(f"Plots/Test/{tour_name}_time_group_plot_by_{color_by}.png", bbox_inches='tight')
    # plt.show()
    # #-------------------

    # #-------------------
    # if by_time_group is not None:
    #     grouped = grouped[grouped['time_group'] == by_time_group]
        
    #-------------------
    if color_by and color_by in grouped.columns:
        colors = grouped[color_by]
    else:
        colors = tour_color
    # 
    fig, ax = plt.subplots(figsize=(14,7))
    scatter = ax.scatter(
        grouped['distance'],
        grouped['Stage_time_s'],
        s=grouped['time_group_size'] * 3,
        alpha=0.6,
        c=colors,
        edgecolors='black',
        cmap='viridis' if color_by else None
    )
    if color_by:
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(color_by)
    # ax.scatter(
    #     grouped['distance'],
    #     grouped['Stage_time_s'],
    #     s=grouped['time_group_size'] * 2,
    #     c=colors,
    #     alpha=0.6,
    #     edgecolors='black',
    #     cmap='viridis' if color_by else None
    # )
    # Add reference line
    x_vals = grouped['distance'].sort_values().unique()
    # slopes = [1.0, 1.1, 1.2]
    # gray_shades = ['#333333', '#777777', '#BBBBBB']  # darker to lighter

    # for slope, gray, label in zip(slopes, gray_shades, [f"{s:.1f} min/km" for s in slopes]):
    #     ax.plot(x_vals, slope * x_vals, linestyle='--', linewidth=1, color=gray, label=label)
    # #
    y1 = 1.0 * x_vals
    y2 = 1.3 * x_vals
    ax.plot(x_vals, y1, ls='--', lw = 1, color='blue', label='1.0 min/km')
    ax.plot(x_vals, y2, ls='--', lw = 1, color='#777777', label='1.3 min/km')

    ax.set_title(f'Distance vs Stage Time (per unique time-group) for {full_name}')
    ax.set_xlabel('Stage Distance (km)')
    ax.set_ylabel('Stage Time (min)')
    ax.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"Plots/Test/{tour_name}_time_group_plot_by_{color_by}.png", bbox_inches='tight')
    plt.show()
    #-------------------

# def plot_beeswarm(df,table_name,color_by):
#     ##
#     tour_attributes = get_tour_color_attributes()
#     plot_color = tour_attributes[table_name]['color']
#     tour_name = tour_attributes[table_name]['name']
#     ##
#     #-------------------
#     fig, ax = plt.subplots(figsize=(12,7))
#     sns.stripplot(x='distance', y='Stage_time_s', data=df, jitter=True, alpha=0.6)
#     ax.set_title('Beeswarm Plot: Distance vs Stage Time')
#     ax.set_xlabel('Stage Distance (km)')
#     ax.set_ylabel('Stage Time (seconds)')
#     fig.tight_layout()
#     plt.savefig(f"Plots/Test/{tour_name}_beeswarm_plot_by_{color_by}.png", bbox_inches='tight')
#     plt.show()
#     #-------------------

# def plot_contour(df,table_name, color_by):
#     ##
#     tour_attributes = get_tour_color_attributes()
#     plot_color = tour_attributes[table_name]['color']
#     tour_name = tour_attributes[table_name]['name']
#     ##
#     #-------------------
#     fig, ax = plt.subplots(figsize=(12,7))
#     sns.kdeplot(
#         x=df['distance'],
#         y=df['Stage_time_s'],
#         fill=True,
#         cmap='viridis',
#         bw_adjust=0.5,
#         levels=100,
#         thresh=0.01
#     )
#     ax.set_title('Contour Heatmap: Distance vs Stage Time')
#     ax.set_xlabel('Stage Distance (km)')
#     ax.set_ylabel('Stage Time (seconds)')
#     fig.tight_layout()
#     plt.savefig(f"Plots/Test/{tour_name}_Contour_plot_by_{color_by}.png", bbox_inches='tight')
#     plt.show()
#     #-------------------

def main():
    ##-----------------------
    ## control parameters
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results_plus"
    blacklist_file_path = "outliers.csv"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    include_itt = True
    color_by = 'stage_num'
    # color_by = 'year'
    # color_by = None
    by_time_group = None
    #-----------------------

    print("\nFetching data...")
    df = fetch_data(gt_db_path, table_name, include_itt)

    print("\nFiltering out using outliers.csv...")
    df = apply_outlier_filter(df, blacklist_file_path, table_name)

    print("\nplotting...\n")
    plot_time_group_averages(df,table_name,color_by, by_time_group)
    # plot_beeswarm(df,table_name)
    # plot_contour(df,table_name)

if __name__  == '__main__':
    main()

# import pandas as pd
# import matplotlib.pyplot as plt
# import joypy

# # Your grouped data
# data = [
#     (1.0, 1.52), (1.0, 1.94), (1.0, 2.44), (1.0, 2.44), (1.0, 3.04), (1.0, 3.36), (1.0, 4.53),
#     (1.5, 1.63), (1.5, 1.85), (1.5, 1.99), (1.5, 2.51), (1.5, 3.74), (1.5, 3.99), (1.5, 4.04),
#     (1.5, 5.33), (1.5, 5.53), (1.5, 6.10),
#     (2.0, 1.73), (2.0, 1.83), (2.0, 2.09), (2.0, 2.61), (2.0, 2.84), (2.0, 3.99), (2.0, 4.09), (2.0, 4.48),
#     (2.5, 1.75), (2.5, 1.97), (2.5, 2.47), (2.5, 2.64), (2.5, 3.84), (2.5, 3.33), (2.5, 3.33),
#     (2.5, 4.15), (2.5, 5.54),
#     (3.0, 1.81), (3.0, 1.95), (3.0, 2.15), (3.0, 2.31), (3.0, 3.24), (3.0, 3.89), (3.0, 4.04),
#     (3.0, 4.04), (3.0, 5.45), (3.0, 6.21)
# ]

# # Create DataFrame
# df = pd.DataFrame(data, columns=['x', 'y'])

# # Generate ridgeline plot
# plt.figure(figsize=(10, 10))
# fig, axes = joypy.joyplot(
#     df, 
#     by='x', 
#     column='y', 
#     kind='kde', 
#     overlap=1.2,
#     linewidth=1,
#     colormap=plt.cm.Set3,
#     figsize=(10, 10)
# )
# plt.title('Ridgeline Plot of Y Distributions by X')
# plt.xlabel('Y Value')
# plt.tight_layout()
# plt.show()


# # Summary trend plot: mean y ± std per x group
# # Compute mean and std of y for each x
# summary_stats = df.groupby('x')['y'].agg(['mean', 'std']).reset_index()

# # Plot with error bars
# plt.figure(figsize=(10, 6))
# plt.errorbar(
#     summary_stats['x'],
#     summary_stats['mean'],
#     yerr=summary_stats['std'],
#     fmt='o-',
#     capsize=4,
#     color='steelblue'
# )
# plt.title('Mean Y with Standard Deviation per X')
# plt.xlabel('X Value')
# plt.ylabel('Y Value')
# plt.grid(True)
# plt.tight_layout()
# plt.show()
