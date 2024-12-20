import json
import os
from time import sleep

import requests
from mdps_ds_lib.lib.utils.file_utils import FileUtils

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from mdps_ds_lib.lib.aws.aws_sns import AwsSns
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections
from cumulus_lambda_functions.lib.uds_db.archive_index import UdsArchiveConfigIndex

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class DaacArchiverLogic:
    def __init__(self):
        self.__es_url, self.__es_port = os.getenv('ES_URL'), int(os.getenv('ES_PORT', '443'))
        self.__archive_index_logic = UdsArchiveConfigIndex(self.__es_url, self.__es_port, os.getenv('ES_TYPE', 'AWS'))
        self.__granules_index = GranulesDbIndex()
        self.__sns = AwsSns()
        self.__s3 = AwsS3()

    def get_cnm_response_json_file(self, potential_file, granule_id):
        if 'href' not in potential_file:
            raise ValueError(f'missing href in potential_file: {potential_file}')
        self.__s3.set_s3_url(potential_file['href'])
        LOGGER.debug(f'attempting to retrieve cnm response from : {granule_id} & {potential_file}')
        cnm_response_keys = [k for k, _ in self.__s3.get_child_s3_files(self.__s3.target_bucket, os.path.dirname(self.__s3.target_key)) if k.lower().endswith('.cnm.json')]
        if len(cnm_response_keys) < 1:
            LOGGER.debug(f'missing cnm response file: {os.path.dirname(self.__s3.target_key)}.. trying again in 30 second.')
            sleep(30)  # waiting 30 second. should be enough.
            cnm_response_keys = [k for k, _ in self.__s3.get_child_s3_files(self.__s3.target_bucket, os.path.dirname(self.__s3.target_key)) if k.lower().endswith('.cnm.json')]
            if len(cnm_response_keys) < 1:
                LOGGER.debug(f'missing cnm response file after 2nd try: {os.path.dirname(self.__s3.target_key)}.. quitting.')
                return None
        if len(cnm_response_keys) > 1:
            LOGGER.warning(f'more than 1 cnm response file: {cnm_response_keys}')
        cnm_response_keys = cnm_response_keys[0]
        LOGGER.debug(f'cnm_response_keys: {cnm_response_keys}')
        local_file = self.__s3.set_s3_url(f's3://{self.__s3.target_bucket}/{cnm_response_keys}').download('/tmp')
        cnm_response_json = FileUtils.read_json(local_file)
        FileUtils.remove_if_exists(local_file)
        return cnm_response_json

    def __extract_files(self, uds_cnm_json: dict, daac_config: dict):
        granule_files = uds_cnm_json['product']['files']
        if 'archiving_types' not in daac_config or len(daac_config['archiving_types']) < 1:
            return granule_files  # TODO remove missing md5?
        archiving_types = {k['data_type']: [] if 'file_extension' not in k else k['file_extension'] for k in daac_config['archiving_types']}
        result_files = []
        for each_file in granule_files:
            """
            {
                "type": "data",
                "name": "abcd.1234.efgh.test_file05.nc",
                "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:SNDR-SNPP_ATMS@L1B$OUTPUT___2403261440/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:SNDR-SNPP_ATMS@L1B$OUTPUT___2403261440:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.nc",
                "checksumType": "md5",
                "checksum": "unknown",
                "size": -1
            }
            """
            a = each_file['type']
            if each_file['type'] not in archiving_types:
                continue
            file_extensions = archiving_types[each_file['type']]
            if len(file_extensions) < 1:
                result_files.append(each_file)  # TODO remove missing md5?
            temp_filename = each_file['name'].upper().strip()
            if any([temp_filename.endswith(k.upper()) for k in file_extensions]):
                result_files.append(each_file)  # TODO remove missing md5?
        return result_files

    def send_to_daac_internal(self, uds_cnm_json: dict):
        granule_identifier = UdsCollections.decode_identifier(uds_cnm_json['identifier'])  # This is normally meant to be for collection. Since our granule ID also has collection id prefix. we can use this.
        self.__archive_index_logic.set_tenant_venue(granule_identifier.tenant, granule_identifier.venue)
        daac_config = self.__archive_index_logic.percolate_document(uds_cnm_json['identifier'])
        if daac_config is None or len(daac_config) < 1:
            LOGGER.debug(f'uds_cnm_json is not configured for archival. uds_cnm_json: {uds_cnm_json}')
            return
        daac_config = daac_config[0]  # TODO This is currently not supporting more than 1 daac.
        try:
            self.__sns.set_topic_arn(daac_config['daac_sns_topic_arn'])
            daac_cnm_message = {
                "collection": daac_config['daac_collection_name'],
                "identifier": uds_cnm_json['identifier'],
                "submissionTime": f'{TimeUtils.get_current_time()}Z',
                "provider": granule_identifier.tenant,
                "version": "1.6.0",  # TODO this is hardcoded?
                "product": {
                    "name": granule_identifier.id,
                    "dataVersion": daac_config['daac_data_version'],
                    'files': self.__extract_files(uds_cnm_json, daac_config),
                }
            }
            self.__sns.publish_message(json.dumps(daac_cnm_message))
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_success',
                'archive_error_message': '',
                'archive_error_code': '',
            }, uds_cnm_json['identifier'])
        except Exception as e:
            LOGGER.exception(f'failed during archival process')
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_failed',
                'archive_error_message': str(e),
            }, uds_cnm_json['identifier'])
        return

    def send_to_daac(self, event: dict):
        LOGGER.debug(f'send_to_daac#event: {event}')
        uds_cnm_json = AwsMessageTransformers().sqs_sns(event)
        LOGGER.debug(f'sns_msg: {uds_cnm_json}')
        self.send_to_daac_internal(uds_cnm_json)
        return

    def receive_from_daac(self, event: dict):
        LOGGER.debug(f'receive_from_daac#event: {event}')
        sns_msg = AwsMessageTransformers().sqs_sns(event)
        LOGGER.debug(f'sns_msg: {sns_msg}')
        cnm_notification_msg = sns_msg

        cnm_msg_schema = requests.get('https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.6.1/cumulus_sns_schema.json')
        cnm_msg_schema.raise_for_status()
        cnm_msg_schema = json.loads(cnm_msg_schema.text)
        result = JsonValidator(cnm_msg_schema).validate(cnm_notification_msg)
        if result is not None:
            raise ValueError(f'input cnm event has cnm_msg_schema validation errors: {result}')
        if 'response' not in cnm_notification_msg:
            raise ValueError(f'missing response in {cnm_notification_msg}')
        granule_identifier = UdsCollections.decode_identifier(cnm_notification_msg['identifier'])  # This is normally meant to be for collection. Since our granule ID also has collection id prefix. we can use this.
        try:
            existing_granule_object = self.__granules_index.get_entry(granule_identifier.tenant, granule_identifier.venue, cnm_notification_msg['identifier'])
        except Exception as e:
            LOGGER.exception(f"error while attempting to retrieve existing record: {cnm_notification_msg['identifier']}, not continuing")
            return
        LOGGER.debug(f'existing_granule_object: {existing_granule_object}')
        if cnm_notification_msg['response']['status'] == 'SUCCESS':
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_r_success',
                'archive_error_message': '',
                'archive_error_code': '',
            }, cnm_notification_msg['identifier'])
            return
        self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
            'archive_status': 'cnm_r_failed',
            'archive_error_message': cnm_notification_msg['response']['errorMessage'] if 'errorMessage' in cnm_notification_msg['response'] else 'unknown',
            'archive_error_code': cnm_notification_msg['response']['errorCode'] if 'errorCode' in cnm_notification_msg['response'] else 'unknown',
        }, cnm_notification_msg['identifier'])
        return
