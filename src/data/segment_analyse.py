"""This module is mostly written by chatgpt is has to be reviewed!"""

import ast
import json
import os
import sqlite3
from bisect import bisect_right

import pandas as pd
from rich import print

from data.database import get_rider
from data.processing import create_features


def check_overlap(segment1: list[int], segment2: list[int]) -> bool:
    """
    Check if two segments overlap
    """
    return not (segment1[1] <= segment2[0] or segment2[1] <= segment1[0])


def optimize_segments(segments: list[list[int]], prefer_longest_segments: bool = True) -> list[list[int]]:
    """
    Find the optimal non-overlapping segments that either:
    1. Maximize total distance covered (prefer_longest_segments=False)
    2. Prefer longer individual segments (prefer_longest_segments=True)
    """
    if not segments:
        return []

    if prefer_longest_segments:
        # Sort by length (descending), then by end position for tie-breaking
        sorted_segments = sorted(segments, key=lambda x: (-(x[1] - x[0]), x[1]))
        selected = []
        for segment in sorted_segments:
            is_overlapping = any(check_overlap(segment, s) for s in selected)
            if not is_overlapping:
                # Remove any segments fully contained in the new one
                selected = [s for s in selected if not (segment[0] <= s[0] and segment[1] >= s[1])]
                # Skip if it’s contained within a previously selected segment
                if not any(s[0] <= segment[0] and s[1] >= segment[1] for s in selected):
                    selected.append(segment)
        return sorted(selected, key=lambda x: x[0])

    # Weighted interval scheduling: maximize total coverage
    # Step 1: Sort segments by end
    sorted_segments = sorted(segments, key=lambda x: x[1])
    ends = [s[1] for s in sorted_segments]
    weights = [e - s for s, e in sorted_segments]
    n = len(segments)

    # Step 2: Compute p(i): last non-overlapping segment before i
    p = []
    for i in range(n):
        j = bisect_right(ends, sorted_segments[i][0]) - 1
        p.append(j)

    # Step 3: DP table to store max coverage
    dp = [0] * n
    selected_indices = [[] for _ in range(n)]

    for i in range(n):
        incl = weights[i] + (dp[p[i]] if p[i] != -1 else 0)
        excl = dp[i - 1] if i > 0 else 0

        if incl > excl:
            dp[i] = incl
            selected_indices[i] = (selected_indices[p[i]] if p[i] != -1 else []) + [i]
        else:
            dp[i] = excl
            selected_indices[i] = selected_indices[i - 1] if i > 0 else []

    return [sorted_segments[i] for i in selected_indices[-1]]


def analyze_solution(result: list[list[int]]):
    """
    Analyze and print statistics about the solution
    """
    for i, seg1 in enumerate(result):
        for seg2 in result[i + 1 :]:
            if check_overlap(seg1, seg2):
                print(f"WARNING: Overlap detected between {seg1} and {seg2}")

    total_coverage = sum(end - start for start, end in result)
    segment_lengths = [end - start for start, end in result]
    avg_segment_length = sum(segment_lengths) / len(segment_lengths) if segment_lengths else 0

    print(f"Number of segments: {len(result)}")
    print(f"Total coverage: {total_coverage} meters")
    print(f"Average segment length: {avg_segment_length:.2f} meters")
    print("Individual segments:")
    for start, end in result:
        print(f"  {start}-{end} ({end - start}m)")


def greedy_picker(segments):
    ordered_list = sorted(segments, key=lambda x: x[1])
    selected = []
    for elmt in ordered_list:
        if not selected or selected[-1][1] <= elmt[0]:
            selected.append(elmt)
    return sorted(selected, key=lambda x: x[0])


def segment_picker(segments, report=False):
    longest_segments = optimize_segments(segments, prefer_longest_segments=True)
    max_coverage = optimize_segments(segments, prefer_longest_segments=False)
    greedy = greedy_picker(segments)

    if report:
        print("\nOptimizing for longest segments:")
        analyze_solution(longest_segments)
        print("\nOptimizing for maximum coverage:")
        analyze_solution(max_coverage)
        print("\nOptimizing using the simple greedy algorithm:")
        analyze_solution(greedy)

    return longest_segments, max_coverage, greedy


def name_getter(stage_df, reduced_segments):
    index_list = []
    for seg in reduced_segments:
        index_list.append([ast.literal_eval(k) for k in stage_df["end_points"]].index(seg))

    reduced_df = stage_df.iloc[index_list]
    intervals = [ast.literal_eval(value) for value in reduced_df["end_points"].to_list()]
    total_diff = sum(b - a for a, b in intervals)
    reduced_df = reduced_df.copy()
    reduced_df.loc[:, "coverage"] = total_diff

    return reduced_df


def stage_list_getter(db_path, tour, year):
    """Given tour, year and database path it returns a list of stages"""
    with open(db_path, "r") as f:
        json_data = json.loads(f.read())

    segment_details_db_path = os.path.expanduser(json_data["global"]["segment_details_db_path"])

    conn = sqlite3.connect(segment_details_db_path)
    query = f"SELECT DISTINCT(stage) FROM  segment_details_data WHERE tour_year='{tour}-{year}'"
    stages = conn.execute(query).fetchall()
    return [stage[0] for stage in stages]


def segment_getter(db_path, stage, tour, year):
    """Given stage, tour, year and database path it returns a dataframe of segments"""
    with open(db_path, "r") as f:
        json_data = json.loads(f.read())

    segment_details_db_path = os.path.expanduser(json_data["global"]["segment_details_db_path"])
    conn = sqlite3.connect(segment_details_db_path)
    query = f"SELECT * FROM segment_details_data WHERE tour_year='{tour}-{year}' AND stage='{stage}' "
    df = pd.read_sql_query(query, conn)
    return df


def segment_analyser(db_path, stage, tour, year, hidden=False):
    segment_df = segment_getter(db_path, stage, tour, year)
    # segment_df = segment_df[ast.literal_eval(segment_df["hidden"])]
    if not hidden:
        segment_end_points = [
            ast.literal_eval(segment) for segment in segment_df.loc[segment_df["hidden"] == "False", "end_points"]
        ]
    else:
        segment_end_points = [ast.literal_eval(segment) for segment in segment_df["end_points"]]
    segment_end_points = [i for i in segment_end_points if i[1] - i[0] < 270]
    df_fin = name_getter(segment_df, segment_picker(segment_end_points)[1])
    return df_fin.drop(columns=["segment_id"])


def get_segment_table(tour, years, db_path):
    segment_df_full = pd.DataFrame()
    for year in years:
        stage_list = stage_list_getter(db_path, tour, year)
        for stage in stage_list:
            segment_df = segment_analyser(db_path, stage, tour, year, hidden=False)
            segment_df_full = pd.concat([segment_df_full, segment_df])
    return segment_df_full


def merged_tables(tour, years, segment_df, project_root, db_path):
    for year in years:
        with open(project_root / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        for i, id in enumerate(list(rider_list)[34:35]):
            rider = get_rider(id, tour, year, db_path, training=False, segment_data=True)
            if rider:  # Ensure rider is not None
                if rider.to_segment_df() is not None:
                    print(
                        f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                        f"Number of segments {len(rider.to_segment_df())}.",
                    )
                    data = rider.to_segment_df()
                    data = create_features(data, training=False)

            segment_df = segment_df.merge(
                data.drop(columns=["stage", "ride_day", "race_start_day", "tour_year"]), how="left", on=["segment_name"]
            )
            segment_df["dist_total_segments"] = segment_df.groupby("stage")["distance"].transform("sum")
            return segment_df
