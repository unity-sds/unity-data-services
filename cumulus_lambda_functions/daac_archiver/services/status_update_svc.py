
import os
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from cumulus_lambda_functions.daac_archiver.catalia_archiving_traces import CataliaArchivingTraces
from cumulus_lambda_functions.daac_archiver.services.sfa_client_mw import SfaClientMw
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.daac_archiver.catalia_status_db import CataliaStatusDb

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class StatusUpdateSvc:
    archival_status_schema = {
      "type": "object",
      "required": [
        "status"
      ],
      "properties": {
        "status": {
          "type": "string",
          "enum": [
            "cnm-authorized-success",
            "cnm-authorized-failed",
            "cnm-staged-success",
            "cnm-staged-failed",
            "cnm-submit-success",
            "cnm-submit-failed",
            "cnm-receive-success",
            "cnm-receive-failed"
          ]
        },
        "errorCode": {
          "type": "string"
        },
        "errorMessage": {
          "type": "string"
        },
        "href": {
          "type": "string",
          "format": "iri-reference"
        },
        "datetime": {
              "title": "Date and Time",
              "description": "timestamp of this update, in UTC (Formatted in RFC 3339) ",
              "type": "string",
              "format": "date-time",
              "pattern": "(\\+00:00|Z)$"
          }
      },
      "additionalProperties": False
    }

    def __init__(self):
        self.__uds_ctla_archiving_traces = CataliaArchivingTraces(os.getenv('CATALYA_TRACING_DB', None))
        self.__status_ddb = CataliaStatusDb(os.getenv('CATALYA_STATUS_DB', None))
        self.__archiving_granules_stac = None
        self.__identifier, self.__collection, self.__granule = None, None, None

    def load_manually(self, identifier, collection, granule):
        self.__identifier, self.__collection, self.__granule = identifier, collection, granule
        return self

    def load_from_db(self, identifier:str):
        archived_granule_metadata = self.__uds_ctla_archiving_traces.get(identifier)
        if archived_granule_metadata is None or (isinstance(archived_granule_metadata, list) and len(archived_granule_metadata) < 1):
            raise ValueError(f'missing archived metadata for identifier : {identifier}')
        self.__identifier, self.__collection, self.__granule = identifier, archived_granule_metadata[0][CataliaStatusDb.collection], archived_granule_metadata[0][CataliaStatusDb.name_str]
        return self

    def validate_status(self, archival_status):
        import jsonschema
        from datetime import datetime
        if not isinstance(archival_status, dict):
            raise ValueError(f'archival_status must be a dictionary, got {type(archival_status)}')

        # Validate archival_status against schema
        try:
            jsonschema.validate(archival_status, self.archival_status_schema)
            LOGGER.debug(f'archival_status validation successful: {archival_status}')
        except jsonschema.ValidationError as e:
            LOGGER.error(f'archival_status validation failed: {e}')
            raise ValueError(f'Invalid archival_status format: {e.message}')
        return

    def update_status_wrapper(self, cnm_notification_msg: dict):
        existing_statuses = self.__status_ddb.get(cnm_notification_msg['identifier'])
        if len(existing_statuses) < 1:
            raise ValueError(f'unknown collection & granule: {cnm_notification_msg}')
        self.__identifier, self.__collection, self.__granule = cnm_notification_msg['identifier'], existing_statuses[0][CataliaStatusDb.collection], existing_statuses[0][CataliaStatusDb.name_str]
        if cnm_notification_msg['response']['status'] == 'SUCCESS':
            latest_daac_status = {
                'status': 'cnm-receive-success',
            }
            # TODO ask DAAC if they pass HREF?
        else:
            latest_daac_status = {
                'status': 'cnm-receive-failed',
                'errorMessage': cnm_notification_msg['response']['errorMessage'] if 'errorMessage' in cnm_notification_msg['response'] else 'unknown',
                'errorCode': cnm_notification_msg['response']['errorCode'] if 'errorCode' in cnm_notification_msg['response'] else 'unknown',
            }
        self.update_status(latest_daac_status)
        return self

    def update_status_ddb(self, archival_status):
        if any([k is None for k in [self.__identifier, self.__collection, self.__granule]]):
            raise ValueError(f'missing identifier, collection, or granule ID')
        try:
            self.__status_ddb.add(self.__identifier, self.__collection, self.__granule, archival_status['status'],
                                  archival_status['datetime'],
                                  archival_status['errorCode'] if 'errorCode' in archival_status else None,
                                  archival_status['errorMessage'] if 'errorMessage' in archival_status else None,
                                  archival_status['href'] if 'href' in archival_status else None,
                                  )
        except Exception as e:
            LOGGER.exception(f'Failed to store status in DDB {self.__collection}')
            raise e

    def update_status(self, archival_status: dict):
        """
        1. validate archival_status from parameter against self.archival_status_schema
        2. Add archival_status to self.__archiving_granules_stac>properties>archival:status
        3. get collection and item id from  self.__archiving_granules_stac
        4. convert self.__archiving_granules_stac to a json
        5. call self.__sfa_client.update_item()  # Note partial may not be available. Just update whole for now.
        :param archival_status:
        :return:
        """
        # TODO optional updating DEVSEED. configurable
        # TODO store status to DDB?
        # TODO if final status, write back to S3
        self.validate_status(archival_status)
        # Add timestamp to the status
        archival_status_with_timestamp = archival_status.copy()
        archival_status_with_timestamp['datetime'] = f'{TimeUtils.get_current_time()}Z'
        errors = []
        try:
            self.update_status_ddb(archival_status_with_timestamp)
        except Exception as e:
            errors.append(e)

        try:
            SfaClientMw().load_manually(self.__collection, self.__granule).update_sfa_item_status(archival_status_with_timestamp)
        except Exception as e:
            errors.append(e)

        # TODO update TRACE if success and write to S3 original file adjacent
        if len(errors) > 0:
            raise RuntimeError(f'Failed to update STAC item status: {errors}')
        return