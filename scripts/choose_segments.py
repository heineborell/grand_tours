from pathlib import Path

from rich import print as print

from data.segment_analyse import segment_analyser, stage_list_getter

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    year = 2023

    the_stage = stage_list_getter(db_path=DB_PATH, tour=tour, year=year)[4]
    df = segment_analyser(DB_PATH, the_stage, tour, year)
    print(df)
