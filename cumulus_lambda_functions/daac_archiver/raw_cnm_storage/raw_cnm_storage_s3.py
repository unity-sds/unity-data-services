import json
import os
from datetime import datetime, timezone

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

from cumulus_lambda_functions.daac_archiver.raw_cnm_storage.raw_cnm_storage_abstract import RawCnmStorageAbstract


class RawCnmStorageS3(RawCnmStorageAbstract):
    def __init__(self):
        super().__init__()
        self.__s3_bucket = os.environ.get('CNM_STORAGE_BUCKET')
        self.__s3_base_path = os.environ.get('CNM_STORAGE_PREFIX', 'CNM_MESSAGES')
        self.__s3 = AwsS3()
        self.__s3.target_bucket = self.__s3_bucket
        self.__sending_id, self.__collection_id, self.__granule_id, self.__target_collection_id = None, None, None, None

    def load_metadata(self, sending_id, collection_id, granule_id, target_collection_id):
        self.__sending_id, self.__collection_id, self.__granule_id, self.__target_collection_id = sending_id, collection_id, granule_id, target_collection_id
        return self

    def store_data(self, cnm_msg: dict):
        if any([k is None for k in [self.__sending_id, self.__collection_id, self.__granule_id, self.__target_collection_id]]):
            raise ValueError(f'one or more of sending_id, collection_id, granule_id, target_collection_id is null: {[self.__sending_id, self.__collection_id, self.__granule_id, self.__target_collection_id]}')
        target_key_1 = [] if self.__s3_base_path == '' else [self.__s3_base_path]
        target_key_1.extend([self.__collection_id, self.__granule_id, self.__target_collection_id, self.__sending_id, f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S%Z')}.json"])
        self.__s3.target_key = '/'.join(target_key_1)
        self.__s3.upload_bytes(json.dumps(cnm_msg).encode())
        return self
