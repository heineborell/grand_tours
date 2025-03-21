from rich import print

from models.linear_regression import LinearRegressionModel


class Trainer:
    def __init__(self, model_name):
        self.model = self._get_model(model_name)
        print(f"Loaded {self.model}")

    def _get_model(self, model_name):
        if model_name == "linear_regression":
            return LinearRegressionModel()
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def train(self, X_train, y_train):
        self.model.train(X_train, y_train)
        print("Training finished")

    def evaluate(self, X_test, y_test):
        return self.model.evaluate(X_test, y_test)
