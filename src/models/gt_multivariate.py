#src/models/gt_multivariate.py

import pandas as pd
import numpy as np
#
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, r2_score
#
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')

## Train linear regression on multivariate data
## y = β₀ + β₁ · distance + β₂ · stage_num + β₃ · vertical_meters + ...
def train_multivariate_regression(X, y, itt_mask):
    """
    Fits a LinearRegression model on multivariate data.
    Args:
        X (np.array): Feature matrix.
        y (np.array): Target vector.
        itt_mask (np.array): Mask for ITT rows.
    Returns:
        dict: Model, training info, and evaluation metrics.
    """
    X_train, X_test, y_train, y_test, itt_train, itt_test = train_test_split(
        X, y, itt_mask, test_size=0.2, random_state=108
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    multivariate_reg_params = {
        "model": model,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "mae": mean_absolute_error(y_test, y_pred),
        "mse": mean_squared_error(y_test, y_pred),
        "mape": mean_absolute_percentage_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred),
        "ITT_indices": np.where(itt_train)[0]
    }
    return multivariate_reg_params
