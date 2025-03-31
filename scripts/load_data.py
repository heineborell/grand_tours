from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders

if __name__ == "__main__":
    db_path = Path("config/db_path.json")
    tour = "giro"
    year = 2022

    config_path = Path(config_loader(tour, year, "config/config.json"))

    # # Load data
    data = load_data(tour, year, db_path, training=True, segment_data=True)
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(db_path, tour, year))}.")
