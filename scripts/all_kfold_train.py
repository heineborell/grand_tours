import json
from pathlib import Path

from rich import print as print
from sklearn.model_selection import KFold, train_test_split

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders
from training.kfold import kfold_split_train

if __name__ == "__main__":
    db_path = Path("config/db_path.json")
    tour = "tdf"
    year = 2024

    config_path = Path(config_loader(tour, year, "config/config.json"))

    # # Load data
    data = load_data(tour, year, db_path, training=True, segment_data=False).dropna(subset="avg_power")
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(db_path, tour, year))}.")

    config_train = Path(f"config/config_{tour}_training-{year}_all_power.json")
    with open(config_train, "r") as f:
        config = json.loads(f.read())

    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    kfold = KFold(n_splits=5, shuffle=True, random_state=31)
    kfold_split_train(X_train, config, kfold)
