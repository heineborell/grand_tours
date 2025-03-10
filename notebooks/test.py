import ast
import getpass
import sqlite3

import pandas as pd

import segment_analyse

if __name__ == "__main__":
    username = getpass.getuser()

    # # grand_tour = "tdf"
    # grand_tour = "giro"
    # year = 2022

    conn = sqlite3.connect(f"/Users/{username}/iCloud/Research/Data_Science/Projects/data/segment_details.db")

    # query_date = (
    #     f"SELECT DISTINCT x.week, x.year "
    #     f"FROM ( "
    #     f"    SELECT `year`, strftime('%W', `date`) AS week "
    #     f"    FROM {grand_tour}_results "
    #     f") AS x"
    # )
    #
    # query_id = f" SELECT DISTINCT(athlete_id) FROM strava_table where tour_year = '{grand_tour}-{year}'"

    query_all = "SELECT * FROM segment_details_data WHERE tour_year = 'tdf-2024' AND stage='Stage 4 '"

    # diff_no = [set([i["activity_no"] for i in ordered_list])]
    # ordered_list = [k for k in ordered_list if k["activity_no"] == "11768746162" and not k["hidden"]]
    # ordered_list = [i for i in ordered_list if i["end_points"][1] - i["end_points"][0] < 868 * 0.1]
    #

    df = pd.read_sql_query(query_all, conn)
    segment_list = [ast.literal_eval(k) for k in df["end_points"]]
    print(segment_list)

    segment_analyse.segment_picker(segment_list)
