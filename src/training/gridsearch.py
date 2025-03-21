from rich import print
from sklearn.model_selection import GridSearchCV

from training.trainer import Trainer


def param_search(X_train, config, features, target):
    models = list(config["models"].keys())
    for i, model in enumerate(models):
        print(f"[bold blue] {model} [/bold blue]")
        # Define the parameter grid to search over
        param_grid = config["models"][model]["param_grid"]
        if not param_grid:
            print("[bold red] No hyperparameter [/bold red]")
            continue

        # Create a GridSearchCV object
        model_bare = Trainer(model, hyperparams=None)
        grid_search = GridSearchCV(
            estimator=model_bare._get_model(model, hyperparams=None).model,
            param_grid=param_grid,
            cv=5,
            scoring="neg_root_mean_squared_error",
        )

        # Fit the grid search to the training data
        grid_search.fit(X_train[features], X_train[target])

        # Get the best parameters
        best_params_SVR = grid_search.best_params_
        print(f"Best Parameters: {best_params_SVR}")

    # def segment_scraper(self):
    #     print(self.activity_whole_list)
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
    #         futures = {}
    #         for i, j in enumerate(self.activity_whole_list):
    #             # Submit each task with a slight delay
    #             futures[executor.submit(self._activity_data_getter, i + 1, j)] = j
    #             time.sleep(10)  # Adjust the sleep time as needed
    #
    #         for future in concurrent.futures.as_completed(futures):
    #             try:
    #                 result = future.result()
    #                 rprint(f"[turquoise2] Task result:{result} [/turquoise2]")
    #             except Exception as e:
    #                 task_id = futures[future]
    #                 rprint(f"[bright red] Task {task_id} generated an exception: {e} [/bright red]")
    #
    #
