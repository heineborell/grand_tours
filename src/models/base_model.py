from abc import ABC, abstractmethod

from sklearn.metrics import mean_absolute_percentage_error, root_mean_squared_error


class BaseModel(ABC):
    def __init__(self):
        self.model = None

    @abstractmethod
    def train(self, X_train, y_train):
        pass

    @abstractmethod
    def predict(self, X_test):
        pass

    def evaluate(self, X_test, y_test, only_predict):
        y_pred = self.predict(X_test)
        if not only_predict:
            return (root_mean_squared_error(y_test, y_pred), mean_absolute_percentage_error(y_test, y_pred))
        else:
            return y_pred, y_test.to_list()
