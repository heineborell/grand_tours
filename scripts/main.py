from pathlib import Path

from rich import print
from sklearn.model_selection import train_test_split

from data.data_loader import load_data
from training.gridsearch import json_writer, param_search

if __name__ == "__main__":
    config_path = Path("config/config.json")
    db_path = Path("config/db_path.json")

    # # Load data
    data = load_data("tdf", 2024, db_path, training=True)
    print(f"Dataframe columns:{list(data.columns)}")

    # Splitting train and test
    X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

    params = param_search(X_train, config_path)
    json_writer(config_path, params)

    # kfold = KFold(n_splits=5, shuffle=True, random_state=31)
    # kfold_split_train(X_train, config_path, kfold)
