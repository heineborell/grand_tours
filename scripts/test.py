import ast
import getpass
import sqlite3

import pandas as pd

import segment_analyse

if __name__ == "__main__":
    username = getpass.getuser()

    grand_tour = "tdf"
    # grand_tour = "giro"
    year = 2024

    conn = sqlite3.connect(f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/segment_details.db")

    segment_query = f"SELECT * FROM segment_details_data WHERE tour_year = '{grand_tour}-{year}'"

    df = pd.read_sql_query(segment_query, conn)
    activity_ids = set(df["stage"])
    nonoverlapping_segments = pd.DataFrame()
    for id in activity_ids:
        print(id)
        stage_df = df.loc[df["stage"] == id].reset_index(drop=True)
        segment_list = [ast.literal_eval(k) for k in stage_df["end_points"]]
        longest_seg, max_coverage, greedy = segment_analyse.segment_picker(segment_list, report=False)
        nonoverlapping_segments = pd.concat(
            [nonoverlapping_segments, segment_analyse.name_getter(stage_df, max_coverage)]
        )

    conn = sqlite3.connect(f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/grand_tours.db")

    strava_query = (
        f"SELECT activity_id, athlete_id, strava_distance, stage, segment "
        f"FROM strava_table WHERE tour_year = '{grand_tour}-{year}'"
    )
    df = pd.read_sql_query(strava_query, conn)
    print(df)
