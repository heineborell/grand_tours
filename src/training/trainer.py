from models.linear_regression import LinearRegressionModel
from models.linearsvr import LinearSVRModel
from models.random_forest import RandomForestRegressorModel
from models.xgboost import XgBoostModel


class Trainer:
    def __init__(self, model_name, hyperparams=None):
        self.model = self._get_model(model_name, hyperparams)

    def _get_model(self, model_name, hyperparams):
        if hyperparams is None:
            hyperparams = {}  # Default to an empty dictionary

        if hyperparams is None and model_name == "xgboost":
            hyperparams = {"tree_method": "gpu_hist"}  # Default to an empty dictionary

        if model_name == "linear_regression":
            return LinearRegressionModel()
        elif model_name == "random_forest_regressor":
            return RandomForestRegressorModel(hyperparams)
        elif model_name == "xgboost":
            return XgBoostModel(hyperparams)
        elif model_name == "linearsvr":
            return LinearSVRModel(hyperparams)
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def train(self, X_train, y_train):
        self.model.train(X_train, y_train)

    def evaluate(self, X_test, y_test, only_predict=False):
        return self.model.evaluate(X_test, y_test, only_predict)
