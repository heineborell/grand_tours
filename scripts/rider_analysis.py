from pathlib import Path

from rich import print
from sklearn.model_selection import KFold, train_test_split

from data.data_loader import get_data_info, load_data
from data.processing import fetch_riders
from training.gridsearch import param_search
from training.kfold import kfold_split_train

if __name__ == "__main__":
    config_path = Path("config/config_noxgb.json")
    db_path = Path("config/db_path.json")
    tour = "tdf"
    year = 2024

    # # Load data
    data = load_data(tour, year, db_path, training=True).dropna(subset=["avg_power"])

    print(f"The total number of riders in the race dataset is {len(fetch_riders(db_path, tour, year))}.")

    sorted_list = get_data_info(data)

    for rider in list(sorted_list["strava_id"])[-15:-1]:
        rider_data = data.loc[data["strava_id"] == rider]

        # Splitting train and test
        X_train, X_test = train_test_split(rider_data, test_size=0.2, random_state=42)

        param_search(X_train, config_path)
        kfold = KFold(n_splits=5, shuffle=True, random_state=31)
        kfold_split_train(X_train, config_path, kfold)
