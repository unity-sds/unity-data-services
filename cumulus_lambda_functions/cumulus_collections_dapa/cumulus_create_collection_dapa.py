import json
import os

import pystac

from cumulus_lambda_functions.cumulus_stac.collection_transformer import CollectionTransformer
from cumulus_lambda_functions.cumulus_wrapper.query_collections import CollectionsQuery
from cumulus_lambda_functions.lib.aws.aws_lambda import AwsLambda
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CumulusCreateCollectionDapa:
    def __init__(self, event):
        required_env = ['CUMULUS_LAMBDA_PREFIX', 'CUMULUS_WORKFLOW_SQS_URL']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__event = event
        self.__request_body = None
        self.__cumulus_collection_query = CollectionsQuery('', '')
        self.__cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
        self.__ingest_sqs_url = os.getenv('CUMULUS_WORKFLOW_SQS_URL')
        self.__workflow_name = os.getenv('CUMULUS_WORKFLOW_NAME', 'CatalogGranule')
        self.__provider_id = ''  # TODO. need this?
        self.__collection_creation_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME', '').strip()

    def execute_creation(self):
        try:
            cumulus_collection_doc = CollectionTransformer().from_stac(self.__request_body)
            creation_result = self.__cumulus_collection_query.create_collection(cumulus_collection_doc, self.__cumulus_lambda_prefix)
            if 'status' not in creation_result:
                LOGGER.error(f'status not in creation_result: {creation_result}')
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': creation_result
                    })
                }
            rule_creation_result = self.__cumulus_collection_query.create_sqs_rules(
                cumulus_collection_doc,
                self.__cumulus_lambda_prefix,
                self.__ingest_sqs_url,
                self.__provider_id,
                self.__workflow_name,
            )
            if 'status' not in rule_creation_result:
                LOGGER.error(f'status not in rule_creation_result. deleting collection: {rule_creation_result}')
                delete_collection_result = self.__cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix, cumulus_collection_doc['name'], cumulus_collection_doc['version'])
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': {rule_creation_result},
                        'details': f'collection deletion result: {delete_collection_result}'
                    })
                }
        except Exception as e:
            LOGGER.exception('error while creating new collection in Cumulus')
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': f'error while creating new collection in Cumulus. check details',
                    'details': str(e)
                })
            }
        LOGGER.info(f'creation_result: {creation_result}')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': creation_result
            })
        }

    def start(self):
        if 'body' not in self.__event:
            raise ValueError(f'missing body in {self.__event}')
        self.__request_body = json.loads(self.__event['body'])
        LOGGER.debug(f'request body: {self.__request_body}')
        validation_result = pystac.Collection.from_dict(self.__request_body).validate()
        if not isinstance(validation_result, list):
            LOGGER.error(f'request body is not valid STAC collection: {validation_result}')
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'request body is not valid STAC Collection schema. check details',
                         'details': validation_result})
            }
        if self.__collection_creation_lambda_name != '':
            response = AwsLambda().invoke_function(
                function_name=self.__collection_creation_lambda_name,
                payload=self.__event,
            )
            LOGGER.debug(f'async function started: {response}')
            return {
                'statusCode': 202,
                'body': json.dumps({
                    'message': 'processing'
                })
            }
        LOGGER.debug(f'creating collection.')
        return self.execute_creation()