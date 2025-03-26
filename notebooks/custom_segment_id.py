## Create a custom segment_id from (segment_name, segment_distance) pair
import sqlite3

db_path = 'data/strava_segments.db'
table_name = 'segment_activity'
#
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add the new column 'our_segment_id' if it doesn't exist
cursor.execute(f"""ALTER TABLE {table_name} ADD COLUMN our_segment_id INTEGER""")
conn.commit()

# Find duplicate segments based on name and distance
cursor.execute(f"""
    SELECT segment_name, segment_distance_km, COUNT(*) as count
    FROM {table_name}
    GROUP BY segment_name, segment_distance_km
    HAVING count > 1
""")

# Fetch all similar segment groups
similar_segments = cursor.fetchall()

# Assign unique IDs to similar segments
our_segment_id = 1  

for segment_name, segment_distance_km, _ in similar_segments:
    # Update the our_segment_id for similar segments
    cursor.execute(f"""
        UPDATE {table_name}
        SET our_segment_id = ?
        WHERE segment_name = ? AND segment_distance_km = ?
    """, (our_segment_id, segment_name, segment_distance_km))
    our_segment_id += 1  # Increment ID for next group

conn.commit()

# Print a summary of the updates
cursor.execute(f"""
    SELECT COUNT(DISTINCT our_segment_id) as unique_ids, COUNT(*) as total_rows
    FROM {table_name}
    WHERE our_segment_id IS NOT NULL
""")
unique_ids, total_rows = cursor.fetchone()
print(f"Assigned {unique_ids} unique IDs to {total_rows} similar segment rows.")

# Close the connection
conn.close()