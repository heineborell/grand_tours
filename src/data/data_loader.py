from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, db_path, training=True):
    rider_list = fetch_riders(db_path, tour, year)
    full_df = create_dataframe(rider_list, tour, year, db_path, training)
    cleaned_df = clean_dataframe(full_df)

    return create_features(cleaned_df, training).reset_index(drop=True)
