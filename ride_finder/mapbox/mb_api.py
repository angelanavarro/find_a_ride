import logging
import os
import json
import uuid

from time import sleep
from mapbox import Uploader, Datasets, MapMatcher
from ride_finder.app_config import DATASETS_PATH


logger = logging.getLogger(__name__)

class MapboxApi(object):

    def __init__(self):
        pass

    def create_dataset(self, name, description):
        datasets = Datasets()
        res = datasets.create(name=name, description=desciption)
        ds_id = None
        if res.ok:
            ds = res.json()
            ds_id = ds['id']
        return ds_id


    def match_to_lines(self, polylines_geojson):
        matcher = MapMatcher()
        corrected_features = []
        for feature in polylines_geojson['features']:
            if len(feature['geometry']['coordinates']) > 100:
                continue
            try:
                sleep(1)
                response = matcher.match(feature, profile='mapbox.cycling')
                if response.ok:
                    corrected = response.geojson()['features'][0]
                    corrected_features.append(corrected_features)
                else:
                    logger.warning("Unexpected response while correcting line %s", response.status_code)
                    corrected_features.append(feature)
            except:
                logger.exception("Failed at correcting line. Storing original")
                corrected_features.append(feature)

        return corrected_features


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

            for i in xrange(0, 15):
                status_resp = service.status(upload_id).json()
                if 'complete' == status_resp['complete']:
                    logger.info("Tileset completed for dataset %s", dataset_filename)
                    break
                else:
                    logger.info("Waiting for upload to complete")
                    sleep(5)
            logger.info("Upload did not complete in the last 75 seconds. Check dashboard.")
