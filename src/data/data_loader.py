import json

from data.processing import clean_dataframe, create_dataframe, create_features, fetch_riders


def load_data(tour, year, db_path, training=True, segment_data=False):
    """Loads pandas dataframe given tour, year, database path"""
    # first fetch the riders given tour and year
    rider_list = fetch_riders(db_path, tour, year)

    # create pandas dataframe given the riders, tour, year and if its training or not.
    # training true will give race datas for the tour and year.
    full_df = create_dataframe(rider_list, tour, year, db_path, training, segment_data)

    # cleaning dataframe (this one takes out the activities that have distance=elevation=0)
    # which are rides on stationary trainers
    cleaned_df = clean_dataframe(full_df)

    # finally this creates a feature called timedelta which is how many days is the ride is away
    # from first stage of the race
    return create_features(cleaned_df, training).reset_index(drop=True)


def get_data_info(data):
    """Creates a table for activity count for each rider"""
    print(f"The total number of riders in dataset is {len(data['strava_id'].unique())}.")

    no_of_activities = (
        data.groupby("strava_id")
        .size()
        .sort_values(ascending=True)
        .reset_index(name="activity_count")
        .sort_values("activity_count", ascending=True)
    )
    return no_of_activities


def config_loader(tour, year, config_path):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    config["tour"] = tour
    config["year"] = year

    json_data = json.dumps(config, indent=4)
    with open(
        config_path,
        "w",
    ) as f:
        f.write(json_data)

    return config_path
