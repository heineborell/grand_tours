from pathlib import Path

from rich import print
from sklearn.model_selection import train_test_split

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders
from training.gridsearch import json_writer, param_search

if __name__ == "__main__":
    db_path = Path("config/db_path.json")
    tour = "tdf"
    year = 2021

    config_path = Path(config_loader(tour, year, "config/config.json"))

    # # Load data
    data = load_data(tour, year, db_path, training=True).dropna(subset=["avg_power"])

    print(f"The total number of riders in the race dataset is {len(fetch_riders(db_path, tour, year))}.")

    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    params = param_search(X_train=X_train, config_path=config_path)
    json_writer(config_path, params)
