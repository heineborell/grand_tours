import subprocess
from getpass import getuser

from data.database import get_rider
from data.processing import create_training_dataframe, fetch_riders

username = getuser()
DB_PATH_1 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/training_merged.db"
DB_PATH_2 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/grand_tours.db"


rider = get_rider(athlete_id=189040, table_name="training_table", NAME_DB_PATH=DB_PATH_2, ACTIVITY_DB_PATH=DB_PATH_1)

# print(rider.model_dump())
# print(rider.to_dataframe())
# subprocess.run(["vd", "-f", "csv", "-"], input=rider.to_dataframe().to_csv(index=False), text=True)
# print(rider.to_dataframe())

# print(fetch_riders(DB_PATH_2, "tdf", 2024))

# for no in fetch_riders(DB_PATH_2, "tdf", 2024):
#     rider = get_rider(athlete_id=no, table_name="training_table", NAME_DB_PATH=DB_PATH_2, ACTIVITY_DB_PATH=DB_PATH_1)
#     print(rider)

full_df = create_training_dataframe(fetch_riders(DB_PATH_2, "tdf", 2024), "training_table", DB_PATH_2, DB_PATH_1)
subprocess.run(["vd", "-f", "csv", "-"], input=full_df.to_csv(index=False), text=True)
