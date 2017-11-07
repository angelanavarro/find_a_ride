import requests
import json
import os
import uuid
import logging
from concurrent import futures
from ride_finder.app_config import STRAVA_DATA_PATH


logger = logging.getLogger(__name__)

class StravaApi(object):

	ACTIVITY_RUN = "Run"
	ACTIVITY_RIDE = "Ride"
	ACTIVITY_SWIM = "Swim"


	def __init__(self, athlete, access_token):
		"""
		Initialize the API for a given user so the athlete ID and access
		token don't need to be passed all over the place all the time.

		PARAMS:
			athlete (int): The strava athlete number
			access_token (str): The athlete's access token. This is really just a workaround
				to doing oauth... Maybe one day.

		"""
		self.api_endpoint = "https://www.strava.com/api/v3"
		self.headers = {'contet-type': "application/json;"}
		self.base_params = {'access_token': access_token}
		self.athlete = athlete


	def fetch_activities(self, before=None, after=None):
		"""
		Fetch the strava activities for the current user.
		Since strava won't let us filter by activity type we'll just get them all.
		To know how many to get first fetch the stats since needs to go through their
		pagination

		OPTIONAL PARAMS:
			before(timestamp): Only fetch activities before this date. Currently ignored
			after(timestamp): Only fetch activities after this date. Currently ignored
		"""
		if before or after:
			raise NotImplementedError("Before and after are currently not implemented")

		max_activity_fetch = 100 # imposed by Strava
		page_futures = {}
		activities = []
		page = 1

		# Find out how many pages of activities are there by getting the athlete's stats
		stats = self.stats()
		if not stats:
			raise ValueError("Not enough information to collect athlete activities!")

		all_rides = stats.get("all_ride_totals", {}).get("count", 0)
		all_runs = stats.get("all_run_totals", {}).get("count", 0)
		all_swims = stats.get("all_swim_totals", {}).get("count", 0)
		all_activities = 0.0 + all_rides + all_runs + all_swims

		if all_activities:
			# Now get the activities. So far seems ok to just send as many concurrent
			# request as we want, but probably wise to not abuse this.
			# Also note that seems strava doesn't serve private activities (counts).
			activities_url = "{}/{}".format(self.api_endpoint, "athlete/activities")
			pages = int(all_activities / max_activity_fetch) + 1

			with futures.ThreadPoolExecutor(max_workers=pages) as executor:
				for page in xrange(1, pages + 1):
					request_data = {'page': page, 'per_page': max_activity_fetch}
					page_futures[page] = executor.submit(self._make_api_request, activities_url, request_data)

			for res in futures.as_completed(page_futures.values()):
				if res.result():
					activities += res.result()

			logger.info("Fetched %s activities for athlete %s", len(activities), self.athlete)
		return activities


	def load_activities(self, filepath):
		"""
		Convenience method to load stored strava activities
		"""
		with open(filepath) as f:
			activities = json.loads(f.read())
		return activities


	def filter_by_type(self, activities, a_type):
		"""
		Convenience method to filter the activities by type.
		"""
		assert a_type in [StravaApi.ACTIVITY_SWIM, StravaApi.ACTIVITY_RIDE, StravaApi.ACTIVITY_RUN]
		return filter(lambda x: x["type"] == a_type, activities)


	def stats(self):
		"""
		Fetch the stats for this user's instance.
		"""
		resource_path = "athletes/{}/stats".format(self.athlete)
		stats_url = "{}/{}".format(self.api_endpoint, resource_path)
		stats = self._make_api_request(stats_url)
		if not stats:
			logger.warning("No stats retrieved for atlhete!")
		return stats


	def _make_api_request(self, url, request_params=None, timeout=10):
		"""
		Wrapper to make the actual Strava API GET calls.
		TODO: Retry failed requests?

		PARAMS:
			url (string): The Strava API url to GET

		OPTIONAL PARAMS:
			request_params(dict): Any additional parameters to send along with the
				basic request.
			timeout (int): Time in seconds to wait for a call to complete. Defaults 10
		"""

		logger.info("calling url %s", url)
		# Update any custom request params with basic authorization params
		request_params = {} if not request_params else request_params
		request_params.update(self.base_params)
		response = None
		try:
			res = requests.get(url, data=request_params, headers=self.headers, timeout=timeout)
			if res.ok:
				response = res.json()
		except Exception:
			logger.exception("Failure while calling API endpoint %s.")
		return response

