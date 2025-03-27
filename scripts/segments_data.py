from pathlib import Path

from rich import print

from data.database import get_rider

if __name__ == "__main__":
    # set database paths (where you put your database files)
    db_path = Path("config/db_path.json")
    # choose tour and year
    tour = "tdf"
    year = 2023

    # Load data
    # data = load_data(tour, year, db_path, training=False, segment_data=True)
    # print(data)
    print(get_rider(18340568, tour, year, db_path, training=True, segment_data=True))
