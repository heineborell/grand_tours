import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import gdown
from rich import print as print

from data.schemas import Ride, Rider, Segment


def hms_to_seconds(hms_value):
    """Takes the time in formats H:M:S, M:S, S to seconds"""
    try:
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
        if "," not in row_json["wap"]:  # some wap's have , seperating them and we filter them out here
            return row_json["wap"].split(" ")[0]  # Extract value safely
    except (KeyError, AttributeError):
        return None  # Return None if key is missing


def mdy_to_ymd(d):
    try:
        date = datetime.strptime(d, "%b %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        date = datetime.strptime(d, "%B %d %Y").strftime("%Y-%m-%d")
    return date


def remove_km(value):
    if not value.endswith("km"):
        raise ValueError(f"Invalid value: {value} (does not end with 'km')")
    return value[:-2]  # Remove last two characters


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
    rides = [
        ride
        for row in ride_rows
        if (ride := create_ride(row, training, race_day_list_full, race_day_list, segment_data)) is not None
    ]
    rider = Rider(strava_id=athlete_id, name=rider_name, rides=rides)

    return rider


def get_rider_config(path, strava_id):
    with open(path, "r") as f:
        config = json.loads(f.read())

    return next((d for d in config if d.get("strava_id") == strava_id), None)


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
    if segment_data:
        segment_name_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_name")]
        segment_dist_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_distance")]
        segment_time_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_time")]
        segment_vert_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_vert")]
        segment_grade_list = [segments for segments in json.loads(row[5 if training else 7]).get("segment_grade")]
        segment_watt_list = [segments for segments in json.loads(row[5 if training else 7]).get("watt")]
        segment_hr_list = [segments for segments in json.loads(row[5 if training else 7]).get("heart_rate")]
        segments = []
        for seg_name, seg_dist, seg_time, seg_vert, seg_grade, seg_watt, seg_hr in zip(
            segment_name_list,
            segment_dist_list,
            segment_time_list,
            segment_vert_list,
            segment_grade_list,
            segment_watt_list,
            segment_hr_list,
        ):
            try:
                dist = remove_km(seg_dist)
            except (KeyError, ValueError) as e:
                sys.stdout.write(f"Error in segment_dist: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                continue
            try:
                time = hms_to_seconds(seg_time)
            except (KeyError, ValueError) as e:
                sys.stdout.write(f"Error in segment_time: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                continue
            try:
                vert = int(seg_vert[:-1].replace(",", ""))
            except (KeyError, ValueError) as e:
                sys.stdout.write(f"Error in segment_vert: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                continue
            try:
                grade = float(seg_grade[:-1])
            except (KeyError, ValueError) as e:
                sys.stdout.write(f"Error in segment_grade: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                continue
            try:
                if seg_watt != "—":
                    watt = int(seg_watt[:-1])
                else:
                    watt = None
            except (KeyError, ValueError) as e:
                sys.stdout.write(f"Error in segment_watt: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                watt = None
                continue
            try:
                if seg_hr != "—":
                    heart_rate = int(seg_hr[:-3])
                else:
                    heart_rate = None
            except ValueError as e:
                sys.stdout.write(f"Error in segment_hr: {e}\n")
                sys.stdout.flush()
                sys.stdout.write("\033[F\033[K")
                heart_rate = None
                continue
            segments.append(
                Segment(
                    name=seg_name,
                    dist=dist,
                    time=time,
                    vert=vert,
                    grade=grade,
                    watt=watt,
                    heart_rate=heart_rate,
                )
            )
    else:
        segments = []
    try:
        time = hms_to_seconds(ride_data["move_time"])
    except (KeyError, ValueError) as e:
        sys.stdout.write(f"Error in move_time: {e} in activity {row[0]}.\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    try:
        distance = float(ride_data["dist"].split(" ")[0])
    except (KeyError, ValueError) as e:
        sys.stdout.write(f"Error in distance: {e} in activity {row[0]}.\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    try:
        elevation = get_elevation(ride_data)
    except (KeyError, ValueError) as e:
        sys.stdout.write(f"Error in elevation: {e} in activity {row[0]}.\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    try:
        avg_power = safe_get_wap(ride_data)
    except (KeyError, ValueError) as e:
        sys.stdout.write(f"Error in avg_power: {e} in activity {row[0]}.\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    try:
        ride_date = mdy_to_ymd(row[3 if training else 5])
    except (KeyError, ValueError) as e:
        sys.stdout.write(f"Error in ride_date: {e} in activity {row[0]}.\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    try:
        if training:
            race_start_day = race_day_list_full[race_day_list.index(row[2].split("_")[0] + "-" + row[2][-4:])][0]
        else:
            race_start_day = race_day_list_full[race_day_list.index(row[2])][0]
    except (KeyError, ValueError, IndexError) as e:
        sys.stdout.write(f"Error in race_start_day: {e}\n")
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")
        return None
    return Ride(
        activity_id=row[0],
        distance=distance,
        time=time,
        elevation=elevation,
        avg_power=avg_power,
        tour_year=row[2],
        ride_date=ride_date,
        race_start_day=race_start_day,
        **({"stage": row[6].strip()} if not training else {}),
        segments=segments,
    )


def download_database(urls, filenames):
    """
    Downloads files from a list of Google Drive URLs into the data/ folder,
    skipping files that already exist. Filenames are provided explicitly.

    Args:
        urls (list of str): Google Drive file URLs.
        filenames (list of str): Corresponding filenames for each URL.
    """
    assert len(urls) == len(filenames), "Each URL must have a corresponding filename."

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    target_dir = PROJECT_ROOT / "data"
    target_dir.mkdir(parents=True, exist_ok=True)

    for url, filename in zip(urls, filenames):
        target_path = target_dir / filename

        if target_path.exists():
            print(f"File already exists, skipping: {filename}")
            continue

        # Download and save with the given filename
        output = gdown.download(url, output=str(target_path), quiet=False, fuzzy=True)
        if output is not None:
            print(f"Downloaded and saved: {filename}")
        else:
            print(f"Failed to download: {url}")


def set_db_path():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    config_path = PROJECT_ROOT / "config/db_path.json"
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    config["global"]["grand_tours_db_path"] = str(PROJECT_ROOT / "data/grand_tours.db")
    config["global"]["training_db_path"] = str(PROJECT_ROOT / "data/training_merged_v2.db")
    config["global"]["segment_details_db_path"] = str(PROJECT_ROOT / "data/segment_details_v3.db")

    json_data = json.dumps(config, indent=4)
    with open(
        config_path,
        "w",
    ) as f:
        f.write(json_data)
