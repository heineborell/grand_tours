import sqlite3


def fetch_riders(DB_PATH, tour, year):
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT DISTINCT(athlete_id) FROM strava_table WHERE tour_year='{tour}-{year}'"
    riders = conn.execute(query).fetchall()
    return [rider[0] for rider in riders]


# def create_training_dataframe():
#     rider_ids = [101, 102, 103]  # Example: Fetch some riders
#     dfs = [fetch_rider(r).to_dataframe() for r in rider_ids if fetch_rider(r)]
#
#     return pd.concat(dfs, ignore_index=True)
