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
X, y = (
    data.drop(["strava_id", "activity_id", "avg_power", "tour_year", "time", "ride_day", "race_start_day"], axis=1),
    data["time"],
)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# # Train model
trainer = Trainer("linear_regression")
trainer.train(X_train, y_train)
# # Evaluate
score = trainer.evaluate(X_test, y_test)
print(f"{trainer.model.model} Performance: {score}")
