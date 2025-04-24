'''This script uses the function in data_compiler to generate dataframes for 2020-2023 and 2024,
and puts them in csv files in the data folder for model 1.'''

import data_compiler
from sklearn.model_selection import train_test_split
from pathlib import Path

data_2020_2023 = data_compiler.generate_race_data_with_training_features(range(2020,2024))
data_2024 = data_compiler.generate_race_data_with_training_features(2024)

data_train, data_test = train_test_split(data_2020_2023, train_size=0.8, random_state=42, shuffle=True)

#Get current directory
current_directory = Path(__file__).resolve().parent
DATA_PATH = current_directory / 'data'

data_2020_2023_path = DATA_PATH / '2020-2023-combined-race-training-data.csv'
data_2024_path = DATA_PATH / '2024-combined-race-training-data.csv'
training_path = DATA_PATH / 'model-training-set.csv'
test_path = DATA_PATH / 'model-testing-set.csv'

data_2020_2023.to_csv(data_2020_2023_path, index=False)
data_2024.to_csv(data_2024_path, index=False)

data_train.to_csv(training_path, index=False)
data_test.to_csv(test_path, index=False)

print("Datasets generated successfully!")