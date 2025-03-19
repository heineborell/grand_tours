import sqlite3

import pandas as pd

from data.database import get_rider


def fetch_riders(DB_PATH, tour, year):
    """Enter tour-year e.g. 2024-tdf to get the list of rider_ids"""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT DISTINCT(athlete_id) FROM strava_table WHERE tour_year='{tour}-{year}'"
    riders = conn.execute(query).fetchall()
    return [rider[0] for rider in riders]


def create_training_dataframe(rider_ids, NAME_DB_PATH, ACTIVITY_DB_PATH):
    """Given a list of riders get the ride dataframe and concat all dfs."""
    dfs = []
    for r in rider_ids:
        rider = get_rider(r, NAME_DB_PATH, ACTIVITY_DB_PATH)
        if rider:  # Ensure rider is not None
            dfs.append(rider.to_dataframe())

    dfs = [df for df in dfs if not df.empty]
    # Optionally, concatenate all DataFrames into one
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)

    return final_df
