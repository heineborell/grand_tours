from rich import print

from models.linear_regression import LinearRegressionModel
from models.random_forest import RandomForestRegressorModel
from models.xgboost import XgBoostModel


class Trainer:
    def __init__(self, model_name, hyperparams):
        self.model = self._get_model(model_name, hyperparams)
        print(f"Loaded {self.model.model}")

    def _get_model(self, model_name, hyperparams):
        if model_name == "linear_regression":
            return LinearRegressionModel()
        elif model_name == "random_forest_regressor":
            return RandomForestRegressorModel(hyperparams)
        elif model_name == "xgboost":
            return XgBoostModel(hyperparams)
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def train(self, X_train, y_train):
        print(f"[bold green] Length of X_train: [/bold green]{len(X_train)}")
        self.model.train(X_train, y_train)
        print("[bold blue] Training finished [/bold blue]")

    def evaluate(self, X_test, y_test):
        return self.model.evaluate(X_test, y_test)
