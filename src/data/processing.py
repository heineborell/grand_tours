import json
import os
import sqlite3

import numpy as np
import pandas as pd
from rich import print as print

from data.database import get_rider


def fetch_riders(db_path, tour, year):
    """Given tour, year and database path it returns a list of strava_ids"""
    # Load config
    with open(db_path, "r") as f:
        db_path = json.loads(f.read())

    # selects the grand_tours database path from path json file
    grand_tours_db_path = os.path.expanduser(db_path["global"]["grand_tours_db_path"])

    conn = sqlite3.connect(grand_tours_db_path)
    query = f"SELECT DISTINCT(athlete_id) FROM strava_table WHERE tour_year='{tour}-{year}'"
    riders = conn.execute(query).fetchall()
    return [rider[0] for rider in riders]


def fetch_features(db_path, tour, year):
    """Given tour, year and database path it returns a list of strava_ids"""
    # Load config
    with open(db_path, "r") as f:
        db_path = json.loads(f.read())

    # selects the grand_tours database path from path json file
    grand_tours_db_path = os.path.expanduser(db_path["global"]["grand_tours_db_path"])

    conn = sqlite3.connect(grand_tours_db_path)
    query = (
        f"SELECT year, TRIM(stage) AS stage, profile_score, startlist_quality "
        f"FROM {tour}_results "
        f"WHERE year = {year} "
        f"GROUP BY stage"
    )
    return pd.read_sql_query(query, conn)


def create_dataframe(rider_ids, tour, year, db_path, training=True, segment_data=False):
    """Given a list of riders get the ride dataframe and concat all dfs."""
    print(f"Creating dataframe training:{training}")
    dfs = []
    for r in rider_ids:
        rider = get_rider(r, tour, year, db_path, training, segment_data)
        if rider:  # Ensure rider is not None
            dfs.append(rider.to_dataframe())

    # here if a dataframe is all NaN they are dropped or if an entry is None its
    # changed into NaN.
    dfs = [df for df in dfs if not df.empty if not df.empty and not df.isna().all().all()]
    dfs = [df.map(lambda x: np.nan if (x is pd.NA or x is None) else x) for df in dfs]

    # Optionally, concatenate all DataFrames into one
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)

    return final_df


def clean_dataframe(data):
    """Choose the rides with distance and elevation greater than zero."""
    data = data[(data["distance"] > 0) & (data["elevation"] > 0)].dropna(subset=["time"])
    return data


def create_features(data, training):
    """Create new features for the database."""
    # Feature Engineering
    data["time_delta"] = (data["race_start_day"] - data["ride_day"]).apply(lambda x: x.days)
    try:
        data["elevation_ratio"] = data["elevation"] / (data["elevation"] + 1000 * data["distance"])
    except KeyError:
        pass
    if training:
        data = data.drop(index=data.loc[data["ride_day"] > data["race_start_day"]].index)
        data = data.drop(index=data.loc[data["time_delta"] <= 0].index)
    if not training:
        pass
    return data
