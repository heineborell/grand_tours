from pathlib import Path

from rich import print

from data.data_loader import config_loader
from data.database import get_rider
from data.processing import fetch_riders

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    year = 2022

    # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    # Get rider list
    rider_list = fetch_riders(DB_PATH, tour, year)

    for rider in list(rider_list)[-3:-1]:
        print(get_rider(rider, tour, year, DB_PATH, training=True, segment_data=True).to_segment_df())
