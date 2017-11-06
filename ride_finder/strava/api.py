import requests
import json
import os
import uuid
import logging
from ride_finder.app_config import STRAVA_DATA_PATH


logger = logging.getLogger(__name__)

class StravaApi(object):

	ACTIVITY_RUN = "Run"
	ACTIVITY_RIDE = "Ride"
	ACTIVITY_SWIM = "Swim"

	def __init__(self, athlete=407824, access_token=""):
		self.api_endpoint = "https://www.strava.com/api/v3"
		self.headers = {'contet-type': "application/json;"}
		self.base_params = {'access_token': ""}
		self.athlete = athlete


	def fetch_activities(self, before=None, after=None):
		# First find out how many activities there are
		stats = self.stats()
		all_activities = 0.0
		if stats:
			all_rides = stats.get("all_ride_totals", {}).get("count", 0)
			all_runs = stats.get("all_run_totals", {}).get("count", 0)
			all_swims = stats.get("all_swim_totals", {}).get("count", 0)
			all_activities = all_rides + all_runs + all_swims

		# Now get all the activities
		activities_per_request = 100
		activities_url = "{}/{}".format(self.api_endpoint, "athlete/activities")
		pages = (all_activities / activities_per_request) + 1

		activities = []
		page = 1
		while (page * activities_per_request) < all_activities:
			request_data = {'page': page, 'per_page': activities_per_request}
			fetched = self._make_api_request(activities_url, request_data)
			if fetched:
				activities += fetched
			page += 1
		return activities


	def load_activities(self, filepath):
		with open(filepath) as f:
			activities = json.loads(f.read())
		return activities


	def filter_by_type(self, activities, a_type):
		return filter(lambda x: x["type"] == a_type, activities)


	def stats(self):
		resource_path = "athletes/{}/stats".format(self.athlete)
		stats_url = "{}/{}".format(self.api_endpoint, resource_path)
		stats = self._make_api_request(stats_url)
		return stats


	def _make_api_request(self, url, request_params=None):
		logger.info("calling url %s", url)
		# Update any custom request params with basic authorization params
		request_params = {} if not request_params else request_params
		request_params.update(self.base_params)
		response = None
		try:
			res = requests.get(url, data=request_params, headers=self.headers)
			if res.ok:
				response = res.json()
		except Exception as e:
			logger.info("response: %s", res.text)
			logger.exception("Failure while calling API endpoint %s")
		return response

