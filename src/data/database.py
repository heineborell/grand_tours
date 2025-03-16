import sqlite3

# from data.schemas import Rider, Ride


def get_db_connection(DB_PATH):
    return sqlite3.connect(DB_PATH)


def fetch_rides(DB_PATH):
    """Fetch all rides given date from the database."""
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats_data")
    riders_data = cursor.fetchall()
    return riders_data


# # Connect to an in-memory database
# conn_memory = sqlite3.connect(":memory:")
# cursor = conn_memory.cursor()
#
# # Attach both databases
# cursor.execute("ATTACH DATABASE 'database1.db' AS db1")
# cursor.execute("ATTACH DATABASE 'database2.db' AS db2")
#
# # Create a query that joins data from both databases
# query = """
# SELECT *
# FROM db1.table_name1 t1
# INNER JOIN db2.table_name2 t2 ON t1.common_column = t2.common_column
# """
#
#
# # Fetch directly with SQLite
# cursor.execute(query)
# merged_data = cursor.fetchall()
#
# conn_memory.close()
