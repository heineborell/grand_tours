"""
This script automates the setup process for the cycling grand tour data analysis project.

It performs the following steps:
1. Downloads the required database files from Google Drive.
2. Sets up local file paths for accessing the downloaded data.
3. Loads a sample tour and year from the database to verify successful setup.

This script ensures that the necessary data is available and correctly configured for further analysis or development.
"""

from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.database import download_database, set_db_path
from data.processing import fetch_riders

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Google Drive URL
    urls = [
        "https://drive.google.com/file/d/1ZWI6orj1HrjZ-MH_vKddJyXIpLPwyIcl/view?usp=share_link",
        "https://drive.google.com/file/d/101u1n86zCi37PbEHtu5rqwWrcvh1TNXs/view?usp=share_link",
        "https://drive.google.com/file/d/1_lGxibgY0sLqoq9-BvKeNuXlOBmmwSKh/view?usp=share_link",
    ]
    download_database(urls=urls, filenames=["grand_tours.db", "training_merged_v2.db", "segment_details_v3.db"])
    set_db_path()

    # Enter tour, year of your choice
    tour = "giro"
    year = 2023

    # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    # Load data
    data = load_data(tour, year, db_path=DB_PATH, training=False, segment_data=False)
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(DB_PATH, tour, year))}.")
