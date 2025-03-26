import sqlite3
import pandas as pd
import numpy as np
#
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
##
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')

## Function that contains dictionary of tour-color attributes 
def get_tour_color_attributes():
    tour_color_attributes = {
        "tdf_results": {"name": "tdf", "color": "yellow"},
        "giro_results": {"name": "giro", "color": "pink"},
        "vuelta_results": {"name": "vuelta", "color": "red"}
    }
    return tour_color_attributes

## copy/paste the data from grand_tours.db and save it to a pandas dataframe.
def fetch_data(db_path, table_name, include_itt=True, winners_only=False):
    conn = sqlite3.connect(db_path)
    query = f"""SELECT year, stage_num, name, distance, time, ITT FROM {table_name} WHERE time IS NOT NULL """
    if not include_itt:
        query += " AND ITT = 0"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if winners_only:
        df = df.sort_values(by=['year', 'stage_num']).groupby(['year', 'stage_num']).first().reset_index()
    return df

##
def convert_time_to_seconds(time_str):
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return np.nan
    except:
        return np.nan
    
##
def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

##
def preprocess_data(df, normalize=False):
    df['time'] = df['time'].apply(convert_time_to_seconds)
    df = df.dropna()
    outliers = df[df['time'] / 60 > 1200]
    if not outliers.empty:
        print("Outlier data detected from year:", outliers['year'].unique())
    df = df[df['time'] / 60 <= 1200]
    X = df[['distance']].values
    y = df['time'].values / 60
    if normalize:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
    return X, y

##
def train_linear_regression(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    #
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    return model, X_train, y_train, rmse, mae, mse, r2

## 
def plot_linear_regression(table_name, model, X_train, y_train, include_itt, normalize, winners_only, rmse, mae, mse, r2):
    tour_attributes = get_tour_color_attributes()
    if table_name not in tour_attributes:
        raise ValueError("Invalid table name.")
    plot_color = tour_attributes[table_name]["color"]
    tour_name = tour_attributes[table_name]["name"]
    #
    itt_label = "ITT_T" if include_itt else "ITT_F"
    norm_label = "N_T" if normalize else "N_F"
    winners_label = "WO_T" if winners_only else "WO_F"
    #-------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(X_train, y_train, color=plot_color, edgecolors='k', s=15, label='Actual Data')
    ax.plot(X_train, model.predict(X_train), color='b', lw=1.5, label='Regression Line')
    b1 = model.coef_[0]
    b0 = model.intercept_
    intercept_sign = "-" if b0 < 0 else "+"
    equation = f"y = {b1:.2f}x {intercept_sign} {abs(b0):.2f}" if not normalize else f"Y = {b1:.2f}X {intercept_sign} {abs(b0):.2f}" 
    #
    ax.set_xlabel('Distance (km)' if not normalize else 'Normalized Distance', fontsize=14)
    ax.set_ylabel('Time (minutes)' if not normalize else 'Normalized Time', fontsize=14)
    rmse_minutes = round(rmse, 2)
    rmse_hms = seconds_to_hms(rmse * 60)
    ax.set_title(f'{tour_name} distance vs time (ITT: {include_itt}, Normalize: {normalize}, Winners Only: {winners_only}, Fit: Linear)')
    textstr = f" MAE: {mae:.2f} min \n MSE: {mse:.2f} \n RMSE: {rmse_minutes} min ({rmse_hms}) \n R²: {r2:.3f} \n {equation}"
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))
    # set font size for both major and minor ticks
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    ax.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"Plots/Regression/{tour_name}_Linear_Regression_{itt_label}_{norm_label}_{winners_label}.png", bbox_inches='tight')
    plt.show()
    #-------------------

##-----------------------
## control parameters
##-----------------------
gt_db_path = "data/grand_tours.db"
# table_name = "giro_results"
# table_name = "tdf_results"
table_name = "vuelta_results"
include_itt = False
normalize = False
winners_only = True
#-----------------------
df = fetch_data(gt_db_path, table_name, include_itt, winners_only)
X, y = preprocess_data(df, normalize)
model, X_train, y_train, rmse, mae, mse, r2 = train_linear_regression(X, y)
print("\n")
print("Mean Absolute Error (MAE) = average of |y_test - y_pred| = ", mae)
print("Mean Squared Error (MSE) = average of (y_test^2 - y_pred^2) = ", mse)
print("Root Mean Squared Error (RMSE) = sqrt(MSE) = ", rmse )
print("R^2 = ", r2)
print("\n")
plot_linear_regression(table_name, model, X_train, y_train, include_itt, normalize, winners_only, rmse, mae, mse, r2)
