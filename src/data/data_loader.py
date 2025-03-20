import yaml

from data.processing import create_features, create_training_dataframe, fetch_riders


def load_data(tour, year, training=True):
    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    rider_list = fetch_riders(config["grand_tours_db_path"], tour, year)
    full_df = create_training_dataframe(
        rider_list, tour, year, config["grand_tours_db_path"], config["training_db_path"], training
    )

    return create_features(full_df, training)
