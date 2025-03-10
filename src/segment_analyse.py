def check_overlap(segment1: list[int], segment2: list[int]) -> bool:
    """
    Check if two segments overlap
    """
    return not (segment1[1] <= segment2[0] or segment2[1] <= segment1[0])


def find_compatible_segments(segments: list[list[int]], current_idx: int) -> list[int]:
    """
    Find all segments that are compatible (non-overlapping) with given segment
    """
    current = segments[current_idx]
    compatible = []

    for i, segment in enumerate(segments[:current_idx]):
        if not check_overlap(current, segment):
            compatible.append(i)

    return compatible


def optimize_segments(segments: list[list[int]], prefer_longest_segments: bool = True) -> list[list[int]]:
    """
    Find the optimal non-overlapping segments that either:
    1. Maximize total distance covered (prefer_longest_segments=False)
    2. Prefer longer individual segments (prefer_longest_segments=True)
    """
    if prefer_longest_segments:
        # Sort by length (descending), then by end position for tie-breaking
        sorted_segments = sorted(segments, key=lambda x: (-(x[1] - x[0]), x[1]))

        selected = []
        for segment in sorted_segments:
            # Check if this segment overlaps with any selected segments
            is_overlapping = any(check_overlap(segment, selected_segment) for selected_segment in selected)

            if not is_overlapping:
                # Check if this segment contains or is contained by other segments
                contains_smaller = False
                selected_to_remove = []

                for selected_segment in selected:
                    if segment[0] <= selected_segment[0] and segment[1] >= selected_segment[1]:
                        # Current segment completely contains a selected segment
                        selected_to_remove.append(selected_segment)
                    elif selected_segment[0] <= segment[0] and selected_segment[1] >= segment[1]:
                        # Current segment is contained within a selected segment
                        contains_smaller = True
                        break

                if not contains_smaller:
                    # Remove any smaller segments this one contains
                    for to_remove in selected_to_remove:
                        selected.remove(to_remove)
                    selected.append(segment)

    else:
        # For maximum coverage, use dynamic programming with overlap checking
        sorted_segments = sorted(segments, key=lambda x: (x[0], -x[1]))  # Sort by start, then length
        n = len(segments)

        if n == 0:
            return []

        # dp[i] stores the maximum coverage we can get using segments[0..i]
        dp = [(0, []) for _ in range(n)]  # Store value and segments used

        # Base case
        dp[0] = (sorted_segments[0][1] - sorted_segments[0][0], [0])

        # Fill dp table
        for i in range(1, n):
            current = sorted_segments[i]
            current_length = current[1] - current[0]

            # Find best compatible combination
            best_value = current_length
            best_segments = [i]

            # Check all compatible previous segments
            for j in range(i):
                if not check_overlap(current, sorted_segments[j]):
                    prev_value, prev_segments = dp[j]
                    # Check if adding current segment to this combination creates overlaps
                    is_compatible = True
                    for seg_idx in prev_segments:
                        if check_overlap(current, sorted_segments[seg_idx]):
                            is_compatible = False
                            break

                    if is_compatible:
                        total_value = prev_value + current_length
                        if total_value > best_value:
                            best_value = total_value
                            best_segments = prev_segments + [i]

            # Compare with previous best without current segment
            prev_value, prev_segments = dp[i - 1]
            if prev_value > best_value:
                best_value = prev_value
                best_segments = prev_segments

            dp[i] = (best_value, best_segments)

        # Get the final solution
        _, selected_indices = dp[n - 1]
        selected = [sorted_segments[i] for i in selected_indices]

    # Sort final result by start position
    return sorted(selected, key=lambda x: x[0])


def analyze_solution(segments: list[list[int]], result: list[list[int]]):
    """
    Analyze and print statistics about the solution
    """
    # Verify no overlaps
    for i, seg1 in enumerate(result):
        for seg2 in result[i + 1 :]:
            if check_overlap(seg1, seg2):
                print(f"WARNING: Overlap detected between {seg1} and {seg2}")

    total_coverage = sum(end - start for start, end in result)
    segment_lengths = [end - start for start, end in result]
    avg_segment_length = sum(segment_lengths) / len(segment_lengths)

    print(f"Number of segments: {len(result)}")
    print(f"Total coverage: {total_coverage} meters")
    print(f"Average segment length: {avg_segment_length:.2f} meters")
    print("Individual segments:")
    for start, end in result:
        print(f"  {start}-{end} ({end - start}m)")


# Example usage
def segment_picker(segments):
    print("\nOptimizing for longest segments:")
    longest_segments = optimize_segments(segments, prefer_longest_segments=True)
    analyze_solution(segments, longest_segments)

    print("\nOptimizing for maximum coverage:")
    max_coverage = optimize_segments(segments, prefer_longest_segments=False)
    analyze_solution(segments, max_coverage)

    return longest_segments, max_coverage
