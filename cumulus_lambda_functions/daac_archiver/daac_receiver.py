import json
import os
import requests
from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.daac_archiver.services.status_update_svc import StatusUpdateSvc
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

class DaacReceiver:
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
        self.update_stac(cnm_notification_msg)
        return
    
    def update_stac(self, cnm_notification_msg):
        update_type = os.getenv('ARCHIVAL_STATUS_MECHANISM', '')
        if not any([k for k in ['UDS', 'CATALYA'] if k == update_type]):
            raise ValueError(f"missing ARCHIVAL_STATUS_MECHANISM environment variable or value is not {['UDS', 'FAST_STAC']}")
        if update_type == 'UDS':
            return self.update_stac_uds(cnm_notification_msg)
        dac = StatusUpdateSvc()
        return dac.update_status_wrapper(cnm_notification_msg)

    def update_stac_uds(self, cnm_notification_msg):
        granules_index = GranulesDbIndex()
        granule_identifier = UdsCollections.decode_identifier(cnm_notification_msg['identifier'])  # This is normally meant to be for collection. Since our granule ID also has collection id prefix. we can use this.
        try:
            existing_granule_object = granules_index.get_entry(granule_identifier.tenant,
                                                                      granule_identifier.venue,
                                                                      cnm_notification_msg['identifier'])
        except Exception as e:
            LOGGER.exception(
                f"error while attempting to retrieve existing record: {cnm_notification_msg['identifier']}, not continuing")
            return
        LOGGER.debug(f'existing_granule_object: {existing_granule_object}')
        if cnm_notification_msg['response']['status'] == 'SUCCESS':
            granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_r_success',
                'archive_error_message': '',
                'archive_error_code': '',
            }, cnm_notification_msg['identifier'])
            return
        granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
            'archive_status': 'cnm_r_failed',
            'archive_error_message': cnm_notification_msg['response']['errorMessage'] if 'errorMessage' in
                                                                                         cnm_notification_msg[
                                                                                             'response'] else 'unknown',
            'archive_error_code': cnm_notification_msg['response']['errorCode'] if 'errorCode' in cnm_notification_msg[
                'response'] else 'unknown',
        }, cnm_notification_msg['identifier'])
        return