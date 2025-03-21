import yaml

from data.data_loader import load_data

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)


print(config)
# # Load data
data = load_data("tdf", 2024, training=True)
print(data)
X, y = (
    data.drop(["strava_id", "activity_id", "avg_power", "tour_year", "time", "ride_day", "race_start_day"], axis=1),
    data["time"],
)

print(X, y)

# # Train model
# trainer = Trainer(config["model"])
# trainer.train(X, y)
#
# # Evaluate
# score = trainer.evaluate(X, y)
# print(f"Model Performance: {score}")
