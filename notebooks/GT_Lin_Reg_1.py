'''
Normalizing distances: X_norm  = (X - X_mean)/StDev
'''
import sqlite3
import pandas as pd
import numpy as np
#
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
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

##
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

def train_linear_regression(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return model, rmse, X_train, y_train

def train_polynomial_regression(X, y, degree=2):
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return model, rmse, X_train, y_train, poly

def plot_regression(model, X_train, y_train, include_itt, normalize, winners_only, table_name, fit_type, poly=None):
    tour_attributes = get_tour_color_attributes()
    if table_name not in tour_attributes:
        raise ValueError("Invalid table name.")
    plot_color = tour_attributes[table_name]["color"]
    tour_name = tour_attributes[table_name]["name"]
    #
    rmse_minutes = round(rmse, 2)
    rmse_hms = seconds_to_hms(rmse * 60)
    #-----------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(X_train, y_train, color=plot_color, edgecolors='k', s=15, label='Actual Data')
    if fit_type == "linear":
        ax.plot(X_train, model.predict(X_train), color='red', linewidth=2, label='Regression Line')
        textstr = f"RMSE: {rmse_minutes} min ({rmse_hms})\n{equation}"
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))
    else:
        X_sorted = np.sort(X_train, axis=0)
        X_poly_sorted = poly.transform(X_sorted)
        ax.plot(X_sorted, model.predict(X_poly_sorted), color='blue', linewidth=2, label='Polynomial Fit')
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Time (minutes)')
    ax.set_title(f'Distance vs Time (ITT: {include_itt}, Normalize: {normalize}, Winners Only: {winners_only}, Fit: {fit_type})')
    #
    textstr = f"RMSE: {rmse_minutes} min ({rmse_hms})"
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))
    ax.legend()
    fig.tight_layout()
    plt.savefig(f"Plots/Regression/{tour_name}_{fit_type}_Regression.png", bbox_inches='tight')
    plt.show()
    #-----------------------



# def plot_regression(model, X_train, y_train, include_itt, normalize, winners_only, table_name):
#     tour_attributes = get_tour_color_attributes()
#     if table_name not in tour_attributes:
#         raise ValueError("Invalid table name.")
#     plot_color = tour_attributes[table_name]["color"]
#     tour_name = tour_attributes[table_name]["name"]
#     #-----------------------------------#
#     fig, ax = plt.subplots(figsize=(10, 6))
#     #
#     ax.scatter(X_train, y_train, color=plot_color, edgecolors='k', s=15, label='Actual Data')
#     ax.plot(X_train, model.predict(X_train), color='red', lw=1, label='Regression Line')
#     ax.set_xlabel('Distance (km)')
#     ax.set_ylabel('Time (minutes)')
#     #
#     # Get model coefficients
#     slope = model.coef_[0]
#     intercept = model.intercept_
#     intercept_sign = "-" if intercept < 0 else "+"
#     equation = f"y = {slope:.2f}x {intercept_sign} {abs(intercept):.2f}"
#     #
#     rmse_minutes = round(rmse, 2)
#     rmse_hms = seconds_to_hms(rmse * 60)
#     ax.set_title(f'Distance vs Time (ITT: {include_itt}, Normalize: {normalize}, Winners Only: {winners_only})')
#     #
#     # Display RMSE and best-fit equation
#     textstr = f"RMSE: {rmse_minutes} min ({rmse_hms})\n{equation}"
#     ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
#             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))

#     ax.legend()
#     fig.tight_layout()
#     plt.savefig(f"Plots/Regression/{tour_name}_Linear_Regression.png", bbox_inches='tight')
#     plt.show()
#     #-----------------------------------#
##-----------------------
## control parameters
##-----------------------
gt_db_path = "data/grand_tours.db"
table_name = "giro_results"
include_itt = False
normalize = True
winners_only = True
fit_type = "linear"  # Change to "polynomial" for polynomial regression
# fit_type = "linear" 
#-----------------------
#-----------------------
df = fetch_data(gt_db_path, table_name, include_itt, winners_only)
X, y = preprocess_data(df, normalize)
if fit_type == "linear":
    model, rmse, X_train, y_train = train_linear_regression(X, y)
    plot_regression(model, X_train, y_train, include_itt, normalize, winners_only, table_name, fit_type)
else:
    model, rmse, X_train, y_train, poly = train_polynomial_regression(X, y)
    plot_regression(model, X_train, y_train, include_itt, normalize, winners_only, table_name, fit_type, poly=poly)
