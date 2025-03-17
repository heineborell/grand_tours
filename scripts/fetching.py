from data.database import get_rider

DB_PATH_1 = "/Users/deniz/iCloud/Research/Data_Science/Projects/data/training_merged.db"
DB_PATH_2 = "/Users/deniz/iCloud/Research/Data_Science/Projects/data/grand_tours.db"

# activities = fetch_rides(db_path_activity=DB_PATH_1, db_path_name=DB_PATH_2)

rider = get_rider(10045754, "training_table", DB_PATH_2, DB_PATH_1)
# print(rider.model_dump())
for ride in rider.rides:
    print(ride.avg_power)
