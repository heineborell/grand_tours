"""This module is mostly written by chatgpt is has to be reviewed!"""

import ast
import json
import os
import sqlite3

import pandas as pd
from rich import print

from data.database import get_rider
from data.processing import create_features


def check_overlap(segment1: list[int], segment2: list[int]) -> bool:
    """
    Check if two segments overlap

    Args:
        segment1: First segment [start, end]
        segment2: Second segment [start, end]

    Returns:
        bool: True if segments overlap, False otherwise
    """
    return max(segment1[0], segment2[0]) < min(segment1[1], segment2[1])


def optimize_for_longest_segments(segments: list[list[int]]) -> list[list[int]]:
    """
    Find non-overlapping segments prioritizing longer individual segments.

    Args:
        segments: List of segments [start, end]

    Returns:
        list: Optimized non-overlapping segments ordered by start position
    """
    if not segments:
        return []

    # Sort by length (descending), then by start position for tie-breaking
    sorted_segments = sorted(segments, key=lambda x: (-(x[1] - x[0]), x[0]))

    selected = []
    for segment in sorted_segments:
        # Check if current segment overlaps with any already selected segment
        if not any(check_overlap(segment, selected_seg) for selected_seg in selected):
            selected.append(segment)

    # Return segments sorted by start position
    return sorted(selected, key=lambda x: x[0])


def optimize_for_maximum_coverage(segments: list[list[int]]) -> list[list[int]]:
    """
    Find non-overlapping segments maximizing total distance covered.
    Uses dynamic programming for optimal solution.

    Args:
        segments: List of segments [start, end]

    Returns:
        list: Optimized non-overlapping segments ordered by start position
    """
    if not segments:
        return []

    # Sort segments by end position
    segments = sorted(segments, key=lambda x: x[1])
    n = len(segments)

    # Initialize dp table and solution reconstruction info
    dp = [0] * (n + 1)  # dp[i] = max coverage using first i segments
    solution = [[] for _ in range(n + 1)]  # solution[i] = segments used for dp[i]

    for i in range(1, n + 1):
        # Find latest non-overlapping segment before current one
        j = i - 1
        while j > 0 and segments[j - 1][1] > segments[i - 1][0]:
            j -= 1

        # Case 1: Include current segment
        include_current = (segments[i - 1][1] - segments[i - 1][0]) + dp[j]

        # Case 2: Exclude current segment
        exclude_current = dp[i - 1]

        # Choose the better option
        if include_current > exclude_current:
            dp[i] = include_current
            solution[i] = solution[j] + [segments[i - 1]]
        else:
            dp[i] = exclude_current
            solution[i] = solution[i - 1]

    return sorted(solution[n], key=lambda x: x[0])


def optimize_for_shortest_segments(segments: list[list[int]]) -> list[list[int]]:
    """
    Find non-overlapping segments prioritizing shorter individual segments.

    Args:
        segments: List of segments [start, end]

    Returns:
        list: Optimized non-overlapping segments ordered by start position
    """
    if not segments:
        return []

    # Sort by length (ascending), then by start position for tie-breaking
    sorted_segments = sorted(segments, key=lambda x: (x[1] - x[0], x[0]))

    selected = []
    for segment in sorted_segments:
        # Check if current segment overlaps with any already selected segment
        if not any(check_overlap(segment, selected_seg) for selected_seg in selected):
            selected.append(segment)

    # Return segments sorted by start position
    return sorted(selected, key=lambda x: x[0])


def greedy_picker(segments: list[list[int]]) -> list[list[int]]:
    """
    Classic greedy algorithm for interval scheduling.
    Takes earliest ending segments that don't overlap.

    Args:
        segments: List of segments [start, end]

    Returns:
        list: Non-overlapping segments ordered by start position
    """
    if not segments:
        return []

    # Sort by end position
    sorted_segments = sorted(segments, key=lambda x: x[1])

    selected = [sorted_segments[0]]
    last_end = sorted_segments[0][1]

    for segment in sorted_segments[1:]:
        if segment[0] >= last_end:  # No overlap with last selected segment
            selected.append(segment)
            last_end = segment[1]

    return sorted(selected, key=lambda x: x[0])


def verify_solution(segments: list[list[int]]) -> bool:
    """
    Verify that a solution has no overlapping segments.

    Args:
        segments: List of segments [start, end]

    Returns:
        bool: True if solution is valid (no overlaps), False otherwise
    """
    for i in range(len(segments) - 1):
        for j in range(i + 1, len(segments)):
            if check_overlap(segments[i], segments[j]):
                return False
    return True


def analyze_solution(result: list[list[int]]):
    """
    Analyze and print statistics about the solution

    Args:
        result: List of non-overlapping segments
    """
    # Verify solution validity
    is_valid = verify_solution(result)
    if not is_valid:
        print("WARNING: Solution contains overlapping segments!")

    total_coverage = sum(end - start for start, end in result)
    segment_lengths = [end - start for start, end in result]
    avg_segment_length = sum(segment_lengths) / len(segment_lengths) if segment_lengths else 0

    print(f"Number of segments: {len(result)}")
    print(f"Total coverage: {total_coverage} meters")
    print(f"Average segment length: {avg_segment_length:.2f} meters")
    print("Individual segments:")
    for start, end in result:
        print(f"  {start}-{end} ({end - start}m)")


def segment_picker(segments, report=False):
    """
    Main function to select segments using different strategies.

    Args:
        segments: List of segments [start, end]
        report: Whether to print analysis of solutions

    Returns:
        tuple: (longest_segments, max_coverage, greedy, shortest_segments)
    """
    # Apply different optimization strategies
    segments = [i for i in segments if i[1] - i[0] < 100]
    longest_segments = optimize_for_longest_segments(segments)
    max_coverage = optimize_for_maximum_coverage(segments)
    greedy = greedy_picker(segments)
    shortest_segments = optimize_for_shortest_segments(segments)

    if report:
        print("\nOptimizing for longest segments:")
        analyze_solution(longest_segments)

        print("\nOptimizing for maximum coverage:")
        analyze_solution(max_coverage)

        print("\nOptimizing using the simple greedy algorithm:")
        analyze_solution(greedy)

        print("\nOptimizing for shortest segments:")
        analyze_solution(shortest_segments)

    # Return results in the same format as the original to maintain compatibility
    return longest_segments, max_coverage, greedy, shortest_segments


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
    segment_end_points = [i for i in segment_end_points if i[1] - i[0] < 200]
    df_fin = name_getter(segment_df, segment_picker(segment_end_points)[1])
    return df_fin.drop(columns=["segment_id"])


def get_segment_table(tour, years, db_path):
    segment_df_full = pd.DataFrame()
    for year in years:
        stage_list = stage_list_getter(db_path, tour, year)
        for stage in stage_list:
            segment_df = segment_analyser(db_path, stage, tour, year, hidden=True)
            segment_df_full = pd.concat([segment_df_full, segment_df])
    return segment_df_full


def merged_tables(tour, years, segment_df, project_root, db_path):
    for year in years:
        with open(project_root / f"config/config_{tour}_training-{year}_individual.json", "r") as f:
            train_config = json.loads(f.read())
        rider_list = [conf["strava_id"] for conf in train_config]
        final_table = None
        for i, id in enumerate(list(rider_list)):
            rider = get_rider(id, tour, year, db_path, training=False, segment_data=True)
            if rider:  # Ensure rider is not None
                if rider.to_segment_df() is not None:
                    # print(
                    #     f"rider id:{id}. Rider {i}/{len(rider_list)}.",
                    #     f"Number of segments {len(rider.to_segment_df())}.",
                    # )
                    data = rider.to_segment_df()
                    data = create_features(data, training=False)
                    data = data.astype(
                        {
                            "activity_id": "Int64",
                            "strava_id": "Int64",
                            "rider_name": "string",
                            "tour_year": "string",
                            "stage": "string",
                            "total_distance": "float",
                            "total_elevation": "Int64",
                            "distance": "float",
                            "time": "Int64",
                            "watt": "Int64",
                            "heart_rate": "Int64",
                        }
                    )

                    merged_df = segment_df.merge(
                        data.drop(columns=["stage", "ride_day", "race_start_day", "tour_year"]),
                        how="left",
                        on=["segment_name"],
                    )
                    merged_df["dist_total_segments"] = merged_df.groupby("stage")["distance"].transform("sum")
                    merged_df["elevation_total_segments"] = (
                        merged_df.assign(vertical_filtered=lambda df: df["vertical"].where(df["grade"] >= 0, 0))
                        .groupby("stage")["vertical_filtered"]
                        .transform("sum")
                    )
                    if final_table is None:
                        # even if merged_df is all NA, this ensures stable dtypes
                        final_table = pd.DataFrame(columns=merged_df.columns)
                        for col in merged_df.columns:
                            final_table[col] = final_table[col].astype(merged_df[col].dtype)

                    final_table = pd.concat([final_table, merged_df])

    final_table = final_table.drop(columns=["activity_id_x"])
    return final_table
