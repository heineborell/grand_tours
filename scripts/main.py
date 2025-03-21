import yaml
from rich import print
from sklearn.model_selection import train_test_split

from data.data_loader import load_data
from training.trainer import Trainer

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)


# # Load data
data = load_data("tdf", 2024, training=True)
print(data.columns)

# Splitting train and test
X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)
features = ["distance", "elevation", "time_delta"]
target = "time"
models = ["linear_regression", "random_forest_regressor", "xgboost"]

for model in models:
    trainer = Trainer(model, config["models"][model]["hyperparameters"])
    trainer.train(X_train[features], X_train[target])
    score = trainer.evaluate(X_test[features], X_test[target])
    print(f"{trainer.model.model} RMSE: {score}")
