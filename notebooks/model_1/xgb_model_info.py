features = [
            'distance',
            'elevation',
            #'stage',
            #'year',
            'profile_score',
            'startlist_quality',
            'time_delta',
            #'elevation_ratio',
            'time_trial',
            #'no_sessions',
            'mean_train_dist',
            'mean_train_avg_speed',
            'mean_train_elevation',
            'mean_train_EVD'
            ]
target = 'time'

best_params = {'learning_rate': 0.1,
                'max_depth': 5,
                'n_estimators': 1000,
                'reg_alpha': 0.1,
                'reg_lambda': 5
                }