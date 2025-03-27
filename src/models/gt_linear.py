#src/models/gt_linear.py

import numpy as np
##
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, r2_score

def train_linear_regression(X, y, itt_mask):
    """
    Train linear regression model and return parameters in a dictionary.
    Input:
        X (array-like): Input feature matrix.
        y (array-like): Target values.
        itt_mask (np.ndarray): Boolean array indicating ITT rows in the original data.
    Returns:
        dict: Contains model, transformed X_train, y_train, and error metrics.
    """
    ## Split data while preserving ITT mask
    X_train, X_test, y_train, y_test, itt_train, itt_test = train_test_split(X, y, itt_mask, test_size=0.2, random_state=108)
   
    ## Train the regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    ## Store parameters in a dictionary
    lin_reg_params = {
        "model": model,
        "X_train": X_train,
        "y_train": y_train,
        "num_test": len(X_test),
        "mae": mean_absolute_error(y_test, y_pred),
        "mse": mean_squared_error(y_test, y_pred),
        "mape": mean_absolute_percentage_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred),
        "ITT_indices": np.where(itt_train)[0]
    }
    return lin_reg_params
