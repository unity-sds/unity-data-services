import os
from typing import Optional

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from pydantic import BaseModel

from cumulus_lambda_functions.lib.uds_db.archive_index import UdsArchiveConfigIndex
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class ArchivingTypesModel(BaseModel):
    data_type: str
    file_extension: Optional[list[str]] = []


class DaacUpdateModel(BaseModel):
    daac_collection_id: str
    daac_provider: Optional[str] = None
    daac_data_version: Optional[str] = None
    daac_sns_topic_arn: Optional[str] = None
    daac_role_arn: Optional[str] = None
    daac_role_session_name: Optional[str] = None
    archiving_types: Optional[list[ArchivingTypesModel]] = None


class DaacAddModel(BaseModel):
    daac_collection_id: str
    daac_provider: Optional[str] = None
    daac_data_version: str
    daac_sns_topic_arn: str
    daac_role_arn: str
    daac_role_session_name: str
    archiving_types: Optional[list[ArchivingTypesModel]] = []


class DaacDeleteModel(BaseModel):
    daac_collection_id: str


class DaacArchiveCrud:
    def __init__(self, authorization_info, collection_id, request_body):
        self.__daac_sns_topic_arn = os.getenv('DAAC_SNS_TOPIC_ARN')
        self.__request_body = request_body
        self.__collection_id = collection_id
        self.__authorization_info = authorization_info
        required_env = ['ES_URL', 'ADMIN_COMMA_SEP_GROUPS']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__es_url = os.getenv('ES_URL')
        self.__es_port = int(os.getenv('ES_PORT', '443'))
        self.__daac_config = UdsArchiveConfigIndex(self.__es_url, self.__es_port, os.getenv('ES_TYPE', 'AWS'), os.getenv('ES_USE_SSL', 'TRUE').strip() is True)
        collection_identifier = UdsCollections.decode_identifier(collection_id)
        self.__daac_config.set_tenant_venue(collection_identifier.tenant, collection_identifier.venue)

    def delete_config(self):
        try:
            result = self.__daac_config.delete_config(self.__collection_id, self.__request_body['daac_collection_id'])
        except Exception as e:
            LOGGER.exception(f'error during add config: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': {'message': f'error during operation: {e}'}
            }
        return {
            'statusCode': 200,
            'body': {'message': 'deleted'}
        }

    def update_config(self):
        try:
            current_result = self.__daac_config.get_config(self.__collection_id, None, self.__request_body['daac_collection_id'])
            if len(current_result) != 1:
                return {
                    'statusCode': 500,
                    'body': {'message': f'Invalid current result for the update: missing or duplicate results: {current_result}'}
                }
            updating_dict = {
                **{k: v for k, v in self.__request_body.items() if v is not None},
                'ss_username': self.__authorization_info['username'],
                'collection': self.__collection_id,
            }
            result = self.__daac_config.update_config(updating_dict)
        except Exception as e:
            LOGGER.exception(f'error during update config: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': {'message': f'error during operation: {e}'}
            }

        return {
            'statusCode': 200,
            'body': {'message': 'updated'}
        }

    def add_new_config(self):
        try:
            current_result = self.__daac_config.get_config(self.__collection_id, None,
                                                           self.__request_body['daac_collection_id'])
            if len(current_result) > 0:
                return {
                    'statusCode': 500,
                    'body': {
                        'message': f'Already have config for specified daac: {current_result}'}
                }

            ingesting_dict = {
                **{k: v for k, v in self.__request_body.items() if v is not None},
                'ss_username': self.__authorization_info['username'],
                'collection': self.__collection_id,
            }
            result = self.__daac_config.add_new_config(ingesting_dict)
        except Exception as e:
            LOGGER.exception(f'error during add config: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': {'message': f'error during operation: {e}'}
            }
        return {
            'statusCode': 200,
            'body': {'message': 'inserted'}
        }

    def get_config(self):
        try:
            result = self.__daac_config.get_config(self.__collection_id)
        except Exception as e:
            LOGGER.exception(f'error during get config: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': {'uds_daac_sns_arn': self.__daac_sns_topic_arn, 'message': f'error during operation: {e}'}
            }
        return {
            'statusCode': 200,
            'body': {
                'uds_daac_sns_arn': self.__daac_sns_topic_arn,
                'configs': result
            }
        }
