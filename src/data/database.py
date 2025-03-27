import json
import os
import sqlite3
from datetime import datetime
from typing import Optional

from data.schemas import Ride, Rider, Segment


def hms_to_seconds(hms: dict[int, str]) -> Optional[int]:
    """Takes the time in formats H:M:S, M:S, S to seconds"""
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
    """Returns the first day of the races."""

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


def get_rider(athlete_id, tour, year, db_path, training=True, segment_data=False):
    """Create Pydantic Rider object given athlete_id, tour, year, db_path."""

    # Load database path config
    with open(db_path, "r") as f:
        db_path = json.loads(f.read())

    # set paths for both of databases grand_tours and training
    grand_tours_db_path = os.path.expanduser(db_path["global"]["grand_tours_db_path"])
    training_db_path = os.path.expanduser(db_path["global"]["training_db_path"])

    # Fetch rider name given athlete_id from sql query
    with sqlite3.connect(grand_tours_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM strava_names WHERE athlete_id = ?", (athlete_id,))
        rider_row = cursor.fetchone()
        if not rider_row:
            return None  # Rider not found

        rider_name = rider_row[0]

    # Fetch rides, if its training fetch it from training db if its race fetch it from grand_tours
    if training:
        with sqlite3.connect(training_db_path) as conn:
            cursor = conn.cursor()
            rides_query = "SELECT * FROM training_table WHERE athlete_id=? AND tour_year=?"
            # Execute with a tuple for values
            ride_rows = cursor.execute(rides_query, (athlete_id, tour + "_training" + str(-year))).fetchall()
    else:
        with sqlite3.connect(grand_tours_db_path) as conn:
            cursor = conn.cursor()
            rides_query = "SELECT * FROM strava_table WHERE athlete_id=? AND tour_year=?"
            # Execute with a tuple for values
            ride_rows = cursor.execute(rides_query, (athlete_id, tour + str(-year))).fetchall()

    race_day_list_full, race_day_list = get_race_day(grand_tours_db_path)
    drop_list = []
    if segment_data:
        [check_segment(row, drop_list, training) for row in ride_rows]

    # Convert SQL rows to Pydantic models
    ride_rows = [row for row in ride_rows if row[0] not in drop_list]
    rides = [create_ride(row, training, race_day_list_full, race_day_list, segment_data) for row in ride_rows]
    rider = Rider(strava_id=athlete_id, name=rider_name, rides=rides)

    return rider


def get_race_day(grand_tours_db_path):
    # get the first day for all races
    race_day_list_full = get_first_day_race(grand_tours_db_path)
    race_day_list = [i[1] for i in race_day_list_full]
    return race_day_list_full, race_day_list


def check_segment(row, drop_list, training):
    try:
        ([Segment(name=segments) for segments in json.loads(row[5 if training else 7]).get("segment_name")],)
    except TypeError:
        drop_list.append(row[0])


def create_ride(row, training, race_day_list_full, race_day_list, segment_data):
    ride_data = json.loads(row[4 if training else -1])
    segment_name_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_name")]
    # segment_time_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_time")]
    segments = []
    if segment_data:
        for seg in segment_name_list:
            segments.append(Segment(name=seg))
    return Ride(
        activity_id=row[0],
        distance=ride_data["dist"].split(" ")[0],
        time=hms_to_seconds(ride_data),
        elevation=get_elevation(ride_data),
        avg_power=safe_get_wap(ride_data),
        tour_year=row[2],
        ride_date=mdy_to_ymd(row[3 if training else 5]),
        race_start_day=race_day_list_full[race_day_list.index(row[2].split("_")[0] + row[2][12:])][0],
        **({"stage": row[6].strip()} if not training else {}),
        segments=segments,
    )
