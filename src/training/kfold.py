import numpy as np
import pandas as pd
from rich import print
from sklearn.metrics import mean_absolute_percentage_error, root_mean_squared_error
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from training.trainer import Trainer


def kfold_split_train(X_train, config, kfold):
    # make empty rmse holder
    n_splits = kfold.n_splits
    models = list(config["models"].keys())
    cv_rmses = np.zeros((n_splits, len(models)))
    cv_mape = np.zeros((n_splits, len(models)))

    # loop through all splits
    for i, (train_index, test_index) in enumerate(
        tqdm(kfold.split(X_train), total=kfold.n_splits, desc="Processing Kfold")
    ):
        ## get train and holdout sets
        X_train_train = X_train.iloc[train_index]
        X_holdout = X_train.iloc[test_index]
        xtrain_len = len(X_train_train)
        xholdout_len = len(X_holdout)

        # Scale features within the fold
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_train[config["features"]])
        X_holdout_scaled = scaler.transform(X_holdout[config["features"]])

        y_train = X_train_train[config["target"]]
        y_holdout = X_holdout[config["target"]]

        # loop through all models
        for j, model in enumerate(models):
            trainer = Trainer(model, config["models"][model]["hyperparameters"])
            trainer.train(X_train_scaled, y_train)
            score = trainer.evaluate(X_holdout_scaled, y_holdout)

            # record rmse
            cv_rmses[i, j] = score[0]
            # record mape
            cv_mape[i, j] = score[1]

    df = pd.DataFrame(
        {
            "strava_id": [config["strava_id"]] * len(models),
            "Model": models,
            "cv_rmse": np.mean(cv_rmses, axis=0),
            "cv_mape": np.mean(cv_mape, axis=0),
            "x_tr_tr_len": [xtrain_len] * len(models),
            "x_holdout_len": [xholdout_len] * len(models),
            "features": len(models) * [config["features"]],
        }
    )
    return df


def tester(X_train, X_test, config):
    # make empty rmse holder
    models = list(config["models"].keys())
    test_rmses = np.zeros(len(models))
    test_mape = np.zeros(len(models))

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train[config["features"]])
    X_test_scaled = scaler.transform(X_test[config["features"]])
    xtrain_len = len(X_train_scaled)
    xtest_len = len(X_test_scaled)

    y_train = X_train[config["target"]]
    y_test = X_test[config["target"]]

    # loop through all models
    for j, model in enumerate(tqdm(models, total=len(models), desc="Processing Train-Test")):
        trainer = Trainer(model, config["models"][model]["hyperparameters"])
        trainer.train(X_train_scaled, y_train)
        score = trainer.evaluate(X_test_scaled, y_test)

        # record rmse
        test_rmses[j] = score[0]
        # record mape
        test_mape[j] = score[1]

    df = pd.DataFrame(
        {
            "strava_id": [config["strava_id"]] * len(models),
            "Model": models,
            "test_rmse": test_rmses,
            "test_mape": test_mape,
            "x_tr_len": [xtrain_len] * len(models),
            "x_test_len": [xtest_len] * len(models),
            "features": len(models) * [config["features"]],
        }
    )
    print(df)


def segment_tester(X_train, X_test, config):
    # load models and make empty rmse holder
    models = list(config["models"].keys())
    test_rmses = np.zeros(len(models))
    test_mape = np.zeros(len(models))

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train[config["features"]])
    y_train = X_train[config["target"]]
    xtrain_len = len(X_train_scaled)
    xtest_len = len(X_test)

    df_stage_len = X_test.drop_duplicates(subset=["stage"])[
        ["strava_id", "activity_id_y", "stage", "total_distance", "dist_total_segments"]
    ]
    df_stage_len["coverage"] = df_stage_len["dist_total_segments"] / df_stage_len["total_distance"]
    print(df_stage_len)

    # loop through all models
    for j, model in enumerate(tqdm(models, total=len(models), desc="Processing Train-Test")):
        trainer = Trainer(model, config["models"][model]["hyperparameters"])
        trainer.train(X_train_scaled, y_train)
        stage_list = X_test["stage"].unique()

        predict_result = []
        test_result = []
        # For each stage predict the segment times
        for stage in stage_list:
            X_test_stage = X_test.loc[X_test["stage"] == stage]
            X_test_stage_scaled = scaler.transform(X_test_stage[config["features"]])
            y_test = X_test_stage[config["target"]]

            # for each stage predict the times for all segments then
            # sum all segments and find the stage time also sum the
            # real times and append them in a list
            predictions = trainer.evaluate(X_test_stage_scaled, y_test, only_predict=True)
            predict_result.append(sum(predictions[0]))
            test_result.append(sum(predictions[1]))

        # # record rmse
        test_rmses[j] = root_mean_squared_error(predict_result, test_result)
        # # record mape
        test_mape[j] = mean_absolute_percentage_error(predict_result, test_result)

    df = pd.DataFrame(
        {
            "strava_id": [config["strava_id"]] * len(models),
            "name": X_train["rider_name"][0],
            "Model": models,
            "test_rmse": test_rmses,
            "test_mape": test_mape,
            "x_tr_len": [xtrain_len] * len(models),
            "x_test_len": [xtest_len] * len(models),
            "features": len(models) * [config["features"]],
        }
    )
    return df
