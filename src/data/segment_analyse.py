"""This module optimizes segment selection using different strategies."""

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

    Args:
        segment1: First segment [start, end]
        segment2: Second segment [start, end]

    Returns:
        bool: True if segments overlap, False otherwise
    """
    return not (segment1[1] <= segment2[0] or segment2[1] <= segment1[0])


def optimize_segments(segments: list[list[int]], prefer_longest_segments: bool = True) -> list[list[int]]:
    """
    Find the optimal non-overlapping segments that either:
    1. Maximize total distance covered (prefer_longest_segments=False)
    2. Prefer longer individual segments (prefer_longest_segments=True)

    Args:
        segments: List of segments [start, end]
        prefer_longest_segments: Whether to prioritize longer individual segments

    Returns:
        list: Optimized non-overlapping segments ordered by start position
    """
    if not segments:
        return []

    if prefer_longest_segments:
        # Sort by length (descending), then by end position for tie-breaking
        sorted_segments = sorted(segments, key=lambda x: (-(x[1] - x[0]), x[1]))
        selected = []
        for segment in sorted_segments:
            # Check if current segment overlaps with any already selected segment
            if not any(check_overlap(segment, s) for s in selected):
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
        # Find the rightmost position where ends[j] <= sorted_segments[i][0]
        j = bisect_right(ends, sorted_segments[i][0]) - 1
        p.append(j)

    # Step 3: DP table to store max coverage
    dp = [0] * n
    selected_indices = [[] for _ in range(n)]

    for i in range(n):
        # Include the current segment
        incl = weights[i] + (dp[p[i]] if p[i] != -1 else 0)
        # Exclude the current segment
        excl = dp[i - 1] if i > 0 else 0

        if incl > excl:
            dp[i] = incl
            selected_indices[i] = (selected_indices[p[i]] if p[i] != -1 else []) + [i]
        else:
            dp[i] = excl
            selected_indices[i] = selected_indices[i - 1] if i > 0 else []

    return [sorted_segments[i] for i in selected_indices[-1]]


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

    ordered_list = sorted(segments, key=lambda x: x[1])
    selected = []
    for elmt in ordered_list:
        if not selected or selected[-1][1] <= elmt[0]:
            selected.append(elmt)
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
    # Filter segments longer than 100m (maintaining compatibility with first version)
    # segments = [i for i in segments if i[1] - i[0] < 100]

    # Apply different optimization strategies
    longest_segments = optimize_segments(segments, prefer_longest_segments=True)
    max_coverage = optimize_segments(segments, prefer_longest_segments=False)
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

    # Return all four strategies to maintain compatibility with first version
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
    if not hidden:
        segment_end_points = [
            ast.literal_eval(segment) for segment in segment_df.loc[segment_df["hidden"] == "False", "end_points"]
        ]
    else:
        segment_end_points = [ast.literal_eval(segment) for segment in segment_df["end_points"]]
    segment_end_points = [i for i in segment_end_points if i[1] - i[0] < 100]
    df_fin = name_getter(segment_df, segment_picker(segment_end_points)[1])
    # subprocess.run(["vd", "-f", "csv", "-"], input=df_fin.to_csv(index=False), text=True)
    return df_fin.drop(columns=["segment_id"])


def get_segment_table(tour, years, db_path):
    segment_df_full = pd.DataFrame()
    for year in years:
        stage_list = stage_list_getter(db_path, tour, year)
        for stage in stage_list:
            segment_df = segment_analyser(db_path, stage, tour, year)
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

                    segment_df["stage"] = segment_df["stage"].str.strip()
                    # subprocess.run(["vd", "-f", "csv", "-"], input=data.to_csv(index=False), text=True)

                    merged_df = segment_df.merge(
                        data.drop(columns=["ride_day", "race_start_day", "tour_year"]),
                        how="left",
                        on=["segment_name", "stage"],
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
