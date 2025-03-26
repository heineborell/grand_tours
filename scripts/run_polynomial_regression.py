# Project/scripts/run_polynomial_regression.py

from src.config import DB_PATHS, get_tour_attributes
from src.data.load_data import fetch_data
from src.data.preprocess import preprocess_regression_data
from src.models.gt_polynomial import train_polynomial_regression
from src.plotting.plot_polynomial_regression import plot_poly_regression

def polynomial_regression():
    # table_name = "giro_results"
    # db_path = DB_PATHS[table_name]
    # fit_params = {"Include ITT": True, "Normalize": False}
    
    # df = fetch_data(db_path, table_name, fit_params)
    # df = preprocess_data(df)
    # model = train_linear_regression(df)
    # plot_regression(model, df)

    ##-----------------------
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    include_itt = True
    normalize = False
    # time_group = 1
    fit_params = {"Include ITT": include_itt, "Normalize": normalize}
    ##-----------------------
    #
    print("\nFetching data...")
    # df = fetch_data(gt_db_path, table_name,fit_params)
    df = fetch_distance_and_time_data(gt_db_path, table_name,fit_params)
    #
    print("\nFiltering out using outliers.csv...")
    outlier_path = "data/outliers.csv"
    df = apply_outlier_filter(df, outlier_path,table_name)
    #
    print("\nPreprocessing data...")
    X, y, itt_mask = preprocess_regression_data(df, fit_params)
    #
    print("\nTraining polynomial regerssion model...")
    lin_reg_params= train_polynomial_regression(X, y, itt_mask)
    #
    print("\nPlotting and summarizing model...")
    plot_poly_regression(table_name,fit_params,lin_reg_params)
    #
    print("\nPolynomial regression completed successfully.\n")