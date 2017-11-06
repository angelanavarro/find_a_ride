import unittest
from mock import MagicMock, patch

from ride_finder.app_config import STRAVA_DATA_PATH
from ride_finder import driver

class TestDriver(unittest.TestCase):


	@patch('ride_finder.driver.StravaApi')
	def test_populate_athlete_data_no_store(self, api_mock):
		mock_activities = {"mock": "value"}
		api_mock().fetch_activities.return_value = mock_activities
		activities = driver.populate_athlete_data(store=False)
		self.assertTrue(mock_activities, activities)


	@patch('ride_finder.driver.utils')
	@patch('ride_finder.driver.StravaApi', spec=True)
	def test_populate_athlete_data_store(self, api_mock, utils_mock):
		mock_activities = {"mock": "value"}
		prefix = "2"
		api_mock().fetch_activities.return_value = mock_activities
		api_mock().filter_by_type.return_value = mock_activities

		activities = driver.populate_athlete_data(prefix=prefix)

		utils_mock.save_json_file.assert_any_call(mock_activities, STRAVA_DATA_PATH, "2_{}.json".format(api_mock.ACTIVITY_RUN))
		utils_mock.save_json_file.assert_any_call(mock_activities, STRAVA_DATA_PATH, "2_{}.json".format(api_mock.ACTIVITY_RIDE))


	def test_populate_map_datasets(self):
		pass
