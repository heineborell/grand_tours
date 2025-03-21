from sklearn.svm import SVR

from models.base_model import BaseModel


class LinearSVRModel(BaseModel):
    def __init__(self, hyperparams):
        super().__init__()
        self.model = SVR(**hyperparams)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)
