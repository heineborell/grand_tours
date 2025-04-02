from pathlib import Path

import pandas as pd
from rich import print
from sklearn.model_selection import train_test_split

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders
from training.gridsearch import json_writer, param_search

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/config_vam.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    years = [2021, 2022, 2023, 2024]
    data_list = []

    for year in years:
        # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
        config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

        # Load data
        data = load_data(tour, year, db_path=DB_PATH, training=True, segment_data=False)
        print(f"The total number of riders in the race dataset is {len(fetch_riders(DB_PATH, tour, year))}.")
        data_list.append(data)

    data = pd.concat(data_list)
    print(data)
    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    tour = "tdf"
    year = 2024
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    params = param_search(X_train=X_train, config_path=config_path)
    json_writer(config_path, params)
