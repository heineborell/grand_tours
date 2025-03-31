from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    year = 2023

    # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    # Load data
    data = load_data(tour, year, db_path=DB_PATH, training=True, segment_data=False)
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(DB_PATH, tour, year))}.")
