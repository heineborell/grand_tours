import pandas as pd
import numpy as np
import sqlite3
import re
'''
# List all the tables in the database 
db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(db_cursor.fetchall())

# Output:
#     tdf_results
#     giro_results
#     vuelta_results
#     strava_names
#     segments_data
#     stats_data
#     strava_table

# Similarly using pandas
table = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(table)

## Outout: 
             name
0     tdf_results
1    giro_results
2  vuelta_results
3    strava_names
4   segments_data
5      stats_data
6    strava_table
'''

## A more comprehensive way to print table & column names:
## https://stackoverflow.com/questions/305378/how-do-i-get-a-list-of-tables-the-schema-a-dump-using-the-sqlite3-api/33100538#33100538
## https://tomordonez.com/get-schema-sqlite-python/

conn = sqlite3.connect('grand_tours.db')
db_cursor = conn.cursor()


newline_indent = '\n   '
conn.text_factory = str

result = db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
table_names = sorted(list(zip(*result))[0])
print ("\ntables are:"+newline_indent+newline_indent.join(table_names))

for table_name in table_names:
    result = db_cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall()
    column_names = list(zip(*result))[1]
    #print (("\ncolumn names for %s:" % table_name) +newline_indent +(newline_indent.join(column_names)))
    #
    print (("\n\nColumn schema for table %s:" % table_name))
    for row in db_cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall():
        print(row)

print ("\nexiting.")
#

db_cursor.close()
conn.close()

def basic_database_summary(db_path):
    #
    ## https://stackoverflow.com/questions/305378/how-do-i-get-a-list-of-tables-the-schema-a-dump-using-the-sqlite3-api/33100538#33100538
    ## https://tomordonez.com/get-schema-sqlite-python/
    #
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #
    newline_indent = '\n   '
    conn.text_factory = str

    result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = sorted(list(zip(*result))[0])
    print ("\ntables are:"+newline_indent+newline_indent.join(table_names))

    for table_name in table_names:
        result = cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        #print (("\ncolumn names for %s:" % table_name) +newline_indent +(newline_indent.join(column_names)))
        #
        print (("\n\nColumn schema for table %s:" % table_name))
        for row in cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall():
            print(row)
    #
    # Close the connection
    cursor.close()
    conn.close()