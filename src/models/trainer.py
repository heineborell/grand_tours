from rich import print as print
from sklearn.model_selection import train_test_split

from data.processing import create_features


def train_model(athlete_id, dataframe):
    print("started training")
    data = create_features(dataframe)
    data = data.loc[data["strava_id"] == athlete_id]

    X = data[["distance", "elevation", "time_delta"]]
    y = data["time"]  # Predicting power output

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # pipeline = Pipeline(
    #     [("scaler", StandardScaler()), ("model", RandomForestRegressor(n_estimators=100, random_state=42))]
    # )
    #
    # pipeline.fit(X_train, y_train)
    #
    # with open("models/model.pkl", "wb") as f:
    #     pickle.dump(pipeline, f)
    return X_train
