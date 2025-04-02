import json
from pathlib import Path

import pandas as pd
from rich import print as print
from sklearn.model_selection import KFold, train_test_split

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders
from training.kfold import kfold_split_train

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

    year = 2024
    config_train = Path(f"config/config_{tour}_training-{year}_all.json")
    with open(config_train, "r") as f:
        config = json.loads(f.read())

    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    kfold = KFold(n_splits=5, shuffle=True, random_state=31)
    kfold_split_train(X_train, config, kfold)
