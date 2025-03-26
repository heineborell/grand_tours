import json
import os
import sqlite3

import numpy as np
import pandas as pd
from rich import print as print

from data.database import get_rider


def fetch_riders(db_path, tour, year):
    # Load config
    with open(db_path, "r") as f:
        db_path = json.loads(f.read())

    grand_tours_db_path = os.path.expanduser(db_path["global"]["grand_tours_db_path"])

    """Enter tour and year e.g. 2024, tdf to get the list of rider_ids"""
    conn = sqlite3.connect(grand_tours_db_path)
    query = f"SELECT DISTINCT(athlete_id) FROM strava_table WHERE tour_year='{tour}-{year}'"
    riders = conn.execute(query).fetchall()
    return [rider[0] for rider in riders]


def create_dataframe(rider_ids, tour, year, db_path, training=True):
    """Given a list of riders get the ride dataframe and concat all dfs."""
    print(f"Creating dataframe training:{training}")
    dfs = []
    for r in rider_ids:
        rider = get_rider(r, tour, year, db_path, training)
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
    data = data[(data["distance"] > 0) & (data["elevation"] > 0)].dropna(subset=["time"])
    return data


def create_features(data, training):
    # Feature Engineering
    data["time_delta"] = (data["race_start_day"] - data["ride_day"]).apply(lambda x: x.days)
    if training:
        data = data.drop(index=data.loc[data["ride_day"] > data["race_start_day"]].index)
    return data
