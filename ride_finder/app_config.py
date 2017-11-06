import os

APP_HOME = os.path.dirname(os.path.abspath(__file__))
STRAVA_DATA_PATH = os.path.join(APP_HOME, "strava", "stored_data")
DATASETS_PATH = os.path.join(APP_HOME, "mapbox", "datasets")