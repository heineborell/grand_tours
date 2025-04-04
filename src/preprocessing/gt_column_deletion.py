# src/preprocessing/gt_column_deletion.py
from pathlib import Path
import sqlite3

'''
Let column to be deleted = chosen_column
1. Create a temporary table with all columns except the chosen_column.
2. Copy all data except the chosen_column into the temporary table.
3. Replace the original table with the temporary table.
'''

db_path = 'data/strava_segments.db'
table_name = 'segment_activity'
chosen_column = 'our_segment_id'
#
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all column names except the 'chosen_column'
cursor.execute(f"PRAGMA table_info({table_name});")
columns = [col[1] for col in cursor.fetchall() if col[1] != {chosen_column}]

# Join the remainingcolumn names for SQL queries
columns_str = ', '.join(columns)

# Drop the 'chosen_column' column using a temporary table
cursor.executescript(f"""
    PRAGMA foreign_keys=off;

    BEGIN TRANSACTION;

    CREATE TABLE temp_table AS 
    SELECT {columns_str} FROM {table_name};

    DROP TABLE {table_name};

    ALTER TABLE temp_table RENAME TO {table_name};

    COMMIT;

    PRAGMA foreign_keys=on;
""")
conn.commit()

print(f"Column {chosen_column} has been dropped successfully.")

# Close the connection
conn.close()