import pandas as pd
import numpy as np
import seaborn as sns
##
from src.config import get_tour_attributes
from src.config import PLOT_PATHS
from src.utils.time_utils import seconds_to_hms
##
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib import style
plt.style.use('bmh')
##

def plot_poly_regression(table_name, fit_params, poly_reg_params):
    """
    Plot the polynomial regression fit with actual training data.
    Input:
        poly_reg_params (dict): Dictionary containing model, training data, and error metrics.
    """

    tour_attributes = get_tour_attributes()
    tour_color = tour_attributes[table_name]["color"]
    tour_name = tour_attributes[table_name]["name"]
    ##
    itt_txt = "ITT_T" if fit_params['Include ITT'] else "ITT_F"
    norm_txt = "N_T" if fit_params['Normalize']  else "N_F"
    Rank_txt = f"Rnk_{fit_params['Rank cutoff']}"
    #
    itt_indices = poly_reg_params['ITT_indices']
    #-------------------
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.scatter(poly_reg_params['X_train'][:, 1], poly_reg_params['y_train'], color=tour_color, edgecolors='k', s=7, label=f"{tour_name} Data")
    if len(itt_indices) > 0:
        ax.plot(poly_reg_params['X_train'][itt_indices, 1], poly_reg_params['y_train'][itt_indices], marker='o',  mfc='b', mec='k', ms=4, ls='None', label=f"{tour_name} ITT Data")
    #
    ax.set_xlabel('Distance (km)' if not fit_params['Normalize'] else 'Normalized Distance', fontsize=14)
    ax.set_ylabel('Time (minutes)' if not fit_params['Normalize'] else 'Normalized Time', fontsize=14)
    ax.set_title(f'Polynomial regression for distance vs time for {tour_name}',fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    ax.legend(fontsize=12)
    fig.tight_layout()
    plt.savefig(f"Plots/Test/{tour_name}_Poly_Reg_3_{itt_txt}_{norm_txt}_{Rank_txt}.png", bbox_inches='tight')
    plt.show()
    #-------------------

def main():
    ##-----------------------
    ## control parameters
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results_plus"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    include_itt = True
    normalize = False
    rank_cutoff = 10
    # winners_only = True
    #-----------------------
    fit_params = {"Include ITT": include_itt, "Normalize": normalize, "Rank cutoff": rank_cutoff }

    df = fetch_data(gt_db_path, table_name, fit_params)
    X, y, itt_mask = preprocess_regression_data(df, fit_params)
    poly_reg_params = train_polynomial_regression(X, y,itt_mask)
    plot_poly_regression(table_name, fit_params, poly_reg_params)
