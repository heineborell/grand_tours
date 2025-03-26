import pandas as pd
import numpy as np
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
#
import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('bmh')

## Read the data for years 2000-2023 
db_path = "data/grand_tours.db"
conn = sqlite3.connect(db_path)
table_name = "giro_results"
query = f"""SELECT year, name, stage_num, distance, time FROM "{table_name}" WHERE year BETWEEN 2000 AND 2023"""
df = pd.read_sql_query(query, conn)

# Replace ,, with NaN safely
df["time"] = df["time"].replace(",,", np.nan)

# Forward-fill missing times per runner (now using 'name') and year
df.sort_values(by=["year", "name", "stage_num"], inplace=True)
df["time"] = df.groupby(["year", "name"])["time"].fillna(method="ffill")

# Convert time from hh:mm:ss or mm:ss to total seconds safely
def time_to_seconds(t):
    if isinstance(t, str) and ":" in t:  # Ensure t is a valid string
        parts = t.split(":")
        if len(parts) == 2:  # Case: "mm:ss"
            h, m, s = 0, int(parts[0]), int(parts[1])
        elif len(parts) == 3:  # Case: "hh:mm:ss"
            h, m, s = map(int, parts)
        else:
            return np.nan  # Unexpected format
        return h * 3600 + m * 60 + s
    return np.nan  # Handle NaN or invalid values

df["time_seconds"] = df["time"].apply(time_to_seconds)

# Drop rows with invalid time values
df.dropna(subset=["time_seconds"], inplace=True)

# Prepare data for regression
X = df[["distance"]]  
y = df["time_seconds"]   

# Train linear regression model
model = LinearRegression()
model.fit(X, y)

# Predict times for the known data (2000-2023) for RMSE evaluation
df["predicted_time_seconds"] = model.predict(X)

# Ensure y and predictions are valid before computing RMSE
if not df["predicted_time_seconds"].isna().any():
    rmse = np.sqrt(mean_squared_error(df["time_seconds"], df["predicted_time_seconds"]))
else:
    rmse = np.nan  # Handle the case where no valid predictions exist

# Load 2024 data to predict
query_2024 = f"""SELECT stage_num, distance FROM "{table_name}" WHERE year = 2024"""
df_2024 = pd.read_sql_query(query_2024, conn)

# Predict times for 2024 sections
df_2024["predicted_time_seconds"] = model.predict(df_2024[["distance"]])

# Convert seconds back to hh:mm:ss
def seconds_to_time(s):
    if np.isnan(s):  # Handle any unexpected NaN values
        return "00:00:00"
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    s = int(s % 60)
    return f"{h:02}:{m:02}:{s:02}"

df_2024["predicted_time"] = df_2024["predicted_time_seconds"].apply(seconds_to_time)

# Close database connection
conn.close()

# Print RMSE result safely
if np.isnan(rmse):
    print("\nRMSE could not be calculated due to missing data.")
else:
    print(f"\nModel RMSE: {rmse:.2f} seconds\n")

# Print the first few rows of predicted times
print("Predicted Winning Times for 2024:\n")
print(df_2024[["stage_num", "distance", "predicted_time"]].head(10).to_string(index=False))

#-----------------------------------#
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(X, y, color="blue", label="Actual Times")
ax.plot(X, model.predict(X), color="red", linewidth=2, label="Regression Line")
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Time (seconds)")
ax.set_title("Linear Regression:  time vs distance")
fig.tight_layout()
plt.savefig("Plots/LR_for_"+ table_name  +".png", bbox_inches='tight')
plt.show()
#-----------------------------------#