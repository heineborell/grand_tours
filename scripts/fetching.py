import subprocess
from getpass import getuser

from data.processing import create_training_dataframe, fetch_riders

username = getuser()
DB_PATH_1 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/training_merged.db"
DB_PATH_2 = f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/grand_tours.db"


# rider = get_rider(
#     athlete_id=189040, tour="tdf", year=2023, grand_tours_db_path=DB_PATH_2,
# training_db_path=DB_PATH_1, training=False
# )
# print(rider.model_dump())
# print(rider.to_dataframe())

full_df = create_training_dataframe(
    fetch_riders(DB_PATH_2, "tdf", 2024), "tdf", 2024, DB_PATH_2, DB_PATH_1, training=True
)
# train_model(189040, full_df)
subprocess.run(["vd", "-f", "csv", "-"], input=full_df.to_csv(index=False), text=True)
