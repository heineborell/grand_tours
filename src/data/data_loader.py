import yaml

from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, training=True):
    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    rider_list = fetch_riders(config["grand_tours_db_path"], tour, year)
    full_df = create_dataframe(
        rider_list, tour, year, config["grand_tours_db_path"], config["training_db_path"], training
    )
    cleaned_df = clean_dataframe(full_df)

    return create_features(cleaned_df, training)
