import sqlite3
import pandas as pd
import numpy as np
#
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
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
def adjusted_r2(r2, n, k):
    """
    Compute Adjusted R² Score where 
    Adjusted R² compensates for model complexity by penalizing unnecessary terms.
    R2 = regular R² score
    n = number of samples
    k = number of independent variables (features)
    """
    return 1 - ((1 - r2) * (n - 1) / (n - k - 1))

##
def train_polynomial_regression(X, y, degree=2):
    print("made it")
    y = np.ravel(y)
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    #
    X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)
    #
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    #
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    adj_r2 = adjusted_r2(r2, X_test.shape[0], X_test.shape[1] - 1) 
    return model, X_train, X_test, y_train, y_test, rmse, mse, mae, adj_r2, r2, poly

## 
def plot_poly_regression(table_name, model, X_train, y_train, include_itt, normalize, winners_only, rmse, mse, mae, adj_r2, r2, poly):
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
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(X_train[:, 1], y_train, color=plot_color, edgecolors='k', s=15, label='Actual Data')
    #
    # Sort values for a smooth regression curve
    sorted_indices = X_train[:, 1].argsort()
    X_sorted = X_train[sorted_indices, 1].reshape(-1, 1)  # Original feature values
    X_poly_sorted = poly.transform(X_sorted)  # Transform to polynomial features
    y_poly_pred = model.predict(X_poly_sorted)  # Predictions
    ax.plot(X_sorted, y_poly_pred, color='b', lw=1.5, label="Polynomial Regression Fit")
    #
    b0, b1, b2 = model.intercept_, model.coef_[1], model.coef_[2]
    b1_sign = "-" if b1 < 0 else "+"
    b2_sign = "-" if b2 < 0 else "+"
    equation = f"y = {b0:.2f} {b1_sign} {abs(b1):.2f}x {b2_sign} {abs(b2):.2f}x²" if not normalize else f"Y = {b0:.2f} {b1_sign} {abs(b1):.2f}X {b2_sign} {abs(b2):.2f}X²"
    ax.set_title(f'Distance vs Time (ITT: {include_itt}, Normalize: {normalize}, Winners Only: {winners_only}, Fit: Polynomial)')
    # textstr = f" MAE: {mae:.2f} min \n MSE: {mse:.2f} \n RMSE: {rmse_minutes} min ({rmse_hms}) \n {equation}"
    rmse_hms = seconds_to_hms(rmse * 60)
    textstr = f"MAE: {mae:.2f}\nMSE: {mse:.2f}\nRMSE: {rmse:.2f} min ({rmse_hms}) \nR²: {r2:.3f}\nAdj R²: {adj_r2:.3f}\n{equation}"
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))
    #
    ax.set_xlabel('Distance (km)' if not normalize else 'Normalized Distance', fontsize=14)
    ax.set_ylabel('Time (minutes)' if not normalize else 'Normalized Time', fontsize=14)
    # set font size for both major and minor ticks
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    ax.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"Plots/Regression/{tour_name}_Polynomial_Regression_{itt_label}_{norm_label}_{winners_label}.tiff", format="tiff", dpi=300, bbox_inches='tight')
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
print("X shape:", X.shape)
print("y shape:", y.shape)
model, X_train, X_test, y_train, y_test, rmse, mse, mae, adj_r2, r2, poly = train_polynomial_regression(X, y)
# model, X_train, X_test, y_train, y_test, rmse, mse, mae, poly= train_polynomial_regression(X, y)
print("\n")
print("Mean Absolute Error (MAE) = average of |y_test - y_pred| = ", mae)
print("Mean Squared Error (MSE) = average of (y_test^2 - y_pred^2) = ", mse)
print("Root Mean Squared Error (RMSE) = sqrt(MSE) = ", rmse )
print("\n")
plot_poly_regression(table_name, model, X_train, y_train, include_itt, normalize, winners_only, rmse, mse, mae, adj_r2, r2, poly)







# import sqlite3
# import pandas as pd
# import numpy as np
# ##
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.preprocessing import PolynomialFeatures
# ##
# import matplotlib.pyplot as plt
# from matplotlib.ticker import FixedLocator
# from matplotlib import style
# plt.style.use('bmh')

# ## Function that contains dictionary of tour-color attributes 
# def get_tour_color_attributes():
#     tour_color_attributes = {
#         "tdf_results": {"name": "TDF", "color": "yellow"},
#         "giro_results": {"name": "Giro", "color": "pink"},
#         "vuelta_results": {"name": "Vuelta", "color": "red"}
#     }
#     return tour_color_attributes

# def fetch_distance_and_time_data(db_path, table_name, fit_params):
#     """
#     Copy/paste race data from an SQLite database based on specified filtering conditions.
#     Input:
#         db_path (str): Path to the SQLite database file.
#         table_name (str): Name of the table containing race data.
#         fit_params (dict): Dictionary containing filtering options such as:
#             - 'Include ITT': Whether to include Individual Time Trial (ITT) stages.
#             - 'Winners only': Whether to filter only stage winners.
#     Returns:
#         pd.DataFrame: A Pandas DataFrame containing the filtered race data.

#     The function executes an SQL query to select relevant columns from the specified table,
#     filtering out rows where time data is missing. If 'Include ITT' is False, it further 
#     filters out ITT stages. Additionally, if 'Winners only' is set to True, the data is 
#     grouped by year and stage number to retain only the first-ranked competitor per stage.
#     """
#     conn = sqlite3.connect(db_path)
#     query = f"""SELECT year, stage_num, distance, time, ITT FROM {table_name} WHERE time IS NOT NULL """

#     if not fit_params['Include ITT']:
#         query += " AND ITT = 0"
#     df = pd.read_sql_query(query, conn)
#     conn.close()

#     if fit_params['Winners only']:
#         df = df.sort_values(by=['year', 'stage_num']).groupby(['year', 'stage_num']).first().reset_index()
#     return df


# def convert_time_to_seconds(time_str):
#     """
#     Convert a time string in HH:MM:SS or MM:SS format into total seconds.
#     Input:
#         time_str (str): A string representing time in either "HH:MM:SS" or "MM:SS" format.
#     Returns:
#         int or float: The total time in seconds. If input is invalid, returns NaN.
#     """
#     try:
#         parts = list(map(int, time_str.split(':')))
#         if len(parts) == 3:
#             return parts[0] * 3600 + parts[1] * 60 + parts[2]
#         elif len(parts) == 2:
#             return parts[0] * 60 + parts[1]
#         return np.nan
#     except:
#         return np.nan
    

# def seconds_to_hms(seconds):
#     """
#     Convert a total number of seconds into a formatted HH:MM:SS string.
#     Input:
#         seconds (int or float): The total number of seconds.
#     Returns:
#         str: A string representing the time in "HH:MM:SS" format.
#     """
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     return f"{hours:02}:{minutes:02}:{seconds:02}"


# def preprocess_regression_data(df, fit_params):
#     """
#     Preprocess race data for regression analysis by converting time formats, removing outliers, 
#     and normalizing features if specified.
#     Input:
#         df (pd.DataFrame): DataFrame containing race data.
#         fit_params (dict): Dictionary containing preprocessing options such as:
#             - 'Normalize': Whether to standardize the feature values.
#     Returns:
#         tuple: (X, y)
#             - X (numpy.ndarray): Processed feature matrix containing distance values.
#             - y (numpy.ndarray): Target variable representing time in minutes.
#     The function:
#         - Converts time from HH:MM:SS or MM:SS format into total seconds.
#         - Filters out missing values.
#         - Identifies and removes outliers where time exceeds 20 hours.
#         - Extracts 'distance' as the feature (X) and 'time' (in minutes) as the target variable (y).
#         - Normalizes X using `StandardScaler` if 'Normalize' is set to True.
#     """
#     df['time'] = df['time'].apply(convert_time_to_seconds)
#     df = df.dropna()

#     outliers = df[df['time'] / 60 > 1200]
#     if not outliers.empty:
#         print("Outlier data detected from year:", outliers['year'].unique())
#     df = df[df['time'] / 60 <= 1200]
    
#     # Extract ITT mask before modifying X, y
#     itt_mask = df['ITT'] == 1

#     X = df[['distance']].values
#     y = df['time'].values / 60

#     if fit_params['Normalize'] == True:
#         scaler = StandardScaler()
#         X = scaler.fit_transform(X)
#     return X, y, itt_mask

# def train_polynomial_regression(X, y, itt_mask, degree=2):
#     """
#     Train a polynomial regression model and return parameters in a dictionary.    
#     Input:
#         X (array-like): Input feature matrix.
#         y (array-like): Target values.
#         degree (int): Degree of the polynomial regression.
#     Returns:
#         dict: Contains model, transformed X_train, y_train, error metrics, and polynomial transformer.
#     """
#     # Transform input features to polynomial features
#     poly = PolynomialFeatures(degree=degree)
#     X_poly = poly.fit_transform(X)
    
#     # Split data while preserving ITT mask
#     X_train, X_test, y_train, y_test, itt_train, itt_test = train_test_split(X_poly, y, itt_mask, test_size=0.2, random_state=42)

#     # # Split data into training and testing sets
#     # X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)
#     num_train = len(X_train)
#     num_test = len(X_test)

#     # Train the polynomial regression model
#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # Predict on test data
#     y_pred = model.predict(X_test)

#     # Calculate evaluation metrics
#     mae = mean_absolute_error(y_test, y_pred)
#     mse = mean_squared_error(y_test, y_pred)
#     rmse = np.sqrt(mse)
#     r2 = r2_score(y_test, y_pred)

#     # Convert ITT boolean mask into index positions
#     itt_train_indices = np.where(itt_train)[0]

#     # Store parameters in a dictionary
#     poly_reg_params = {
#         "model": model,
#         "X_train": X_train,
#         "y_train": y_train,
#         "num_train": num_train,
#         "num_test": num_test,
#         "mae": mae,
#         "mse": mse,
#         "rmse": rmse,
#         "r2": r2,
#         "poly": poly,
#         "ITT_indices": itt_train_indices
#     }
#     return poly_reg_params

# def plot_poly_regression(table_name, fit_params, poly_reg_params):
#     """
#     Plot the polynomial regression fit with actual training data.
#     Input:
#         poly_reg_params (dict): Dictionary containing model, training data, and error metrics.
#     """
#     ## 1. IF ITT = TRUE HIGHLIGHT THE POINTS WITH GREEN
#     tour_attributes = get_tour_color_attributes()
#     plot_color = tour_attributes[table_name]["color"]
#     tour_name = tour_attributes[table_name]["name"]
#     ##
#     itt_txt = "ITT_T" if fit_params['Include ITT'] else "ITT_F"
#     norm_txt = "N_T" if fit_params['Normalize']  else "N_F"
#     winners_txt = "WO_T" if fit_params['Winners only']  else "WO_F"
#     #
#     itt_indices = poly_reg_params['ITT_indices']
#     #-------------------
#     fig, ax = plt.subplots(figsize=(10, 6.5))
#     ax.scatter(poly_reg_params['X_train'][:, 1], poly_reg_params['y_train'], color=plot_color, edgecolors='k', s=10, label='Actual Data')
#     if len(itt_indices) > 0:
#         ax.plot(poly_reg_params['X_train'][itt_indices, 1], poly_reg_params['y_train'][itt_indices], marker='o',  mfc=plot_color, mec='b', ms=4, ls='None', label="ITT")
#     #
#     sorted_indices = poly_reg_params['X_train'][:, 1].argsort()
#     X_sorted = poly_reg_params['X_train'][sorted_indices, 1].reshape(-1, 1)  # Original feature values
#     X_poly_sorted = poly_reg_params['poly'].transform(X_sorted)  # Transform to polynomial features
#     y_poly_pred = poly_reg_params['model'].predict(X_poly_sorted)  # Predictions
#     ax.plot(X_sorted, y_poly_pred, color='b', lw=1.5, label="Polynomial Regression Fit")
#     #
#     b0 = poly_reg_params['model'].intercept_
#     b1 = poly_reg_params['model'].coef_[1]
#     b2 = poly_reg_params['model'].coef_[2]
#     b1_sign = "-" if b1 < 0 else "+"
#     b2_sign = "-" if b2 < 0 else "+"
#     if (fit_params['Normalize'] == False):
#         equation = f"y = {b0:.2f} {b1_sign} {abs(b1):.2f}x {b2_sign} {abs(b2):.2f}x²" 
#     else: 
#         equation = f"Y = {b0:.2f} {b1_sign} {abs(b1):.2f}X {b2_sign} {abs(b2):.2f}X²"
#     # num_train = poly_reg_params['num_train']
#     # num_test = poly_reg_params['num_test']
#     # mae = poly_reg_params['mae']
#     # mse = poly_reg_params['mse']
#     # rmse = poly_reg_params['rmse']
#     # r2 = poly_reg_params['r2']
#     #
#     fit_text = '\n'.join([f"{key}: {'T' if value else 'F'}" for key, value in fit_params.items()])
#     # count_text = f"N$_{{train}}$: {num_train} \nN$_{{test}}$:{num_test}\n"
#     # rmse_hms = seconds_to_hms(rmse * 60)
#     # textstr = f"MAE: {mae:.2f}\nMSE: {mse:.2f}\nRMSE: {rmse:.2f} min ({rmse_hms}) \nR²: {r2:.3f}\n{equation}\n{count_text}\n{"-"*30}\n{fit_text}"
#     # Display evaluation metrics and equation
#     textstr = (f"MAE: {poly_reg_params['mae']:.2f} min\n"
#                f"MSE: {poly_reg_params['mse']:.2f}\n"
#                f"RMSE: {poly_reg_params['rmse']:.2f} min\n"
#                f"R²: {poly_reg_params['r2']:.3f}\n"
#                f"{equation}\n"
#                f"N$_{{train}}$: {poly_reg_params['num_train']}\n"
#                f"N$_{{test}}$:{poly_reg_params['num_test']}\n"
#                f"{"-"*30}\n"
#                f"{fit_text}")
#     ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', ec='black', fc='white'))
#     #
#     ax.set_xlabel('Distance (km)' if not fit_params['Normalize'] else 'Normalized Distance', fontsize=14)
#     ax.set_ylabel('Time (minutes)' if not fit_params['Normalize'] else 'Normalized Time', fontsize=14)
#     ax.set_title(f'Polynomial regression for distance vs time for {tour_name}',fontsize=14)
#     ax.tick_params(axis='both', which='major', labelsize=14)
#     ax.tick_params(axis='both', which='minor', labelsize=10)
#     ax.legend(fontsize=12)
#     fig.tight_layout()
#     plt.savefig(f"Plots/Regression/{tour_name}_Polynomial_Regression_{itt_txt}_{norm_txt}_{winners_txt}_v2.png", bbox_inches='tight')
#     plt.show()
#     #-------------------

# ##-----------------------
# ## control parameters
# ##-----------------------
# gt_db_path = "data/grand_tours.db"
# table_name = "giro_results"
# # table_name = "tdf_results"
# # table_name = "vuelta_results"
# include_itt = True
# normalize = False
# winners_only = True
# #-----------------------
# fit_params = {"Include ITT": include_itt, "Normalize": normalize, "Winners only": winners_only}

# df  = fetch_distance_and_time_data(gt_db_path, table_name, fit_params)
# X, y, itt_mask = preprocess_regression_data(df, fit_params)
# poly_reg_params = train_polynomial_regression(X, y,itt_mask)
# plot_poly_regression(table_name, fit_params, poly_reg_params)
