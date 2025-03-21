import os

import yaml

from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, training=True):
    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    grand_tours_db_path = os.path.expanduser(config["grand_tours_db_path"])
    training_db_path = os.path.expanduser(config["training_db_path"])

    rider_list = fetch_riders(grand_tours_db_path, tour, year)
    full_df = create_dataframe(rider_list, tour, year, grand_tours_db_path, training_db_path, training)
    cleaned_df = clean_dataframe(full_df)

    return create_features(cleaned_df, training)
