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
    CONFIG_PATH = PROJECT_ROOT / "config/base_config_vam.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour and set if it is training or race, here we merged all years together
    tour = "tdf"
    training = True
    years = [2021, 2022, 2023, 2024]
    data_list = []

    # Open base config and prepare it for parameter search by entering the tour and years you selected
    config_path = Path(config_loader(tour, years, config_path=CONFIG_PATH))

    for year in years:
        # Load data
        data = load_data(tour, year, db_path=DB_PATH, training=training, segment_data=False)
        print(f"The total number of riders in the race dataset is {len(fetch_riders(DB_PATH, tour, year))}.")
        data_list.append(data)

    data = pd.concat(data_list)
    print(data)
    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    params = param_search(X_train=X_train, config_path=CONFIG_PATH)
    json_writer(CONFIG_PATH, params)
