import sqlite3
import pandas as pd
import re

def split_tour_year_column(db_path, table_name):
    # Purpose: In the gradtours.db database in the tables 
    #          'stats_data', 'segments_data', and strava_table 
    #          split the column 'tour_year' to 'tour' and 'year'
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"""SELECT * FROM "{table_name}" """, conn)  
    #----------------------------#
    # ChatGpt: split 'tour_year' into 'tour' and 'year'
    df[['tour', 'year']] = df['tour_year'].str.extract(r'^(.*)-(\d{4})$')
    #
    df['year'] = df['year'].astype(int)  # Convert 'year' to integer type
    # Drop the original 'tour_year' column
    df = df.drop(columns=['tour_year'])
    #
    # Save the modified DataFrame back to the database
    df.to_sql(f"{table_name}", conn, if_exists='replace', index=False)  
    conn.close()
    print(f"\nSuccessfully split 'tour_year' {table_name} into 'tour' and 'year' columns.\n")
    #----------------------------#
    return None
#    
def split_stage_column(db_path, table_name):
    # Purpose: In the gradtours.db database in all tables split the column
    #          'stage' to 'stage_num' and 'ITT' where ITT can be 1 or 0.
    #        
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"""SELECT * FROM "{table_name}" """, conn)  
    #----------------------------#
    # ChatGpt: split 'stage' into 'stage_num' and 'ITT'
    # Extract integers from 'stage' into a new column 'stage_num'
    df['stage_num'] = df['stage'].str.extract(r'(\d+)').astype(int)
    #
    # Create a new column 'ITT' where 1 if '(ITT)' is in 'stage', else 0
    df['ITT'] = df['stage'].str.contains(r'\(ITT\)', regex=True).astype(int)
    #
    # Drop the original 'stage' column
    # df = df.drop(columns=['stage'])
    #
    # Save the modified DataFrame back to the database
    df.to_sql(f"{table_name}", conn, if_exists='replace', index=False) 
    #
    conn.close()
    print(f"\nSuccessfully updated {table_name} by extracting 'stage_num' and 'ITT' columns.\n")
    #----------------------------#
    return None
#

db_path = "data/grand_tours.db"
#
#--------- Split tour_year to tour and year column -------------------#
# table_name = "segments_data"
# table_name = "stats_data"
# table_name = "strava_table"
# split_tour_year_column(db_path,table_name)
#
#--------- Split stage in to stage_num and ITT columns -------------------#
# table_name = "strava_table"
# table_name = "giro_results"
# table_name = "tdf_results"
table_name = "vuelta_results"
split_stage_column(db_path,table_name)

