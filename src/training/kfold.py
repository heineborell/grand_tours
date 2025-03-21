import numpy as np
from rich import print

from training.trainer import Trainer


def kfold_split_train(X_train, config, features, target, kfold):
    # make empty rmse holder
    models = list(config["models"].keys())
    cv_rmses = np.zeros((5, len(models)))
    # loop through all splits
    for i, (train_index, test_index) in enumerate(kfold.split(X_train)):
        ## get train and holdout sets
        print(f"[bold red] Kfold no:{i + 1} [/bold red]")
        X_train_train = X_train.iloc[train_index]
        X_holdout = X_train.iloc[test_index]

        # loop through all models
        for j, model in enumerate(models):
            print(f"------------------\n {model}")
            trainer = Trainer(model, config["models"][model]["hyperparameters"])
            trainer.train(X_train_train[features], X_train_train[target])
            score = trainer.evaluate(X_holdout[features], X_holdout[target])
            print(f"RMSE: {score}")

            # record mse
            cv_rmses[i, j] = score

    print(cv_rmses)
