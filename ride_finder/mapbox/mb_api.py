import logging
import os
import json
import uuid

from time import sleep
from mapbox import Uploader, Datasets
from ride_finder.app_config import DATASETS_PATH


logger = logging.getLogger(__name__)

class MapboxApi(object):

    def __init__(self):
        pass

    def create_dataset(name, description):
        datasets = Datasets()
        res = datasets.create(name=name, description=desciption)
        ds_id = None
        if res.ok:
            ds = res.json()
            ds_id = ds['id']
        return ds_id


    def upload_dataset_features(self, dataset_id, dataset_filename):
        """
        Upload a dataset to mapbox
        This is rather slow uploading one by one so use upload as tileset
        """
        datasets = Datasets()
        with open(os.path.join(DATASETS_PATH, dataset_filename)) as src:
            features = json.load(src)
            for fid, feature in enumerate(features.get("features", [])):
                datasets.update_feature(dataset_id, fid, feature)


    def upload_as_tileset(self, dataset_filename, map_id=None):
        map_id = uuid.uuid1().hex if not map_id else map_id
        service = Uploader()
        with open(os.path.join(DATASETS_PATH, dataset_filename)) as src:
            upload_resp = service.upload(src, map_id)

        if upload_resp.status_code == 201:
            upload_id = upload_resp.json()['id']

            for i in xrange(0, 12):
                status_resp = service.status(upload_id).json()
                if 'complete' == status_resp['complete']:
                    logger.info("Tileset completed for dataset %s", dataset_filename)
                    break
                else:
                    logger.info("Waiting for upload to complete")
                    sleep(5)
            logger.info("Upload did not complete in the last 60 seconds. Check dashboard.")
