import os
import json
from strava import transformer
import uuid
from ride_finder.strava.api import StravaApi
from ride_finder.app_config import DATASETS_PATH, STRAVA_DATA_PATH
from ride_finder import utils

def populate_athlete_data(store=True, prefix=None):

	# Default api for my user
	api = StravaApi()
	activities = api.fetch_activities()
	if store:
		activity_types = [StravaApi.ACTIVITY_RIDE,
			StravaApi.ACTIVITY_RUN,
			StravaApi.ACTIVITY_SWIM]

		# Store them all with the same prefix so it's known they are from the
		# same run
		prefix = uuid.uuid1().hex if not prefix else prefix

		for activity_type in activity_types:
			filtered_data = api.filter_by_type(activities, activity_type)
			activities_filename = "{}_{}.json".format(prefix, activity_type)
			utils.save_json_file(filtered_data, STRAVA_DATA_PATH, activities_filename)

	return activities


def load_strava_activities(filename):
	activities = json.loads(open(os.path.join(STRAVA_DATA_PATH, filename)).read())
	return activities


def populate_map_datasets(activities, prefix=None):

	starts_geojson = transformer.starts_to_geojson(activities)
	polylines_geojson = transformer.polylines_to_geojson(activities)

	prefix = uuid.uuid1().hex if not prefix else prefix

	starts_filename = "{}_{}.geojson".format(prefix, "starts")
	utils.save_json_file(starts_geojson, DATASETS_PATH, starts_filename)

	maps_filename = "{}_{}.geojson".format(prefix, "maps")
	utils.save_json_file(polylines_geojson, DATASETS_PATH, maps_filename)

	return {'maps': maps_filename, 'starts': starts_filename}


def filter_by_difficulty(activities):
	"""
	Filter rides by difficulty so we can add different layers
	"""
def ride_finder():
	job_id = uuid.uuid1().hex # Identify all files with this id
	activities = populate_athlete_data(prefix=job_id)
	geojson_files = populate_map_datasets(activities, prefix=job_id)

	mb_api = MapboxApi()
	mp_api.upload_as_tileset(geojson_files['maps'], "rides_by_dificulty_maps")
	mp_api.upload_as_tileset(geojson_files['rides'], "rides_by_dificulty_points")

	#Strava data should be uploaded in map and available

