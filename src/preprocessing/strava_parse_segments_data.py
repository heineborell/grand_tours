'''
1. Connects to the SQLite database and reads the segments_data table.
2. Parses the BLOB data in the segment column to extract the required fields.
3. Creates a new table called segment_activity with a specified schema.
4. Extracts and formats data according to the unit handling rules specified.
5. Inserts the parsed data into the new table.
'''
import sqlite3
import pandas as pd
import json
import re

# Paths for old and new databases
old_db_path = "data/training.db"  
new_db_path = 'data/strava_segments.db'  

# Read the original data from the old database
old_conn = sqlite3.connect(old_db_path)
df = pd.read_sql("SELECT activity_id, athlete_id, segment FROM segments_data", old_conn)
old_conn.close()

# Connect to the new SQLite database
new_conn = sqlite3.connect(new_db_path)
cursor = new_conn.cursor()

# Drop the existing table if it exists
cursor.execute("DROP TABLE IF EXISTS segment_activity")

# Create the new table 'segment_activity' in the new database with 'id' as the PRIMARY KEY
cursor.execute('''
    CREATE TABLE segment_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        athlete_id INTEGER,
        segment_name TEXT,
        segment_distance_km REAL,
        segment_vert_m REAL,
        segment_grade REAL,
        segment_time_seconds INTEGER,
        segment_speed_kph REAL,
        power_watt INTEGER,
        heart_rate_bpm INTEGER,
        vertical_ascent_m REAL,
        FOREIGN KEY (athlete_id) REFERENCES segments_data(athlete_id),
        FOREIGN KEY (segment_name) REFERENCES segments_data(segment_name)
    )
''')


'''
Example JSON BLOB
{"segment_name": ["Del puti al gim", "Osinbiribil - Kostorbe", "Repecho al Puente en la Gi-636", "Beraqueta Kalea Climb", "LA CUESTA DEL DIABLO", "Anzaran- Ficoba", "Sprint a Francia", "Climb Hopital Marin - Virage Galbarreta", "sprint", "Route de La Glaci\u00e8re", "D\u00e9but la Glaci\u00e8re", "Route Nationale Climb", "Sprint  la Glaci\u00e8re", "bajada Behobie", "Francia - AP Biriatou"],
 "segment_time": ["1:54", "1:28", "2:13", "1:34", "41s", "2:17", "45s", "2:05", "58s", "5:13", "2:03", "5:19", "1:24", "2:28", "1:37"], 
 "segment_speed": ["32.7km/h", "29.9km/h", "30.7km/h", "27.9km/h", "25.7km/h", "30.6km/h", "29.1km/h", "19.9km/h", "21.2km/h", "18.8km/h", "15.3km/h", "16.0km/h", "18.0km/h", "55.8km/h", "32.1km/h"], 
 "watt": ["\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014"], 
 "heart_rate": ["\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014", "\u2014"], 
 "segment_distance": ["1.03km", "0.73km", "1.13km", "0.73km", "0.29km", "1.16km", "0.36km", "0.69km", "0.34km", "1.63km", "0.52km", "1.42km", "0.42km", "2.29km", "0.86km"], 
 "segment_vert": ["2m", "9m", "15m", "137m", "12m", "14m", "6m", "29m", "14m", "84m", "42m", "94m", "25m", "111m", "3m"], 
 "segment_grade": ["0.2%", "1.0%", "1.3%", "18.8%", "4.2%", "-0.1%", "1.2%", "4.2%", "3.9%", "5.1%", "8.1%", "6.6%", "6.0%", "-4.9%", "-0.1%"], 
 "VAM": ["", "", "", "5254", "", "", "", "", "", "962", "", "1060", "", "", ""]}

'''
# Prepare a list to hold the parsed data
parsed_data = []

# Regex patterns for extracting numbers
pattern_kph = re.compile(r'(\d+\.?\d*)km/h')
pattern_km = re.compile(r'(\d+\.?\d*)km')
pattern_m = re.compile(r'(\d+\.?\d*)m')
pattern_w = re.compile(r'(\d+\.?\d*)W')
pattern_percent = re.compile(r'(\d+\.?\d*)%')
pattern_bpm = re.compile(r'(\d+)bpm')  

# Function to convert 'mm:ss' or 'hh:mm:ss' to total seconds
def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])  # mm:ss
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])  # hh:mm:ss
    return None

# Iterate through each row in the DataFrame
for _, row in df.iterrows():
    activity_id = row['activity_id']
    athlete_id = row['athlete_id']
    segment_data = json.loads(row['segment'])

    # Check if segment_data is empty (i.e., {})
    if not segment_data or segment_data == {}:
        continue  # Skip this row if segment_data is empty

    # Extract data for each segment
    for i in range(len(segment_data['segment_name'])):
        segment_name = segment_data['segment_name'][i]

        # Extract and convert values based on units
        segment_distance_km = float(pattern_km.search(segment_data['segment_distance'][i]).group(1)) if pattern_km.search(segment_data['segment_distance'][i]) else None
        segment_vert_m = float(pattern_m.search(segment_data['segment_vert'][i]).group(1)) if pattern_m.search(segment_data['segment_vert'][i]) else None
        segment_grade = float(pattern_percent.search(segment_data['segment_grade'][i]).group(1)) if pattern_percent.search(segment_data['segment_grade'][i]) else None

        # Convert 'segment_time' to total seconds
        segment_time_seconds = time_to_seconds(segment_data['segment_time'][i])

        segment_speed_kph = float(pattern_kph.search(segment_data['segment_speed'][i]).group(1)) if pattern_kph.search(segment_data['segment_speed'][i]) else None

        # Handle power_watt: keep "\u2014" as NULL, else extract number as INTEGER
        watt = segment_data['watt'][i]
        if watt != "\u2014":
            power_watt = int(pattern_w.search(watt).group(1)) if pattern_w.search(watt) else None
        else:
            power_watt = None  # Keep NULL if "\u2014"

        # Handle heart_rate_bpm: extract number if 'bpm' is present or keep NULL
        heart_rate = segment_data['heart_rate'][i]
        if heart_rate != "\u2014":
            heart_rate_bpm = int(pattern_bpm.search(heart_rate).group(1)) if pattern_bpm.search(heart_rate) else None
        else:
            heart_rate_bpm = None  # Keep NULL if "\u2014"

        # Handle VAM: empty string or convert to int
        vam = segment_data['VAM'][i]
        vertical_ascent_m = int(vam) if vam.isdigit() else None

        # Append extracted data to the list with updated column names
        parsed_data.append((
            activity_id, athlete_id, segment_name, segment_distance_km, segment_vert_m,
            segment_grade, segment_time_seconds, segment_speed_kph, power_watt, heart_rate_bpm,
            vertical_ascent_m
        ))

# Insert parsed data into the new table in the new database with updated column names
cursor.executemany('''
    INSERT INTO segment_activity (
        activity_id, athlete_id, segment_name, segment_distance_km, segment_vert_m,
        segment_grade, segment_time_seconds, segment_speed_kph, power_watt, heart_rate_bpm, vertical_ascent_m
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', parsed_data)

# Commit and close the new database connection
new_conn.commit()
new_conn.close()

print("\nSuccessfully created 'strava_segments.db' with 'segment_activity' table.\n")