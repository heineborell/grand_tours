from data.database import fetch_rides

DB_PATH = "/Users/deniz/iCloud/Research/Data_Science/Projects/data/training.db"
activities = fetch_rides(DB_PATH=DB_PATH)
