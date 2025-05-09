import json
from pathlib import Path

import pandas as pd
from rich import print as print
from sklearn.model_selection import KFold, train_test_split

from data.processing import create_features, get_rider
from training.kfold import kfold_split_train

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour and set if it is training or race, here we merged all years together
    tour = "giro"
    training = True
    years = [2024]

    all_dfs = []  # List to collect all resulting DataFrames
    for year in years:
        with open(PROJECT_ROOT / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        for i, id in enumerate(list(rider_list)):
            try:
                rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
                if rider:  # Ensure rider is not None
                    if rider.to_segment_df() is not None:
                        data = rider.to_segment_df()
                        data = create_features(data, training=True)
                        print(data)
                        data["speed"] = data["total_distance"] * 1000 / data["total_time"]
                        data = data.loc[data["speed"] > 10.5].reset_index(drop=True)
                        print(
                            f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                            f"Number of segments {len(data)}.",
                        )

                        # Splitting train and test
                        X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)
                        config = next((item for item in train_config if item["strava_id"] == id), None)

                        kfold = KFold(n_splits=5, shuffle=True, random_state=31)
                        df = kfold_split_train(X_train, config, kfold)
                        print(df)
                        all_dfs.append(df)
            except Exception as e:
                print(f"Error processing rider {id}: {e}")

    if all_dfs:
        result_df = pd.concat(all_dfs, ignore_index=True)
        result_df.to_csv(
            PROJECT_ROOT / f"notebooks/model_2/model_results/segment_cv_results_{tour}_{years[0]}.csv", index=False
        )
