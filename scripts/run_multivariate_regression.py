# Project/scripts/run_multivariate_regression.py

from src.config import DB_PATHS, get_tour_attributes
from src.data.load_data import fetch_data
from src.utils.time_utils import convert_time_to_seconds
from src.data.preprocess import preprocess_regression_data
from src.models.gt_multivariate import train_multivariate_regression
from src.plotting.plot_multivariate_regression import summarize_and_plot_multivariate_regression

def multivariate_regression():
    # table_name = "giro_results"
    # db_path = DB_PATHS[table_name]
    # fit_params = {"Include ITT": True, "Normalize": False}
    # df = fetch_data(db_path, table_name, fit_params)
    # df = preprocess_data(df)
    # model = train_multivariate_regression(df)
    # plot_regression(model, df)

    # ##-----------------------
    # ## control parameters
    # gt_db_path = "data/grand_tours.db"
    # table_name = "giro_results"
    # # table_name = "tdf_results"
    # # table_name = "vuelta_results"
    # include_itt = True
    # normalize = False
    # # time_group = 1
    # ##-----------------------
    # fit_params = {"Include ITT": include_itt, "Normalize": normalize, "Winners only": winners_only}

    # df = fetch_distance_and_time_data(gt_db_path, table_name,fit_params)
    # X, y, itt_mask = preprocess_regression_data(df, fit_params)
    # lin_reg_params= train_multivariate_regression(X, y, itt_mask)
    # plot_linear_regression(table_name,fit_params,lin_reg_params)
    # ###

    ##-----------------------
    ## control parameters
    gt_db_path = "data/grand_tours.db"
    table_name = "giro_results_plus"
    # table_name = "tdf_results"
    # table_name = "vuelta_results"
    include_itt = True
    normalize = False
    blacklist_file_path = "outliers.csv"
    ##-----------------------
    fit_params = {"Include ITT": include_itt, "Normalize": normalize}
    # features
    # features = ['distance']
    features = ['distance', 'stage_num']
    # features = ['distance', 'stage_num', 'vertical_meters']
    # features = ['distance', 'stage_num', 'vertical_meters', 'avg_temperature']
    # features = ['distance', 'stage_num', 'vertical_meters', 'avg_temperature', 'startlist_quality']

    print("\nFetching data...")
    df = fetch_data(gt_db_path, table_name, include_itt)
    # df = fetch_distance_and_time_data(gt_db_path, table_name,fit_params)
    #
    print("\nFiltering out using outliers.csv...")
    outlier_path = "data/outliers.csv"
    df = apply_outlier_filter(df, outlier_path, table_name)
    #
    print("\nPreprocessing data...")
    X, y, itt_mask = preprocess_multivariate_regression_data(df, fit_params, features)
    #
    print("\nTraining regerssion model...")
    regression_result = train_multivariate_regression(X, y, itt_mask)
    #
    print("\nPlotting and summarizing model...")
    summarize_and_plot_predictions(regression_result, table_name, features)
    #
    print("\nMultivariate regression completed successfully.\n")
