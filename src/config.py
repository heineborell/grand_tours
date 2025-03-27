# src/config.py

import numpy as np

PLOT_PATHS = {
    "linear": "plots/linear_reg/",
    "poly": "plots/polynomial_reg/",
    "multi": "plots/multivariate_reg/",
    "gt_eda": "plots/grand_tours_eda/"
}

OUTPUT_PATHS = {
    "output": "output/model_logs/",
}

DB_PATHS = {
    "grand_tours":"data/grand_tours.db",
    "segment_details": "data/segment_details.db",
    "strava_segments": "data/strava_segments.db",
    "training": "data/training"
}

def get_tour_attributes():
    tour_attributes = {
        "tdf_results": {"name": "tdf", "FullName": "Tour de France", "color": "yellow","xVals": np.linspace(1905, 2025,25, dtype=int)},
        "tdf_results_plus": {"name": "tdf", "FullName": "Tour de France", "color": "yellow","xVals": np.linspace(1905, 2025,25, dtype=int)},
        "giro_results": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink","xVals": np.linspace(1905, 2025, 25, dtype=int)},
        "giro_results_plus": {"name": "giro", "FullName": "Giro d'Italia", "color": "pink","xVals": np.linspace(1905, 2025, 25, dtype=int)},
        "vuelta_results": {"name": "vuelta", "FullName": "Vuelta a España","color": "red","xVals": np.linspace(1930, 2030, 11, dtype=int)},
        "vuelta_results_plus": {"name": "vuelta", "FullName": "Vuelta a España","color": "red","xVals": np.linspace(1930, 2030, 11, dtype=int)}
    }
    return tour_attributes
