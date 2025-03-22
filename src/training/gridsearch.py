import concurrent.futures
import json
import time

from rich import print
from sklearn.model_selection import GridSearchCV

from training.trainer import Trainer


def param_search(X_train, config_path):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())
    models = list(config["models"].keys())
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for model in models:
            # Submit each task with a slight delay
            futures[executor.submit(gridder, model, X_train, config_path)] = model
            time.sleep(3)  # Adjust the sleep time as needed

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"[turquoise2] Task result:{result} [/turquoise2]")
            except Exception as e:
                task_id = futures[future]
                print(f"[bright red] Task {task_id} generated an exception: {e} [/bright red]")


def gridder(model, X_train, config_path):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())
    print(f"[bold blue] {model} [/bold blue]")
    # Define the parameter grid to search over
    param_grid = config["models"][model]["param_grid"]
    if not param_grid:
        print("[bold red] No hyperparameter [/bold red]")
        return

    # Create a GridSearchCV object
    model_bare = Trainer(model, hyperparams=None)
    grid_search = GridSearchCV(
        estimator=model_bare._get_model(model, hyperparams=None).model,
        param_grid=param_grid,
        cv=5,
        scoring="neg_root_mean_squared_error",
    )

    # Fit the grid search to the training data
    grid_search.fit(X_train[config["features"]], X_train[config["target"]])

    # Get the best parameters
    best_params_SVR = grid_search.best_params_
    json_writer(best_params_SVR, model, config_path)
    return f"Best Parameters: {best_params_SVR}"


def json_writer(best_params, model, config_path):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    config["models"][model]["hyperparameters"] = best_params

    json_data = json.dumps(config, indent=4)
    with open(
        config_path,
        "w",
    ) as f:
        f.write(json_data)
