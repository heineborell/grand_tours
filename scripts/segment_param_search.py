from pathlib import Path

from rich import print
from sklearn.model_selection import train_test_split
from xgboost import training

from data.data_loader import config_loader
from data.database import get_rider
from data.processing import create_features, fetch_riders
from training.gridsearch import json_writer, param_search

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config_segments.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour and set if it is training or race, here we merged all years together
    tour = "tdf"
    training = True
    years = [2022]

    # Open base config and prepare it for parameter search by entering the tour and years you selected
    config_path = Path(config_loader(tour, years, config_path=CONFIG_PATH))

    # Get rider list
    rider_list = fetch_riders(DB_PATH, tour, years[0])
    total_riders = len(rider_list)
    print(f"The number of riders is {total_riders}.")

    for year in years:
        for i, id in enumerate(list(rider_list)):
            try:
                rider = get_rider(id, tour, year, DB_PATH, training=True, segment_data=True)
                if rider:  # Ensure rider is not None
                    if rider.to_segment_df() is not None:
                        print(
                            f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                            f"Number of segments {len(rider.to_segment_df())}.",
                        )
                        data = rider.to_segment_df()
                        print(data[["distance", "vertical", "grade", "time"]].isnull().sum())
                        print(data["tour_year"].unique())
                        create_features(data, training=True)

                        # # Splitting train and test
                        X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

                        params = param_search(X_train=X_train, config_path=config_path)
                        json_writer(config_path, params, id)
                    else:
                        print(f"[bold pink] The rider {id} has no training rides. [/bold pink]")
            except Exception as e:
                print(f"Error processing rider {id}: {e}")
