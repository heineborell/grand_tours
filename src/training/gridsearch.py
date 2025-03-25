import concurrent.futures
import json
import time

from rich import print
from sklearn.model_selection import GridSearchCV
from tqdm import tqdm  # Import tqdm for progress bar

from training.trainer import Trainer


def param_search(X_train, config_path):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())
    models = list(config["models"].keys())

    # Dictionary to track progress bars for each model
    thread_pbars = {}
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        # Submit tasks and add them to futures
        for i, model in enumerate(models):
            # Create a progress bar for each model
            thread_pbars[model] = tqdm(total=100, desc=f"{model}", position=i + 1, leave=False)
            futures[executor.submit(gridder, model, X_train, config_path, thread_pbars[model])] = model
            time.sleep(1)  # Adjust the sleep time as needed

        # Track the progress of tasks using tqdm for total progress
        with tqdm(total=len(futures), desc="Processing gridsearch", unit="task", position=0) as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    task_id = futures[future]
                    result = future.result()
                    results[task_id] = result
                    pbar.set_postfix(task=task_id)  # Update progress bar with current task
                except Exception as e:
                    task_id = futures[future]
                    print(f"[bright red] Task {task_id} generated an exception: {e} [/bright red]")
                finally:
                    time.sleep(0.5)
                    pbar.update(1)  # Move the progress bar forward
                    # Close the individual progress bar
                    thread_pbars[task_id].close()

    return results  # Return all results after completion


def gridder(model, X_train, config_path, pbar):
    # Load config
    with open(config_path, "r") as f:
        config = json.loads(f.read())
    # Define the parameter grid to search over
    param_grid = config["models"][model]["param_grid"]
    if not param_grid:
        print(f"[bold red] No hyperparameter for {model} [/bold red]")
        pbar.update(100)  # Complete the progress bar
        return None

    else:
        # Create a GridSearchCV object
        model_bare = Trainer(model, hyperparams=None)
        grid_search = GridSearchCV(
            estimator=model_bare._get_model(model, hyperparams=None).model,
            param_grid=param_grid,
            cv=5,
            scoring="neg_root_mean_squared_error",
        )

        # Update progress to show we're starting the fit
        pbar.update(10)
        pbar.refresh()
        # Fit the grid search to the training data
        grid_search.fit(X_train[config["features"]], X_train[config["target"]])

        # Update progress to show we're done fitting
        pbar.update(80)

        # Get the best parameters
        best_params = grid_search.best_params_

        # Complete the progress
        pbar.update(10)

        return best_params


def json_writer(config_path, best_params, rider_id=None):
    # Load base config again
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    tour = config["tour"]
    year = config["year"]

    # change to the parameters you found from gridsearch
    for model in best_params:
        config["models"][model]["hyperparameters"] = best_params[model]

    # delete parameter grid search data
    json_cleaner(config)
    json_data = json.dumps(config, indent=4)
    print(json_data)

    # save to the new json file (dropped the hyperparameter search range) if
    # it is training it saves _training if its race it save as in else
    if config["training"] and rider_id is None:
        with open(
            config_path.parent / f"config_{tour}_training-{year}_all.json",
            "w",
        ) as f:
            f.write(json_data)
    elif not config["training"] and rider_id is None:
        with open(
            config_path.parent / f"config_{tour}-{year}_all.json",
            "w",
        ) as f:
            f.write(json_data)


def json_cleaner(json_data):
    for model in json_data["models"].keys():
        del json_data["models"][model]["param_grid"]
