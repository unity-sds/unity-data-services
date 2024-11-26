import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils

from cumulus_lambda_functions.uds_api.dapa.collections_dapa_cnm import CollectionsDapaCnm

from mdps_ds_lib.lib.cumulus_stac.unity_collection_stac import UnityCollectionStac
from cumulus_lambda_functions.uds_api.dapa.collections_dapa_creation import CollectionDapaCreation
from mdps_ds_lib.lib.cumulus_stac.item_transformer import ItemTransformer
from pystac import ItemCollection, Item
from mdps_ds_lib.lib.utils.file_utils import FileUtils
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

"""
TODO

UNITY_DEFAULT_PROVIDER
CUMULUS_WORKFLOW_NAME
REPORT_TO_EMS
CUMULUS_WORKFLOW_SQS_URL  
CUMULUS_LAMBDA_PREFIX
ES_URL                
ES_PORT              
SNS_TOPIC_ARN
"""
class GranulesCnmIngesterLogic:
    def __init__(self):
        self.__s3 = AwsS3()
        self.__successful_features_json = None
        self.__successful_features: ItemCollection = None
        self.__collection_id = None
        self.__chunk_size = StageInOutUtils.CATALOG_DEFAULT_CHUNK_SIZE
        if 'UNITY_DEFAULT_PROVIDER' not in os.environ:
            raise ValueError(f'missing UNITY_DEFAULT_PROVIDER')
        self.__default_provider = os.environ.get('UNITY_DEFAULT_PROVIDER')
        self.__uds_collection = UdsCollections(es_url=os.getenv('ES_URL'), es_port=int(os.getenv('ES_PORT', '443')))

    @property
    def successful_features_json(self):
        return self.__successful_features_json

    @successful_features_json.setter
    def successful_features_json(self, val):
        """
        :param val:
        :return: None
        """
        self.__successful_features_json = val
        return

    @property
    def collection_id(self):
        return self.__collection_id

    @collection_id.setter
    def collection_id(self, val):
        """
        :param val:
        :return: None
        """
        self.__collection_id = val
        return

    @property
    def successful_features(self):
        return self.__successful_features

    @successful_features.setter
    def successful_features(self, val):
        """
        :param val:
        :return: None
        """
        self.__successful_features = val
        return

    def load_successful_features_s3(self, successful_features_s3_url):
        self.__s3.set_s3_url(successful_features_s3_url)
        if not self.__s3.exists(self.__s3.target_bucket, self.__s3.target_key):
            LOGGER.error(f'missing successful_features: {successful_features_s3_url}')
            raise ValueError(f'missing successful_features: {successful_features_s3_url}')
        local_successful_features = self.__s3.download('/tmp')
        self.__successful_features_json = FileUtils.read_json(local_successful_features)
        FileUtils.remove_if_exists(local_successful_features)
        self.__successful_features = ItemCollection.from_dict(self.__successful_features_json)
        return

    def validate_granules(self):
        if self.successful_features is None:
            raise RuntimeError(f'NULL successful_features')
        missing_granules = []
        for each_granule in self.successful_features.items:
            missing_assets = []
            for each_asset_name, each_asset in each_granule.assets.items():
                temp_bucket, temp_key = self.__s3.split_s3_url(each_asset.href)
                if not self.__s3.exists(temp_bucket, temp_key):
                    missing_assets.append({each_asset_name: each_asset.href})
            if len(missing_assets) > 0:
                missing_granules.append({
                    'granule_id': each_granule.id,
                    'missing_assets': missing_assets
                })
        if len(missing_granules) > 0:
            LOGGER.error(f'missing_granules: {missing_granules}')
            raise ValueError(f'missing_granules: {missing_granules}')
        return

    def extract_collection_id(self):
        if self.successful_features is None:
            raise RuntimeError(f'NULL successful_features')
        if len(self.successful_features.items) < 1:
            LOGGER.error(f'not required to process. No Granules: {self.successful_features.to_dict(False)}')
            return
        self.collection_id = list(set([k.collection_id for k in self.successful_features.items]))
        return

    def has_collection(self):
        uds_collection_result = self.__uds_collection.get_collection(self.collection_id)
        return len(uds_collection_result) > 0

    def create_one_collection(self, collection_id):
        try:
            if collection_id is None:
                raise RuntimeError(f'NULL collection_id')
            if self.has_collection():
                LOGGER.debug(f'{collection_id} already exists. continuing..')
                return {'status': 'success'}
                # ref: https://github.com/unity-sds/unity-py/blob/0.4.0/unity_sds_client/services/data_service.py
            dapa_collection = UnityCollectionStac() \
                .with_id(collection_id) \
                .with_graule_id_regex("^test_file.*$") \
                .with_granule_id_extraction_regex("(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
                .with_title(f'Collection: {collection_id}') \
                .with_process('stac') \
                .with_provider(self.__default_provider) \
                .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'unknown_bucket', 'application/json', 'root') \
                .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'protected', 'data', 'item') \
                .add_file_type("test_file01.nc.cas", "^test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
                .add_file_type("test_file01.nc.cmr.xml", "^test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
                .add_file_type("test_file01.nc.stac.json", "^test_file.*\\.nc.stac.json$", 'protected', 'metadata',
                               'item')

            stac_collection = dapa_collection.start()
            creation_result = CollectionDapaCreation(stac_collection).create()
            if creation_result['statusCode'] >= 400:
                raise RuntimeError(
                    f'failed to create collection: {collection_id}. details: {creation_result["body"]}')
            time.sleep(3)  # cool off period before checking DB
            if not self.has_collection():
                LOGGER.error(f'missing collection. (failed to create): {collection_id}')
                raise ValueError(f'missing collection. (failed to create): {collection_id}')
        except Exception as e:
            return {'status': 'error', 'details': str(e)}
        return {'status': 'success'}

    def create_collection_async(self):
        if self.collection_id is None:
            raise RuntimeError(f'NULL collection_id')
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.create_one_collection, collection_id) for collection_id in self.collection_id]
            results = [future.result() for future in as_completed(futures)]
        errors = [k['details'] for k in results if k['status'] == 'error']
        if len(errors) > 0:
            raise ValueError(f'error while creating collections: {errors}')
        return

    def send_cnm_msg(self):
        LOGGER.debug(f'starting ingest_cnm_dapa_actual')
        try:
            errors = []
            for i, features_chunk in enumerate(StageInOutUtils.chunk_list(self.successful_features_json['features'], self.__chunk_size)):
                try:
                    LOGGER.debug(f'working on chunk_index {i}')
                    dapa_body = {
                        "provider_id": self.__default_provider,
                        "features": features_chunk
                    }
                    collections_dapa_cnm = CollectionsDapaCnm(dapa_body)
                    cnm_result = collections_dapa_cnm.start()
                    if cnm_result['statusCode'] != 200:
                        errors.extend(features_chunk)
                except Exception as e1:
                    LOGGER.exception(f'failed to queue CNM process.')
                    errors.extend(features_chunk)
        except Exception as e:
            LOGGER.exception('failed to ingest to CNM')
            raise ValueError(f'failed to ingest to CNM: {e}')
        if len(errors) > 0:
            raise RuntimeError(f'failures during CNM ingestion: {errors}')
        return

    def start(self, event):
        LOGGER.debug(f'event: {event}')
        sns_msg = AwsMessageTransformers().sqs_sns(event)
        s3_details = AwsMessageTransformers().get_s3_from_sns(sns_msg)
        s3_url = f's3://{s3_details["bucket"]}/{s3_details["key"]}'
        self.load_successful_features_s3(s3_url)
        self.validate_granules()
        self.extract_collection_id()
        self.create_collection_async()
        self.send_cnm_msg()
        return
