import logging
import json
import os

logger = logging.getLogger(__name__)

def save_json_file(json_data, filepath, filename):
	"""
	Convenience method to store the fetched json data.
	PARAMS:
		json_data(dict): A json dictionary to turn into a string and store.
		filepaht(str): The path where the data will land.
		filename(str): The name of the file to write. Note right now an existing
			file will be overriden!
	"""
	full_file_path = os.path.join(filepath, filename)
	try:
		with open(full_file_path, 'w') as f:
			logger.info("Storing json data as %s", filename)
			f.write(json.dumps(json_data, indent=4))
	except:
		#TODO: This probably should be sorted out...
		if os.path.isfile(full_file_path):
			os.remove(full_file_path)
		logger.exception("Failed at saving data!")