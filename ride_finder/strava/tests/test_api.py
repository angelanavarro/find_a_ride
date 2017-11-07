import unittest
from mock import MagicMock, patch
from ride_finder.strava.api import StravaApi


class TestStravaApi(unittest.TestCase):


	@patch('ride_finder.strava.api.requests')
	def test_fetch_fails(self, requests_mock):
		api = StravaApi("test_user", "test_token")
		requests_mock.get = MagicMock(side_effect=Exception("Mock exception"))
		with self.assertRaises(ValueError):
			api.fetch_activities()


	@patch('ride_finder.strava.api.requests')
	def test_no_activities(self, requests_mock):
		api = StravaApi("test_user", "test_token")
		response_mock = MagicMock()
		response_mock.ok = True
		response_mock.json.return_value = {"all_ride_totals": {"count": 0}, "all_run_totals":{"count":0}}
		requests_mock.get.return_value = response_mock
		activities = api.fetch_activities()
		self.assertEqual(activities, [])

if __name__ == '__main__':
    unittest.main()