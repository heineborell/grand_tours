from data.database import get_rider

DB_PATH_1 = "/Users/deniz/iCloud/Research/Data_Science/Projects/data/training.db"
DB_PATH_2 = "/Users/deniz/iCloud/Research/Data_Science/Projects/data/grand_tours.db"

# activities = fetch_rides(db_path_activity=DB_PATH_1, db_path_name=DB_PATH_2)

rider = get_rider(133606, "stats_data", DB_PATH_2, DB_PATH_1)
print(rider)
