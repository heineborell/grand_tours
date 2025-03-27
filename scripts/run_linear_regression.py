# Project/scripts/run_linear_regression.py

import pandas as pd
from src.config import DB_PATHS, get_tour_attributes
from src.data.load_data import fetch_data, apply_outlier_filter, fetch_distance_and_time_data
from src.data.preprocess import preprocess_regression_data
from src.models.gt_linear import train_linear_regression
from src.plotting.plot_linear_regression import summarize_and_plot_linear_regression

def linear_regression():
    ##-----------------------
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results_plus"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    #
    include_itt = True
    normalize = False
    # time_group = 1
    fit_params = {"Include ITT": include_itt, "Normalize": normalize}
    ##-----------------------
    #
    print("\nFetching data...")
    df = fetch_data(gt_db_path, table_name,fit_params)
    # df = fetch_distance_and_time_data(gt_db_path, table_name,fit_params)
    rows, cols = df.shape
    print(f"After fetch:  rows= {rows}, columns= {cols}")

    print("\nFiltering out using outliers.csv...")
    outlier_path = "data/outliers.csv"
    df = apply_outlier_filter(df, outlier_path, table_name)
    rows, cols = df.shape
    print(f"After outlier filter:  rows= {rows}, columns= {cols}")
    #
    print("\nPreprocessing data...")
    X, y, itt_mask = preprocess_regression_data(df, fit_params)
    #
    print(f"After preprocess  len(X)= {len(X)}, len(y)= {len(y)}")

    print("\nTraining linear regerssion model...")
    lin_reg_params = train_linear_regression(X, y, itt_mask)
    #
    print("\nPlotting and summarizing model...")
    summarize_and_plot_linear_regression(table_name, fit_params, lin_reg_params)
    #
    print("\nLinear regression completed successfully.\n")
