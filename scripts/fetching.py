from getpass import getuser

from data.database import get_rider
from data.processing import fetch_riders

username = getuser()
DB_PATH_1 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/training_merged.db"
DB_PATH_2 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/grand_tours.db"

# activities = fetch_rides(db_path_activity=DB_PATH_1, db_path_name=DB_PATH_2)

rider = get_rider(athlete_id=189040, table_name="training_table", NAME_DB_PATH=DB_PATH_2, ACTIVITY_DB_PATH=DB_PATH_1)

print(rider.to_dataframe())

print(fetch_riders(DB_PATH_2, "tdf", 2024))

for no in fetch_riders(DB_PATH_2, "tdf", 2024):
    rider = get_rider(athlete_id=no, table_name="training_table", NAME_DB_PATH=DB_PATH_2, ACTIVITY_DB_PATH=DB_PATH_1)
    print(rider)
