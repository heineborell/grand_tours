#src/models/gt_polynomial.py
from pathlib import Path
import numpy as np
import seaborn as sns
##
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
##
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')

def train_polynomial_regression(X, y, itt_mask, degree=2):
    """
    Train a polynomial regression model and return parameters in a dictionary.    
    Input:
        X (array-like): Input feature matrix.
        y (array-like): Target values.
        degree (int): Degree of the polynomial regression.
    Returns:
        dict: Contains model, transformed X_train, y_train, error metrics, and polynomial transformer.
    """
    # Transform input features to polynomial features
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    
    # Split data while preserving ITT mask
    X_train, X_test, y_train, y_test, itt_train, itt_test = train_test_split(X_poly, y, itt_mask, test_size=0.2, random_state=113)
    
    # Train the regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Store parameters in a dictionary
    poly_reg_params = {
        "model": model,
        "X_train": X_train,
        "y_train": y_train,
        "mae": mean_absolute_error(y_test, y_pred),
        "mse": mean_squared_error(y_test, y_pred),
        "mape": mean_absolute_percentage_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred),
        "poly": poly,
        "ITT_indices": np.where(itt_train)[0]
    }
    return poly_reg_params
