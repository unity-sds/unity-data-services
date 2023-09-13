import json
import os

import pystac
from cumulus_lambda_functions.lib.time_utils import TimeUtils

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections
from starlette.datastructures import URL

from cumulus_lambda_functions.cumulus_wrapper.query_collections import CollectionsQuery

from cumulus_lambda_functions.cumulus_stac.collection_transformer import CollectionTransformer

from cumulus_lambda_functions.lib.aws.aws_lambda import AwsLambda

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CollectionDapaCreation:
    def __init__(self, request_body):
        required_env = ['CUMULUS_LAMBDA_PREFIX', 'CUMULUS_WORKFLOW_SQS_URL']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')

        self.__request_body = request_body
        self.__collection_creation_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME', '').strip()
        self.__cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
        self.__ingest_sqs_url = os.getenv('CUMULUS_WORKFLOW_SQS_URL')
        self.__report_to_ems = os.getenv('REPORT_TO_EMS', 'TRUE').strip().upper() == 'TRUE'
        self.__workflow_name = os.getenv('CUMULUS_WORKFLOW_NAME', 'CatalogGranule')
        self.__provider_id = os.getenv('UNITY_DEFAULT_PROVIDER', '')

    def create(self):
        try:
            # validation_result = pystac.Collection.from_dict(self.__request_body).validate()
            cumulus_collection_query = CollectionsQuery('', '')

            collection_transformer = CollectionTransformer(self.__report_to_ems)
            cumulus_collection_doc = collection_transformer.from_stac(self.__request_body)
            self.__provider_id = self.__provider_id if collection_transformer.output_provider is None else collection_transformer.output_provider
            creation_result = cumulus_collection_query.create_collection(cumulus_collection_doc, self.__cumulus_lambda_prefix)
            if 'status' not in creation_result:
                LOGGER.error(f'status not in creation_result: {creation_result}')
                return {
                    'statusCode': 500,
                    'body': {
                        'message': creation_result
                    }
                }
            uds_collection = UdsCollections(es_url=os.getenv('ES_URL'), es_port=int(os.getenv('ES_PORT', '443')))
            try:
                time_range = collection_transformer.get_collection_time_range()
                uds_collection.add_collection(
                    collection_id=collection_transformer.get_collection_id(),
                    start_time=TimeUtils().set_datetime_obj(time_range[0][0]).get_datetime_unix(True),
                    end_time=TimeUtils().set_datetime_obj(time_range[0][1]).get_datetime_unix(True),
                    bbox=collection_transformer.get_collection_bbox(),
                    granules_count=0,
                )
            except Exception as e:
                LOGGER.exception(f'failed to add collection to Elasticsearch')
                delete_collection_result = cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix, cumulus_collection_doc['name'], cumulus_collection_doc['version'])
                return {
                    'statusCode': 500,
                    'body': {
                        'message': f'unable to add collection to Elasticsearch: {str(e)}',
                        'details': f'collection deletion result: {delete_collection_result}'
                    }
                }
            LOGGER.debug(f'__provider_id: {self.__provider_id}')
            rule_creation_result = cumulus_collection_query.create_sqs_rules(
                cumulus_collection_doc,
                self.__cumulus_lambda_prefix,
                self.__ingest_sqs_url,
                self.__provider_id,
                self.__workflow_name,
            )
            if 'status' not in rule_creation_result:
                LOGGER.error(f'status not in rule_creation_result. deleting collection: {rule_creation_result}')
                delete_collection_result = cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix, cumulus_collection_doc['name'], cumulus_collection_doc['version'])
                uds_collection.delete_collection(collection_transformer.get_collection_id())
                return {
                    'statusCode': 500,
                    'body': {
                        'message': rule_creation_result,
                        'details': f'collection deletion result: {delete_collection_result}'
                    }
                }
        except Exception as e:
            LOGGER.exception('error while creating new collection in Cumulus')
            return {
                'statusCode': 500,
                'body': {
                    'message': f'error while creating new collection in Cumulus. check details',
                    'details': str(e)
                }
            }
        LOGGER.info(f'creation_result: {creation_result}')
        return {
            'statusCode': 200,
            'body': {
                'message': creation_result
            }
        }

    def start(self, current_url: URL, bearer_token: str):
        LOGGER.debug(f'request body: {self.__request_body}')
        validation_result = pystac.Collection.from_dict(self.__request_body).validate()
        if not isinstance(validation_result, list):
            LOGGER.error(f'request body is not valid STAC collection: {validation_result}')
            return {
                'statusCode': 500,
                'body': {'message': f'request body is not valid STAC Collection schema. check details',
                         'details': validation_result}
            }
        actual_path = current_url.path
        actual_path = actual_path if actual_path.endswith('/') else f'{actual_path}/'
        actual_path = f'{actual_path}actual'
        LOGGER.info(f'sanity_check')

        actual_event = {
            'resource': actual_path,
            'path': actual_path,
            'httpMethod': 'POST',
            'headers': {
                'Authorization': bearer_token,
                'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                'Host': current_url.hostname, 'User-Agent': 'python-requests/2.28.2',
                'X-Amzn-Trace-Id': 'Root=1-64a66e90-6fa8b7a64449014639d4f5b4', 'X-Forwarded-For': '44.236.15.58',
                'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'},
            'multiValueHeaders': {
                'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate'], 'Authorization': [bearer_token],
                'Host': [current_url.hostname], 'User-Agent': ['python-requests/2.28.2'],
                'X-Amzn-Trace-Id': ['Root=1-64a66e90-6fa8b7a64449014639d4f5b4'],
                'X-Forwarded-For': ['127.0.0.1'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']
            },
            'queryStringParameters': {},
            'multiValueQueryStringParameters': {},
            'pathParameters': {},
            'stageVariables': None,
            'requestContext': {
                'resourceId': '',
                'authorizer': {'principalId': '', 'integrationLatency': 0},
                'resourcePath': actual_path, 'httpMethod': 'POST',
                'extendedRequestId': '', 'requestTime': '',
                'path': actual_path, 'accountId': '',
                'protocol': 'HTTP/1.1', 'stage': '', 'domainPrefix': '', 'requestTimeEpoch': 0,
                'requestId': '',
                'identity': {
                    'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None,
                    'sourceIp': '127.0.0.1', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None,
                    'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'python-requests/2.28.2', 'user': None
                },
                'domainName': current_url.hostname, 'apiId': ''
            },
            'body': json.dumps(self.__request_body),
            'isBase64Encoded': False
        }
        LOGGER.info(f'actual_event: {actual_event}')
        response = AwsLambda().invoke_function(
            function_name=self.__collection_creation_lambda_name,
            payload=actual_event,
        )
        LOGGER.debug(f'async function started: {response}')
        return {
            'statusCode': 202,
            'body': json.dumps({
                'message': 'processing'
            })
        }