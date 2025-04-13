import json
from pathlib import Path

from rich import print
from sklearn.model_selection import KFold, train_test_split
from xgboost import training

from data.data_loader import config_loader
from data.database import get_rider
from data.processing import create_features, fetch_riders
from training.gridsearch import json_writer, param_search
from training.kfold import kfold_split_train

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config_segments.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour and set if it is training or race, here we merged all years together
    tour = "tdf"
    training = True
    years = [2024]

    # Open base config and prepare it for parameter search by entering the tour and years you selected
    config_path = Path(config_loader(tour, years, config_path=CONFIG_PATH))

    # Get rider list
    rider_list = fetch_riders(DB_PATH, tour, years[0])

    # for id in list(rider_list):
    #     rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
    #     if rider:  # Ensure rider is not None
    #         if rider.to_segment_df() is not None:
    #             print(f"rider id:{id}", len(rider.to_segment_df()))
    rider_id = 7310716
    rider = get_rider(rider_id, tour, years[0], DB_PATH, training=True, segment_data=True)
    data = rider.to_segment_df()
    print(data[["distance", "vertical", "grade", "time"]].isnull().sum())
    create_features(data, training=True)
    # data = data.head(10)

    # # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    params = param_search(X_train=X_train, config_path=config_path)
    train_config_path = json_writer(config_path, params, rider_id)
    print(train_config_path)

    with open(train_config_path, "r") as f:
        train_config = json.loads(f.read())

    kfold = KFold(n_splits=5, shuffle=True, random_state=31)
    print(train_config)
    print(train_config[0]["strava_id"])

    kfold_split_train(X_train=X_train, config=train_config[0], kfold=kfold)
