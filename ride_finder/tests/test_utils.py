import unittest
import tempfile
import os


from ride_finder import utils

class TestUtils(unittest.TestCase):


	def test_save_json_file(self):
		data = {'woo!': 'this is just a test'}
		filename = "saved_json"

		tmpdirname = tempfile.gettempdir()
		utils.save_json_file(data, tmpdirname, filename)
		full_file_path = os.path.join(tmpdirname, filename)
		self.assertTrue(os.path.isfile(full_file_path))

		os.remove(full_file_path)
		# Funnily enough, evernote has stored some files in the
		# directory so i can't delete it for now :p


	def test_save_json_file_bogus(self):
		data = set() # non serializable
		filename = "saved_json"

		tmpdirname = tempfile.gettempdir()
		utils.save_json_file(data, tmpdirname, filename)
		full_file_path = os.path.join(tmpdirname, filename)
		self.assertFalse(os.path.isfile(full_file_path))


if __name__ == '__main__':
    unittest.main()