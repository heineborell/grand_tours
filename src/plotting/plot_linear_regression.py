#src/plotting/plot_linear_regression.py

import numpy as np
import seaborn as sns
##
from src.config import PLOT_PATHS,OUTPUT_PATHS, get_tour_attributes
from src.utils.time_utils import seconds_to_hms
##
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')
##

def summarize_and_plot_linear_regression(table_name, fit_params, lin_reg_params):
    """
    Plot the linear regression fit with actual training data.
    Input:
        table_name (string): name of database table 
        lin_reg_params (dict): Dictionary containing model, training data, and error metrics.
        fit_params (dict): Dictionary containing preprocessing options
    """
    ## Unpack the reg_parameters:
    model = lin_reg_params['model']
    X_train = lin_reg_params['X_train']
    y_train = lin_reg_params['y_train']
    mae = lin_reg_params['mae']
    mse = lin_reg_params['mse']
    mape = lin_reg_params['mape']
    rmse = lin_reg_params['rmse']
    r2 = lin_reg_params['r2']
    itt_indices = lin_reg_params['ITT_indices']
    ##
    tour_attributes = get_tour_attributes()
    tour_color = tour_attributes[table_name]['color']
    tour_name = tour_attributes[table_name]['name']
    ##
    itt_txt = "ITT_T" if fit_params['Include ITT'] else "ITT_F"
    norm_txt = "N_T" if fit_params['Normalize']  else "N_F"
    
    #-------------------
    fig, ax = plt.subplots(figsize=(10, 6.5))
    # plot data
    ax.scatter(X_train, y_train, color=tour_color, edgecolors='k', s=15, label=f"{tour_name} Data")
    if len(itt_indices) > 0:
        print(f"\nlen itt_indices = {len(itt_indices)}")
        ax.plot(X_train.iloc[itt_indices], y_train.iloc[itt_indices], marker='o',  mfc='b', mec='k', ms=4, ls='None', label=f"{tour_name} ITT Data")
    # plot prediction-equation
    y_lin_pred = model.predict(X_train)
    ax.plot(X_train, y_lin_pred, color='b', lw=1.5, label='Regression Line')
    #
    ## Write summary of regression
    b1 = model.coef_[0]
    b0 = model.intercept_
    b0_sign = "-" if b0 < 0 else "+"
    equation = f"y = {b1:.2f}x {b0_sign} {abs(b0):.2f}" if not fit_params['Normalize'] else f"Y = {b1:.2f}X {b0_sign} {abs(b0):.2f}"
    fit_text = '\n'.join([f"{key}: {'T' if value else 'F'}" for key, value in fit_params.items()])
    summary_text = (f"MAE: {mae:.2f} min\n"
            f"MSE: {mse:.2f}\n"
            f"RMSE: {rmse:.2f} min ({seconds_to_hms(rmse * 60)})\n"
            f"R²: {r2:.3f}\n"
            f"{equation}\n"
            f"N$_{{train}}$: {len(X_train)}\n"
            f"N$_{{test}}$: {lin_reg_params['num_test']}\n"
            f"{"-"*30}\n"
            f"{fit_text}")
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', ec='black', fc='white'))
    #
    ax.set_xlabel('Distance (km)' if not fit_params['Normalize'] else 'Normalized Distance', fontsize=14)
    ax.set_ylabel('Time (minutes)' if not fit_params['Normalize'] else 'Normalized Time', fontsize=14)
    ax.set_title(f'Linear regression for distance vs time for {tour_name}',fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    ax.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"{PLOT_PATHS['linear']}{tour_name}_Linear_Regression_{itt_txt}_{norm_txt}.png", bbox_inches='tight')
    plt.show()
    #-------------------

    output_path = f"{OUTPUT_PATHS['output']}{tour_name}_multivariate_regression_summary.txt"
    with open(output_path, "w") as f:
        f.write("--- Regression Summary ---\n")
        f.write(f"Features used: {feature_list}\n")
        f.write(f"R² score: {r2:.4f}\n")
        f.write(f"RMSE: {rmse:.2f} min\n")
        f.write(f"MAE: {mae:.2f} min\n")
        f.write(f"MSE: {mse:.2f}\n")
        f.write(f"MAPE: {mape:.2f}\n")
        f.write(f"Training samples: {len('X_train')}\n")
        f.write(f"Test samples: {len('X_test')}\n\n")
        f.write("--- Regression Equation ---\n")
        f.write(equation + "\n")
