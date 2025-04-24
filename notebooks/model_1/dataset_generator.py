import data_compiler
from sklearn.model_selection import train_test_split

data_2020_2023 = data_compiler.generate_race_data_with_training_features(range(2020,2024))
data_2024 = data_compiler.generate_race_data_with_training_features(2024)

data_train, data_test = train_test_split(data_2020_2023, train_size=0.8, random_state=42, shuffle=True)

data_2020_2023.to_csv(r'data/2020-2023-combined-race-training-data.csv', index=False)
data_2024.to_csv(r'data/2024-combined-race-training-data.csv', index=False)

data_train.to_csv('data/model-training-set.csv', index=False)
data_test.to_csv('data/model-testing-set.csv', index=False)

