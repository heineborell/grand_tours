from pathlib import Path

from rich import print as print

from data.data_loader import config_loader, load_data
from data.processing import fetch_riders

import pandas as pd
import numpy as np

def generate_race_data_with_training_features(years, tours=['giro', 'tdf'], minimum_training_sessions=10):
    '''Generates a table of data from the available races in the tours list for the given years, with added features 
    engineered from the training database corresponding to the tour and year'''

    # Navigate up to the project root
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    CONFIG_PATH = PROJECT_ROOT / "config/base_config.json"
    DB_PATH = PROJECT_ROOT / "config/db_path.json"

    try:
        years = list(years)
    except TypeError:
        years = [years]

    race_data_with_training_features = []
    for year in years:
        for tour in tours:
            #We don't have training data for giro 2020
            if (year == 2020 and tour == 'giro'): 
                pass

            else:
                #load the data
                print(tour + ' ' + str(year))
                race_data = load_data(tour, year, db_path=DB_PATH, training=False, segment_data=False)
                print(tour + ' ' + str(year))
                training_data = load_data(tour, year, db_path=DB_PATH, training=True, segment_data=False)

                #adds an indicator variable for individual time trials. 
                race_data['time_trial'] = 1*race_data.stage.apply(lambda x: "ITT" in x)

                #extracts only the stage number from the stage column.
                race_data['stage'] = race_data.stage.apply(lambda x: x.split(" ")[1])
                
                race_data['time_delta'] = -race_data['time_delta']

                #add a count of training sessions 
                session_counts = training_data['strava_id'].value_counts()
                race_data = race_data.merge(session_counts, on='strava_id', how='left')
                race_data.rename(columns={'count': 'no_sessions'}, inplace=True)

                #keep only those athletes with at least minimum_sessions number of training rides
                race_data = race_data[race_data['no_sessions'] >= minimum_training_sessions]

                #compute average speed for a given ride and convert to km/h for interpretability
                training_data['average_speed'] = training_data.distance/training_data.time * 3600

                #Compute elevation vs distance metric
                training_data['EVD'] = \
                    100*training_data['elevation']/(training_data['distance']*1000 + training_data['elevation']) 
                
                #aggregate the training data
                mean_training_data = training_data[['strava_id', 'distance', 'average_speed', 'elevation', 'EVD']]\
                                        .groupby(by='strava_id').mean()
                mean_training_data.rename(columns={'distance': 'mean_train_dist', 'average_speed': 'mean_train_avg_speed', 
                                                   'elevation': 'mean_train_elevation', 'EVD': 'mean_train_EVD'}, inplace=True)
                
                #merge aggregate training data with race data
                race_data = race_data.merge(mean_training_data, on='strava_id', how='left')

                #store the dataframes in a list
                race_data_with_training_features.append(race_data)
    
    #concatenate the data frames in the list
    race_data_with_training_features = pd.concat(race_data_with_training_features).reset_index(drop=True)
    return race_data_with_training_features
