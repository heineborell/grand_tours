import xgboost as xgb

from models.base_model import BaseModel


class XgBoostModel(BaseModel):
    def __init__(self, hyperparams):
        super().__init__()
        self.model = xgb.XGBRegressor(**hyperparams)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)
