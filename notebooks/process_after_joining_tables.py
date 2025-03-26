import sqlite3
import pandas as pd

def process_database(db_path, table_names):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS test_write_permission (id INTEGER);')
        conn.execute('DROP TABLE test_write_permission;')
        same_db = True
    except sqlite3.OperationalError:
        same_db = False
        conn = sqlite3.connect('Grand_Tours_Plus.db')

    all_data = []

    for table_name in table_names:
        original_conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", original_conn)
        original_conn.close()

        print(f"\nProcessing table: {table_name}")

        if 'stage_number' in df.columns:
            print("Dropping 'stage_number' column if present...")
            df.drop(columns=['stage_number'], inplace=True)

        print("Calculating then adding Stage_time and Stage_time_s...")
        df = add_stage_times(df)

        print("Assigning PCS_Rank...")
        df = assign_rank(df)

        print("Flagging issues...")
        df = flag_issues(df)

        print("Adding time_group and time_group_size...")
        df = add_time_groups(df)

        print("Adding race identifier...")
        race_attributes = get_race_attributes()
        race_name = race_attributes[table_name]['name']
        df.insert(0, 'race', race_name)

        all_data.append(df)

    print("\nCombining data from all races...")
    combined_df = pd.concat(all_data, ignore_index=True)

    print("Reordering columns...")
    preferred_order = [
        "race", "year", "stage", "stage_num", "ITT", "PCS_Rank", "name", "time", "Stage_time", "Stage_time_s",
        "date", "start_time", "winner_avg_speed", "distance", "profile_score", "vertical_meters",
        "Departure:", "Arrival:", "startlist_quality", "won_how", "avg_temperature"
    ]
    remaining = [col for col in combined_df.columns if col not in preferred_order and col != 'issue_flag']
    final_order = preferred_order + remaining + ['issue_flag']
    combined_df = combined_df[[col for col in final_order if col in combined_df.columns]]

    combined_df.sort_values(by=['race', 'year', 'stage_num', 'PCS_Rank'], ascending=[True, False, True, True], inplace=True)

    print("Writing combined processed data to 'grand_tour_combined_plus' table...")
    combined_df.to_sql('grand_tour_combined_plus', conn, if_exists='replace', index=False)
    conn.close()
