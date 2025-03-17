import json
import sqlite3
from datetime import datetime
from typing import Optional

from data.schemas import Ride, Rider


def hms_to_seconds(hms: dict[int, str]) -> Optional[int]:
    try:
        hms_value = hms["move_time"]  # Ensure this is a valid key
        if isinstance(hms_value, str):  # Check if it's a string
            if hms_value.endswith("s"):  # Only seconds format (e.g., "2s")
                return int(hms_value[:-1])  # Convert "2s" -> 2

            parts = list(map(int, hms_value.split(":")))

            if len(parts) == 3:  # H:M:S format
                h, m, s = parts
            elif len(parts) == 2:  # M:S format (assume 0 hours)
                h, m, s = 0, *parts
            else:
                raise ValueError("Invalid time format. Expected H:M:S, M:S, or Ns")

            return h * 3600 + m * 60 + s  # Corrected return statement

    except (KeyError, ValueError, TypeError):  # Handle possible exceptions
        return None


def get_elevation(row_json):
    try:
        return row_json["elevation"].replace(",", "").split(" ")[0]
    except (KeyError, AttributeError):
        return None  # Return None if key is missing


def safe_get_wap(row_json):
    try:
        return row_json["wap"].split(" ")[0]  # Extract value safely
    except (KeyError, AttributeError):
        return None  # Return None if key is missing


def mdy_to_ymd(d):
    try:
        date = datetime.strptime(d, "%b %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        date = datetime.strptime(d, "%B %d %Y").strftime("%Y-%m-%d")
    return date


def get_rider(athlete_id, table_name, NAME_DB_PATH, ACTIVITY_DB_PATH):
    # Fetch rider name
    with sqlite3.connect(NAME_DB_PATH) as conn:
        cursor = conn.cursor()
        # Fetch rider name
        cursor.execute("SELECT name FROM strava_names WHERE athlete_id = ?", (athlete_id,))
        rider_row = cursor.fetchone()
        if not rider_row:
            return None  # Rider not found

        rider_name = rider_row[0]

    # Fetch rides
    with sqlite3.connect(ACTIVITY_DB_PATH) as conn:
        cursor = conn.cursor()
        rides_query = f"SELECT * FROM {table_name} WHERE athlete_id=?"
        # Execute with a tuple for values
        ride_rows = cursor.execute(rides_query, (athlete_id,)).fetchall()

    # # Convert SQL rows to Pydantic models
    rides = [
        Ride(
            activity_id=row[0],
            distance=json.loads(row[4])["dist"].split(" ")[0],
            time=hms_to_seconds(json.loads(row[4])),
            elevation=get_elevation(json.loads(row[4])),
            avg_power=safe_get_wap(json.loads(row[4])),
            tour_year=row[2],
            ride_date=mdy_to_ymd(row[3]),
        )
        for row in ride_rows
    ]
    rider = Rider(strava_id=athlete_id, name=rider_name, rides=rides)

    return rider
