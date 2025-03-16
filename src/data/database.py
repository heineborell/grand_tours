import os
import sqlite3

# from data.schemas import Rider, Ride


def fetch_rides(db_path_activity, db_path_name):
    # Connect to an in-memory database
    conn_memory = sqlite3.connect(":memory:")
    cursor = conn_memory.cursor()

    # Convert to absolute paths
    db_path_activity = os.path.abspath(db_path_activity)
    db_path_name = os.path.abspath(db_path_name)

    # Attach databases safely
    cursor.execute("ATTACH DATABASE ? AS db1", (db_path_activity,))
    cursor.execute("ATTACH DATABASE ? AS db2", (db_path_name,))

    # Create a query that joins data from both databases
    query = """
    SELECT *
    FROM db1.stats_data t1
    INNER JOIN db2.strava_names t2 ON t1.athlete_id = t2.athlete_id
    """

    # Fetch directly with SQLite
    cursor.execute(query)
    riders_data = cursor.fetchall()

    return riders_data
