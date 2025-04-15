import json
from pathlib import Path

from rich import print as print

from data.processing import create_features, get_rider
from data.segment_analyse import segment_analyser, stage_list_getter

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    years = [2023]

    for year in years:
        stage_list = stage_list_getter(db_path=DB_PATH, tour=tour, year=year)
        for stage in stage_list:
            segment_df = segment_analyser(DB_PATH, stage, tour, year)
            print(segment_df)

    for year in years:
        with open(PROJECT_ROOT / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        for i, id in enumerate(list(rider_list)):
            rider = get_rider(id, tour, year, DB_PATH, training=False, segment_data=True)
            if rider:  # Ensure rider is not None
                if rider.to_segment_df() is not None:
                    print(
                        f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                        f"Number of segments {len(rider.to_segment_df())}.",
                    )
                    data = rider.to_segment_df()
                    data = create_features(data, training=False)
                    # print(data)
