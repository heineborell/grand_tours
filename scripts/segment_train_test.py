import json
from pathlib import Path

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
    years = [2024]

    segment_df_full = get_segment_table(tour, years, DB_PATH)
    merged_df = merged_tables(tour, years, segment_df_full, PROJECT_ROOT, DB_PATH)

    for year in years:
        with open(PROJECT_ROOT / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        for i, id in enumerate(list(rider_list)[0:1]):
            try:
                rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
                if rider:  # Ensure rider is not None
                    if rider.to_segment_df() is not None:
                        print(
                            f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                            f"Number of segments {len(rider.to_segment_df())}.",
                        )
                        data = rider.to_segment_df()
                        training_data = create_features(data, training=True)
                        race_data = merged_df.loc[merged_df["strava_id"] == id]

                        config = next((item for item in train_config if item["strava_id"] == id), None)

                        # Finally train-test
                        X_train = training_data
                        X_test = race_data.dropna(subset=["distance"])

                        segment_tester(X_train, X_test, config)
            except Exception as e:
                print(f"Error processing rider {id}: {e}")
