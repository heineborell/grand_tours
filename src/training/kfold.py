import json

import numpy as np
import pandas as pd
from rich import print
from tqdm import tqdm

from training.trainer import Trainer


def kfold_split_train(X_train, config_path, kfold):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    # create empty dataframe
    df = pd.DataFrame(columns=["Model", "cv_rmse", "features", "x_train_length"])
    # make empty rmse holder
    models = list(config["models"].keys())
    cv_rmses = np.zeros((5, len(models)))
    # loop through all splits
    for i, (train_index, test_index) in enumerate(
        tqdm(kfold.split(X_train), total=kfold.n_splits, desc="Processing Kfold")
    ):
        ## get train and holdout sets
        X_train_train = X_train.iloc[train_index]
        X_holdout = X_train.iloc[test_index]

        # loop through all models
        for j, model in enumerate(models):
            trainer = Trainer(model, config["models"][model]["hyperparameters"])
            trainer.train(X_train_train[config["features"]], X_train_train[config["target"]])
            score = trainer.evaluate(X_holdout[config["features"]], X_holdout[config["target"]])

            # record rmse
            cv_rmses[i, j] = score

    df = pd.DataFrame(
        {"Model": models, "cv_rmse": np.mean(cv_rmses, axis=0), "features": len(models) * [config["features"]]}
    )
    print(df)
