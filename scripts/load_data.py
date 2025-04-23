from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.database import download_database
from data.processing import fetch_riders

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Google Drive URL
    urls = [
        "https://drive.google.com/file/d/1QWc76dIf-lVVbbs4QpDoQwIRvUwFkvZP/view?usp=share_link",
        "https://drive.google.com/file/d/1ZWI6orj1HrjZ-MH_vKddJyXIpLPwyIcl/view?usp=share_link",
    ]
    download_database(urls=urls, filenames=["segment_details_v2.db", "grand_tours.db"])

    # Enter tour, year of your choice
    tour = "giro"
    year = 2023

    # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    # Load data
    data = load_data(tour, year, db_path=DB_PATH, training=False, segment_data=False)
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(DB_PATH, tour, year))}.")
