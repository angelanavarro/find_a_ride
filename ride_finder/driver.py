import os
import json
from strava import transformer
import uuid
from ride_finder.strava.api import StravaApi
from ride_finder.mapbox.mb_api import MapboxApi
from ride_finder.app_config import DATASETS_PATH, STRAVA_DATA_PATH
from ride_finder import utils

import logging
logger = logging.getLogger()

def populate_athlete_data(athlete, access_token, store=True, prefix=None):

	"""
	Fetch the athlete's activities.
	PARAMS:
		athlete (int): The athlete's ID for the Strava API
		access_token (string): The access token for the Strava API

	OPTIONAL PARAMS:
		store (bool): True if the data should be stored. Mostly for convenience.
		prefix (string): Use this in all stored data to identify it as part of this run
	"""
	api = StravaApi(athlete, access_token)
	activities = api.fetch_activities()
	if not activities:
		logger.warning("No activities found to populate the user's data!")
		return activities

	if store:
		activity_types = [StravaApi.ACTIVITY_RIDE, StravaApi.ACTIVITY_RUN, StravaApi.ACTIVITY_SWIM]

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


def populate_map_datasets(activities, prefix=None, smooth_lines=False):
	"""
	Given an array of strava activities, turn them into geojson and store them.
	The Mapbox API right now requires these files to be read from disk.

	PARAMS:
		activities (list<dict>): The Strava activities to turn into ride finder tilesets

	OPTIONAL PARAMS:
		prefix (string): Use this to identify the populated files. Defaults to UUID
		smooth_lines(bool): If True, it will try to snap the GPS data to actual roads and
			reduce noise, but will be pretty slow. Defaults to False.

	"""
	prefix = uuid.uuid1().hex if not prefix else prefix
	starts_geojson = transformer.starts_to_geojson(activities)
	polylines_geojson = transformer.polylines_to_geojson(activities)
	if smooth_lines:
		mb_api = MapboxApi()
		polylines_geojson = mb_api.match_to_lines(polylines_geojson)

	starts_filename = "{}_{}.geojson".format(prefix, "starts")
	utils.save_json_file(starts_geojson, DATASETS_PATH, starts_filename)

	maps_filename = "{}_{}.geojson".format(prefix, "maps")
	utils.save_json_file(polylines_geojson, DATASETS_PATH, maps_filename)

	validate_tileset(starts_geojson)
	validate_tileset(polylines_geojson)
	return {'maps': maps_filename, 'starts': starts_filename}


def validate_tileset(tileset):
	"""
	For now at least make sure there are features since we are overriding
	"""
	if not tileset["features"]:
		raise ValueError("Not enough data to generate maps. Halting executiong")
	logger.info("Tileset seems valid")


def create_rides_by_difficulty(athlete=None, access_token=None, activities_filename=None, tileset_name="rides_by_dificulty"):
	"""
	Entry point of this toy experiment. Given an athlete and an access token for a strava user,
	populate a map with the user's strava bike rides.
	Layers of the map will be colored for difficulty based on lengh:elevation, lenght and
	percentage of stoppage time.
	Right now this is only functional for bike ride activities as the layers and metrics are colored
	for those values.

	OPTIONAL PARAMS:
		athlete (id): The strava user id. Defaults to STRAVA_ATHLETE_ID env variable
		access_token (str): The strava access token. Should really be done via oauth.
			Defaults to STRAVA_ACCESS_TOKEN env variable
		activities_filename (str): If activities should be reused from storage
		tileset_name: This is the name of the tileset set to generate
	"""

	#Identify all files with this id
	job_id = uuid.uuid1().hex
	access_token = os.environ['STRAVA_ACCESS_TOKEN'] if not access_token else access_token
	strava_athlete = os.environ['STRAVA_ATHLETE_ID'] if not athlete else athlete
	activities = None
	if activities_filename:
		activities = load_strava_activities(filename)

	if not activities:
		activities = populate_athlete_data(strava_athlete, access_token, prefix=job_id)

	# This will raise an exception if there's no data.
	geojson_files = populate_map_datasets(activities, prefix=job_id)

	# Turn strava data into a tileset
	mb_api = MapboxApi()
	mb_api.upload_as_tileset(geojson_files['maps'], tileset_name)
	# mb_api.upload_as_tileset(geojson_files['starts'], "{}_points".format(tileset_name))

	logger.info("Completed uploading tilesets! Check your map.")


