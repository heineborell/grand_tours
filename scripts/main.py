import yaml
from rich import print
from sklearn.model_selection import train_test_split

from data.data_loader import load_data
from training.gridsearch import param_search

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
models = list(config["models"].keys())
#
param_search(X_train, config, features, target)
# kfold = KFold(n_splits=5, shuffle=True, random_state=31)
# kfold_split_train(X_train, config, features, target, kfold)
