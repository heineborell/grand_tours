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


def get_first_day_race(database_path):
    # Fetch the race dates
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        query = """
SELECT MIN(formatted_date) AS first_day_race, tour_year
FROM (
    SELECT substr(datetime(
        substr(DATE, -4) || '-' ||
        CASE substr(DATE, 1, 3)
            WHEN 'Jan' THEN '01'
            WHEN 'Feb' THEN '02'
            WHEN 'Mar' THEN '03'
            WHEN 'Apr' THEN '04'
            WHEN 'May' THEN '05'
            WHEN 'Jun' THEN '06'
            WHEN 'Jul' THEN '07'
            WHEN 'Aug' THEN '08'
            WHEN 'Sep' THEN '09'
            WHEN 'Oct' THEN '10'
            WHEN 'Nov' THEN '11'
            WHEN 'Dec' THEN '12'
        END || '-' ||
        CASE
            WHEN CAST(TRIM(substr(DATE, 5, INSTR(substr(DATE, 5), ' ')-1)) AS INTEGER) < 10
                THEN '0' || TRIM(substr(DATE, 5, INSTR(substr(DATE, 5), ' ')-1))
            ELSE TRIM(substr(DATE, 5, INSTR(substr(DATE, 5), ' ')-1))
        END
    ), 1, 10) AS formatted_date, tour_year
    FROM strava_table AS t1
)
GROUP BY tour_year;
        """
        cursor = conn.cursor()
        # Fetch rider name
        date_list = cursor.execute(query).fetchall()
    return date_list


def get_rider(athlete_id, tour, year, grand_tours_db_path, training_db_path, training=True):
    # Fetch rider name
    with sqlite3.connect(grand_tours_db_path) as conn:
        cursor = conn.cursor()
        # Fetch rider name
        cursor.execute("SELECT name FROM strava_names WHERE athlete_id = ?", (athlete_id,))
        rider_row = cursor.fetchone()
        if not rider_row:
            return None  # Rider not found

        rider_name = rider_row[0]

    race_day_list_full = get_first_day_race(grand_tours_db_path)
    race_day_list = [i[1] for i in race_day_list_full]

    # Fetch rides
    if training:
        with sqlite3.connect(training_db_path) as conn:
            cursor = conn.cursor()
            rides_query = "SELECT * FROM training_table WHERE athlete_id=? AND tour_year=?"
            # Execute with a tuple for values
            ride_rows = cursor.execute(rides_query, (athlete_id, tour + "_training" + str(-year))).fetchall()
    else:
        with sqlite3.connect(grand_tours_db_path) as conn:
            cursor = conn.cursor()
            rides_query = "SELECT * FROM strava_table WHERE athlete_id=?"
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
            race_start_day=race_day_list_full[race_day_list.index(row[2].split("_")[0] + row[2][12:])][0],
        )
        for row in ride_rows
    ]
    rider = Rider(strava_id=athlete_id, name=rider_name, rides=rides)

    return rider
