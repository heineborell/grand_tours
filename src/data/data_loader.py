import json
import os

from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, training=True):
    # Load config
    with open("config/config.json", "r") as f:
        config = json.loads(f.read())

    grand_tours_db_path = os.path.expanduser(config["global"]["grand_tours_db_path"])
    training_db_path = os.path.expanduser(config["global"]["training_db_path"])

    rider_list = fetch_riders(grand_tours_db_path, tour, year)
    full_df = create_dataframe(rider_list, tour, year, grand_tours_db_path, training_db_path, training)
    cleaned_df = clean_dataframe(full_df)

    return create_features(cleaned_df, training).reset_index(drop=True)
