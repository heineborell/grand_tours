import json
from pathlib import Path

import pandas as pd
from rich import print as print

from data.processing import create_features, get_rider
from data.segment_analyse import get_segment_table, merged_tables
from training.kfold import segment_tester

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour and set if it is training or race, here we merged all years together
    tour = "tdf"
    training = True
    years = [2023]

    # get the non-overlapping segment table of all riders given a tour
    segment_df_full = get_segment_table(tour, years, DB_PATH)
    merged_df = merged_tables(tour, years, segment_df_full, PROJECT_ROOT, DB_PATH)

    all_dfs = []  # List to collect all resulting DataFrames
    for year in years:
        with open(PROJECT_ROOT / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        for i, id in enumerate(list(rider_list)):
            try:
                # getting training rides of a given rider
                rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
                if rider:  # Ensure rider is not None
                    if rider.to_segment_df() is not None:
                        print(f"rider id:{id}. Rider {i}/{len(rider_list)}.")
                        # training rides and race data of a rider
                        data = rider.to_segment_df()
                        training_data = create_features(data, training=True)
                        training_data["speed"] = training_data["total_distance"] * 1000 / training_data["total_time"]
                        training_data = training_data.loc[training_data["speed"] > 10.5].reset_index(drop=True)
                        race_data = merged_df.loc[merged_df["strava_id"] == id]

                        # get the best params of a given rider
                        config = next((item for item in train_config if item["strava_id"] == id), None)

                        # Finally train-test
                        # Note that model training data only consists of training rides and
                        # test data consists of race data
                        X_train = training_data
                        X_test = race_data.dropna(subset=["distance"])

                        df = segment_tester(X_train, X_test, config)
                        print(df)
                        all_dfs.append(df)

            except Exception as e:
                print(f"Error processing rider {id}: {e}")  # Concatenate and save all results

    if all_dfs:
        result_df = pd.concat(all_dfs, ignore_index=True)
        result_df.to_csv(PROJECT_ROOT / f"results/segment_test_results_{tour}_{years[0]}.csv", index=False)
