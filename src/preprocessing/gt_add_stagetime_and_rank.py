from pathlib import Path
import sqlite3
import pandas as pd
from datetime import timedelta

## Function that contains dictionary of tour-color attributes 
def get_tour_attributes():
    tour_color_attributes = {
        "tdf_results": {"name": "tdf", "FullName": "Tour de France", "color": "yellow"},
        "giro_results": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink"},
        "giro_results_plus": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink"},
        "vuelta_results": {"name": "vuelta", "FullName": "Vuelta a España","color": "red"}
    }
    return tour_color_attributes


def parse_time_to_seconds(t):
    """
    Convert a time string (hh:mm:ss or mm:ss) into total seconds.
    Input:
        t (str): Time string, e.g., '3:14:23' or '0:27'
    Output:
        int or None: Time in seconds, or None if invalid or placeholder
    """
    if pd.isna(t) or t in ['-', ',,']:
        return None
    parts = t.strip("'").split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return None

def seconds_to_time_str(seconds):
    """
    Convert seconds to a string in hh:mm:ss format.
    Input:
        seconds (int): Time in seconds
    Output:
        str: Formatted time string
    """
    return str(timedelta(seconds=int(seconds)))

def add_stage_times(df):
    """
    Add 'Stage_time' and 'Stage_time_s' columns to the DataFrame, computed from fastest times and splits.
    Input:
        df (pd.DataFrame): Race data with 'time' values in text
    Output:
        pd.DataFrame: Updated DataFrame with 'Stage_time' and 'Stage_time_s' columns
    """
    from datetime import timedelta

    df = df.copy()
    df['Stage_time'] = None
    df['Stage_time_s'] = None

    def parse_time_to_seconds(t):
        if pd.isna(t) or t in ['-', 'Null', ',,']:
            return None
        parts = t.split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return None

    def seconds_to_str(seconds):
        return str(timedelta(seconds=int(seconds)))

    def process_group(group, df_target):
        stage_seconds = None
        last_split = 0

        for idx in group.index:
            raw_time = df_target.at[idx, 'time']

            # Determine fastest-time (hh:mm:ss)
            if stage_seconds is None and raw_time and raw_time.count(':') == 2:
                stage_seconds = parse_time_to_seconds(raw_time)
                last_split = 0
                total_time = stage_seconds
            elif raw_time == ',,':
                total_time = stage_seconds + last_split if stage_seconds is not None else None
            elif raw_time and raw_time.count(':') >= 1:
                split = parse_time_to_seconds(raw_time)
                if split is not None:
                    last_split += split
                total_time = stage_seconds + last_split if stage_seconds is not None else None
            else:
                total_time = None

            if total_time is not None:
                df_target.at[idx, 'Stage_time_s'] = total_time
                df_target.at[idx, 'Stage_time'] = seconds_to_str(total_time)

    # Group fully-specified rows
    full_mask = df[['year', 'stage_num', 'winner_avg_speed', 'distance']].notna().all(axis=1)
    full_df = df[full_mask]
    partial_df = df[~full_mask]

    for _, group in full_df.groupby(['year', 'stage_num', 'winner_avg_speed', 'distance']):
        process_group(group, full_df)

    for _, group in partial_df.groupby(['year', 'stage_num']):
        process_group(group, partial_df)

    # Merge back
    df.update(full_df)
    df.update(partial_df)

    return df


def assign_rank(df):
    """
    Assign finishing Procyslingstats (PCS) rank to each rider within their stage group.
    Input:
        df (pd.DataFrame): Race data
    Output:
        pd.DataFrame: Updated DataFrame with 'PCS_Rank' column
    """
    df = df.copy()
    df['PCS_Rank'] = None

    def group_and_rank(df, group_keys):
        for _, group in df.groupby(group_keys):
            has_time = group['time'].notna() & ~group['time'].isin(['-', 'Null'])
            with_time = group[has_time].copy()
            without_time = group[~has_time].copy()

            with_time['PCS_Rank'] = range(1, len(with_time) + 1)
            without_time['PCS_Rank'] = range(len(with_time) + 1, len(group) + 1)

            df.loc[with_time.index, 'PCS_Rank'] = with_time['PCS_Rank']
            df.loc[without_time.index, 'PCS_Rank'] = without_time['PCS_Rank']
        return df

    full_mask = df[['year', 'stage_num', 'winner_avg_speed', 'distance']].notna().all(axis=1)
    df = group_and_rank(df[full_mask], ['year', 'stage_num', 'winner_avg_speed', 'distance']).combine_first(df)
    df = group_and_rank(df[~full_mask], ['year', 'stage_num']).combine_first(df)

    df['PCS_Rank'] = df['PCS_Rank'].fillna(9999).infer_objects(copy=False).astype(int)
    return df

def add_time_groups(df):
    df['time_group'] = None
    df['time_group_size'] = None

    for (year, stage_num), group in df.groupby(['year', 'stage_num']):
        subgroup = group.dropna(subset=['Stage_time_s']).copy()
        unique_times = subgroup['Stage_time_s'].sort_values().unique()
        time_group_map = {t: i + 1 for i, t in enumerate(unique_times)}
        size_map = subgroup.groupby('Stage_time_s').size().to_dict()

        for idx in subgroup.index:
            time_val = df.at[idx, 'Stage_time_s']
            df.at[idx, 'time_group'] = time_group_map.get(time_val)
            df.at[idx, 'time_group_size'] = size_map.get(time_val)

    df['time_group'] = df['time_group'].astype('Int64')
    df['time_group_size'] = df['time_group_size'].astype('Int64')
    return df


def flag_issues(df):
    """
    Add a column 'issue_flag' to identify rows with missing group keys or stage time.
    Input:
        df (pd.DataFrame): Data with computed stage times and ranks
    Output:
        pd.DataFrame: Updated DataFrame with 'issue_flag' column
    """
    issue_flags = []
    for idx, row in df.iterrows():
        missing_keys = any(pd.isna(row[k]) for k in ['year', 'stage_num', 'winner_avg_speed', 'distance'])
        missing_time = pd.isna(row['Stage_time_s'])

        if missing_keys and missing_time:
            issue_flags.append('both')
        elif missing_keys:
            issue_flags.append('missing_group_keys')
        elif missing_time:
            issue_flags.append('missing_stage_time')
        else:
            issue_flags.append(None)

    df['issue_flag'] = issue_flags
    return df

def process_database(db_path, table_name):
    """
    Main function to process a given "tour_results" table in grand_tours and create 'tour_plus' table with added info.
    Input:
        db_path (str): Path to SQLite database containing 'tour_results'
    Output:
        Creates/updates 'tour_results_plus' table in the same or a new SQLite database
    """
    print("\nStarting process_database...")

    # Try to connect with write permission
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS test_write_permission (id INTEGER);')
        conn.execute('DROP TABLE test_write_permission;')
        same_db = True
    except sqlite3.OperationalError:
        same_db = False
        conn = sqlite3.connect('Grand_Tours_Plus.db')

    ##-----
    print(f"\nReading {table_name} table from grand_tours database...")
    original_conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", original_conn)
    original_conn.close()

    ##-----
    print("\nDropping 'stage_number' column if present...")
    if 'stage_number' in df.columns:
        df.drop(columns=['stage_number'], inplace=True)

    ##-----
    print("Calculating then adding Stage_time and Stage_time_s...")
    df = add_stage_times(df)

    ##-----
    print("\nAssigning PCS_Rank...")
    df = assign_rank(df)

    ##-----
    print("\nFlagging issues...")
    df = flag_issues(df)

    ##-----
    print("\nAdding time_group and time_group_size...")
    df = add_time_groups(df)
    
    ##-----
    print("\nReordering columns...")
    preferred_order = [
        "year", "stage", "stage_num", "ITT", "PCS_Rank", "name", "time", "Stage_time", "Stage_time_s",
        "date", "start_time", "winner_avg_speed", "distance", "profile_score", "vertical_meters",
        "Departure:", "Arrival:", "startlist_quality", "won_how", "avg_temperature"
    ]
    remaining = [col for col in df.columns if col not in preferred_order and col != 'issue_flag']
    final_order = preferred_order + remaining + ['issue_flag']
    df = df[[col for col in final_order if col in df.columns]]

    ##-----
    print("\nSorting rows...")
    df.sort_values(by=['year', 'stage_num', 'PCS_Rank'], ascending=[False, True, True], inplace=True)

    ##-----
    print(f"\nWriting {table_name}_plus to database...")
    df.to_sql(f'{table_name}_plus', conn, if_exists='replace', index=False)
    conn.close()

    ##-----
    print("\nProcess completed successfully.\n")
    ##-----


def main():
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results"

    tour_attributes = get_tour_attributes()

    table_names = [tour_attributes[key]['name'] for key in tour_attributes]

    process_database(gt_db_path, table_names)


if __name__  == '__main__':
    main()


'''
Given a text file of black-listed riders like 

name         | year  | stage_num
-------------|-------|----------
"Rider A"    | 2024  | NULL
"Rider B"    | NULL  | NULL
"Rider C"    | 2023  | 4

Run the following function before saving or using the '{table_name}_plus' table

##------------
def apply_blacklist(df, blacklist_df):
    mask = pd.Series([False] * len(df))
    for _, blk in blacklist_df.iterrows():
        cond = (df['name'] == blk['name'])
        if pd.notna(blk.get('year')):
            cond &= (df['year'] == blk['year'])
        if pd.notna(blk.get('stage_num')):
            cond &= (df['stage_num'] == blk['stage_num'])
        mask |= cond
    return df[~mask]
##------------

by calling the apply_blacklist() function inside process_database() via:
df = apply_blacklist(df, blacklist_df)

'''