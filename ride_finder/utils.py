import logging
import json
import os

logger = logging.getLogger(__name__)

def save_json_file(json_data, filepath, filename):
	try:
		with open(os.path.join(filepath, filename), 'w') as f:
			logger.info("Storing json data as %s", filename)
			f.write(json.dumps(json_data, indent=4))
	except:
		logger.exception("Failed at saving data!")
		pass