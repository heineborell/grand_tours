import pandas as pd
import numpy as np
##
from src.config import get_tour_attributes, PLOT_PATHS
##
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')
##

# -- Plot and summarize predictions
def summarize_and_plot_multivariate_regression(regression_result, table_name, feature_list):
    tour_attributes = get_tour_attributes()
    tour_color = tour_attributes[table_name]['color']
    tour_name = tour_attributes[table_name]['name']
    ##
    model = regression_result['model']
    y_test = regression_result['y_test']
    y_pred = regression_result['y_pred']
    r2 = regression_result['r2']
    rmse = regression_result['rmse']
    intercept = model.intercept_
    coefs = model.coef_
    ## Scatter plot of predicted vs actual 
    ## If the model is perfect, every point will lie exactly on the y=x line
    #-------------------
    fig, ax1 = plt.subplots(figsize=(10, 6.5))
    ax1.scatter(y_test, y_pred, color=tour_color, edgecolors='k', s=15, label='Predicted vs Actual')
    ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Ideal Fit')
    ax1.set_xlabel('Actual Time (min) ')
    ax1.set_ylabel('Predicted Time (min)')
    ax1.set_title(f'Predicted vs Actual Time')
    ax1.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"plots/multivariate/{tour_name}_Multivariate_regression.png", bbox_inches='tight')
    plt.show()
    plt.close()
    #-------------------

    # Residual plot
    #-------------------
    fig, ax2 = plt.subplots(figsize=(10, 6.5))
    residuals = y_test - y_pred
    ax2.axhline(0, color='red', linestyle='--', linewidth=1)
    ax2.scatter(y_pred, residuals, alpha=0.6, color=tour_color, edgecolors='k', s=15)
    ax2.set_xlabel('Predicted Time (min)')
    ax2.set_ylabel('Residual (Actual - Predicted)')
    ax2.set_title(f'Residual Error Plot')
    fig.tight_layout()
    plt.savefig(f"plots/multivariate/{tour_name}_Multivariate_regression_residuals.png", bbox_inches='tight')
    plt.show()
    plt.close()
    #-------------------

    # print('y test shape = )
    # percentage_error = np.sum(residual/y_test)

    # Print evaluation summary
    print("\n--- Model Summary ---")
    print(f"Features used: {feature_list}")
    print(f"R² score: {r2:.4f}")
    print(f"RMSE: {rmse:.2f} min")
    print(f"MAE: {regression_result['mae']:.2f} min")
    print(f"MSE: {regression_result['mse']:.2f} ")
    print(f"MAPE:{regression_result['mape']:.2f} ")
    print(f"Training samples: {len(regression_result['X_train'])}")
    print(f"Test samples: {len(regression_result['X_test'])}")
    terms = [f"{coefs[i]:.4f} * {feature_list[i]}" for i in range(len(feature_list))]
    equation = f"y = {intercept:.4f} + " + " + ".join(terms)
    print("\n--- Regression Equation ---")
    print(equation)
    print("----------------------")