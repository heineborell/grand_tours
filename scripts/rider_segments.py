import json
from pathlib import Path

from rich import print
from sklearn.model_selection import KFold, train_test_split

from data.data_loader import config_loader
from data.database import get_rider
from data.processing import fetch_riders
from training.kfold import kfold_split_train

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/config_segments.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    year = 2024

    # Gets the configuration json file needed for training models, hyperparameters. Check /config/config.json file.
    config_path = Path(config_loader(tour, year, config_path=CONFIG_PATH))

    # Get rider list
    rider_list = fetch_riders(DB_PATH, tour, year)

    # for id in list(rider_list):
    #     rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
    #     if rider:  # Ensure rider is not None
    #         if rider.to_segment_df() is not None:
    #             print(f"rider id:{id}", len(rider.to_segment_df()))
    rider = get_rider(1905161, tour, year, DB_PATH, training=True, segment_data=True)
    data = rider.to_segment_df()
    print(data[["distance", "vertical", "grade", "time"]].isnull().sum())

    # # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    # params = param_search(X_train=X_train, config_path=config_path)
    # json_writer(config_path, params)

    with open(config_path, "r") as f:
        config = json.loads(f.read())

    kfold = KFold(n_splits=5, shuffle=True, random_state=31)

    kfold_split_train(X_train, config, kfold)
