from pathlib import Path

from rich import print as print

from data.segment_analyse import get_segment_table, merged_tables

if __name__ == "__main__":
    # Get the absolute path of the project root dynamically
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust if needed
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    # Enter tour, year of your choice
    tour = "tdf"
    years = [2024]

    segment_df_full = get_segment_table(tour, years, DB_PATH)
    merged_df = merged_tables(tour, years, segment_df_full, PROJECT_ROOT, DB_PATH)

    print(segment_df_full)
    print(merged_df)
