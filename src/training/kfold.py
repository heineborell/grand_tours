import numpy as np
import pandas as pd
from rich import print
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

        # loop through all models
        for j, model in enumerate(models):
            trainer = Trainer(model, config["models"][model]["hyperparameters"])
            trainer.train(X_train_train[config["features"]], X_train_train[config["target"]])
            score = trainer.evaluate(X_holdout[config["features"]], X_holdout[config["target"]])

            # record rmse
            cv_rmses[i, j] = score[0]
            # record mape
            cv_mape[i, j] = score[1]

    df = pd.DataFrame(
        {
            "Model": models,
            "cv_rmse": np.mean(cv_rmses, axis=0),
            "cv_mape": np.mean(cv_mape, axis=0),
            "x_tr_tr_len": [xtrain_len] * len(models),
            "features": len(models) * [config["features"]],
        }
    )
    print(df)
