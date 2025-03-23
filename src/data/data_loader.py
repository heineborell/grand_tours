import json
import os

from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, db_path, training=True):
    # Load config
    with open(db_path, "r") as f:
        db_path = json.loads(f.read())

    grand_tours_db_path = os.path.expanduser(db_path["global"]["grand_tours_db_path"])
    training_db_path = os.path.expanduser(db_path["global"]["training_db_path"])

    rider_list = fetch_riders(grand_tours_db_path, tour, year)
    full_df = create_dataframe(rider_list, tour, year, grand_tours_db_path, training_db_path, training)
    cleaned_df = clean_dataframe(full_df)

    return create_features(cleaned_df, training).reset_index(drop=True)
