from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders

if __name__ == "__main__":
    db_path = Path("config/db_path.json")
    tour = "tdf"
    year = 2024

    config_path = Path(config_loader(tour, year, "config/config.json"))

    # # Load data
    data = load_data(tour, year, db_path, training=True, segment_data=False)
    print(data)

    print(f"The total number of riders in the race dataset is {len(fetch_riders(db_path, tour, year))}.")

    # sorted_list = get_data_info(data)
    #
    # config_train = Path(f"config/config_{tour}_training-{year}_individual.json")
    # with open(config_train, "r") as f:
    #     config_list = json.loads(f.read())
    #
    # for rider in list(sorted_list["strava_id"])[-20:-1]:
    #     rider_data = data.loc[data["strava_id"] == rider]
    #     print(rider)
    #
    #     # Splitting train and test
    #     X_train, X_test = train_test_split(rider_data, test_size=0.2, random_state=42)
    #
    #     config_rider = [r for r in config_list if r.get("strava_id") == rider]
    #     kfold = KFold(n_splits=5, shuffle=True, random_state=31)
    #     kfold_split_train(X_train, config_rider[0], kfold)
