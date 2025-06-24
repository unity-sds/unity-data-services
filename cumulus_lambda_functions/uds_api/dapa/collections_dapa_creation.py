import json
import os
from time import sleep
from typing import Optional

import pystac
from pydantic import BaseModel

from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections
from starlette.datastructures import URL

from cumulus_lambda_functions.cumulus_wrapper.query_collections import CollectionsQuery

from mdps_ds_lib.lib.cumulus_stac.collection_transformer import CollectionTransformer

from mdps_ds_lib.lib.aws.aws_lambda import AwsLambda

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

class SummariesModel(BaseModel):
    granuleId: list[str]
    granuleIdExtraction: list[str]
    process: list[str]


class ExtentModel(BaseModel):
    temporal: dict
    spatial: dict

class CumulusLinkModel(BaseModel):
    rel: str
    href: str
    type: Optional[str] = ''
    title: Optional[str] = ''

class CumulusCollectionModel(BaseModel):
    """
    {"type": "Collection", "id": "URN:NASA:UNITY:MAIN_PROJECT:DEV:CUMULUS_DAPA_UNIT_TEST___1697248243", "stac_version": "1.0.0",
    "description": "TODO",
    "links": [
{"rel": "root", "href": "./collection.json?bucket=internal&regex=%5EP%5B0-9%5D%7B3%7D%5B0-9%5D%7B4%7D%5BA-Z%5D%7B13%7DT%5B0-9%5D%7B12%7D01.PDS%24", "type": "application/json", "title": "P1570515ATMSSCIENCEAXT11344000000001.PDS"},
{"rel": "item", "href": "./collection.json?bucket=internal&regex=%5EP%5B0-9%5D%7B3%7D%5B0-9%5D%7B4%7D%5BA-Z%5D%7B13%7DT%5B0-9%5D%7B12%7D00.PDS.cmr.xml%24", "type": "metadata", "title": "P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml"},
{"rel": "item", "href": "./collection.json?bucket=internal&regex=%5EP%5B0-9%5D%7B3%7D%5B0-9%5D%7B4%7D%5BA-Z%5D%7B13%7DT%5B0-9%5D%7B12%7D01%5C.PDS%5C.xml%24", "type": "metadata", "title": "P1570515ATMSSCIENCEAXT11344000000001.PDS.xml"},
{"rel": "item", "href": "./collection.json?bucket=internal&regex=%5EP%5B0-9%5D%7B3%7D%5B0-9%5D%7B4%7D%5BA-Z%5D%7B13%7DT%5B0-9%5D%7B12%7D00%5C.PDS%24", "type": "data", "title": "P1570515ATMSSCIENCEAXT11344000000000.PDS"}],
"title": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
"extent": {"spatial": {"bbox": [[0, 0, 0, 0]]},
"temporal": {"interval": [["2023-10-13T18:51:02.397693Z", "2023-10-13T18:51:02.397698Z"]]}},
"license": "proprietary",
"providers": [{"name": "unity"}],
"summaries": {"granuleId": ["^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$"], "granuleIdExtraction": ["(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+"],
"process": ["modis"]}}
    """
    type: Optional[str] = 'Collection'
    stac_version: Optional[str] = '1.0.0'
    id: str
    title: str
    description: Optional[str] = 'TODO'
    license: Optional[str] = 'proprietary'
    summaries: SummariesModel
    links: list[CumulusLinkModel]
    providers: list[dict]
    extent: ExtentModel

class CollectionDapaCreation:
    def __init__(self, request_body):
        required_env = ['CUMULUS_LAMBDA_PREFIX', 'CUMULUS_WORKFLOW_SQS_URL']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')

        self.__request_body = request_body
        self.__collection_creation_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME', '').strip()
        self.__cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
        self.__include_cumulus = os.getenv('CUMULUS_INCLUSION', 'TRUE').upper().strip() == 'TRUE'
        self.__ingest_sqs_url = os.getenv('CUMULUS_WORKFLOW_SQS_URL')
        self.__report_to_ems = os.getenv('REPORT_TO_EMS', 'TRUE').strip().upper() == 'TRUE'
        self.__workflow_name = os.getenv('CUMULUS_WORKFLOW_NAME', 'CatalogGranule')
        self.__provider_id = os.getenv('UNITY_DEFAULT_PROVIDER', '')
        self.__collection_transformer = CollectionTransformer(self.__report_to_ems)
        self.__uds_collection = UdsCollections(es_url=os.getenv('ES_URL'), es_port=int(os.getenv('ES_PORT', '443')), es_type=os.getenv('ES_TYPE', 'AWS'), use_ssl=os.getenv('ES_USE_SSL', 'TRUE').strip() is True)
        self.__cumulus_collection_query = CollectionsQuery('', '')

    def analyze_cumulus_result(self, cumulus_request_result):
        if 'status' not in cumulus_request_result:
            LOGGER.error(f'status not in cumulus_request_result: {cumulus_request_result}')
            return {
                'statusCode': 500,
                'body': {
                    'message': cumulus_request_result
                }
            }, None
        return None, cumulus_request_result


    def __delete_collection_uds(self):
        try:
            delete_collection_result = self.__uds_collection.delete_collection(
                collection_id=self.__collection_transformer.get_collection_id()
            )
        except Exception as e:
            LOGGER.exception(f'failed to add collection to Elasticsearch')
            return {
                'statusCode': 500,
                'body': {
                    'message': f'unable to delete collection to Elasticsearch: {str(e)}',
                }
            }
        return None

    def __create_collection_uds(self, cumulus_collection_doc):

        try:
            time_range = self.__collection_transformer.get_collection_time_range()
            self.__uds_collection.add_collection(
                collection_id=self.__collection_transformer.get_collection_id(),
                start_time=TimeUtils().set_datetime_obj(time_range[0][0]).get_datetime_unix(True),
                end_time=TimeUtils().set_datetime_obj(time_range[0][1]).get_datetime_unix(True),
                bbox=self.__collection_transformer.get_collection_bbox(),
                granules_count=0,
            )
        except Exception as e:
            LOGGER.exception(f'failed to add collection to Elasticsearch')
            delete_collection_result = 'NA'
            if self.__include_cumulus:
                delete_collection_result = self.__cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix,
                                                                                  cumulus_collection_doc['name'],
                                                                                  cumulus_collection_doc['version'])
            return {
                'statusCode': 500,
                'body': {
                    'message': f'unable to add collection to Elasticsearch: {str(e)}',
                    'details': f'collection deletion result: {delete_collection_result}'
                }
            }
        return None

    def delete(self):
        deletion_result = {}
        try:

            cumulus_collection_doc = self.__collection_transformer.from_stac(self.__request_body)
            self.__provider_id = self.__provider_id if self.__collection_transformer.output_provider is None else self.__collection_transformer.output_provider
            LOGGER.debug(f'__provider_id: {self.__provider_id}')
            creation_result = 'NA'

            if self.__include_cumulus:
                result = self.__cumulus_collection_query.list_executions(cumulus_collection_doc, self.__cumulus_lambda_prefix)
                LOGGER.debug(f'execution list result: {result}')
                if len(result['results']) > 0:
                    self.__delete_collection_execution(cumulus_collection_doc, deletion_result)
                    return {
                        'statusCode': 409,
                        'body': {
                            'message': f'There are cumulus executions for this collection. Deleting them. Pls try again in a few minutes.',
                        }
                    }
                # self.__delete_collection_execution(cumulus_collection_doc, deletion_result)
                self.__delete_collection_rule(cumulus_collection_doc, deletion_result)
                delete_result = self.__cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix, cumulus_collection_doc['name'], cumulus_collection_doc['version'])
                delete_err, delete_result = self.analyze_cumulus_result(delete_result)
                if delete_err is not None:
                    LOGGER.error(f'deleting collection ends in error. Trying again. {delete_err}')
                    # self.__delete_collection_execution(cumulus_collection_doc, deletion_result)
                    self.__delete_collection_rule(cumulus_collection_doc, deletion_result)
                    delete_result = self.__cumulus_collection_query.delete_collection(self.__cumulus_lambda_prefix, cumulus_collection_doc['name'], cumulus_collection_doc['version'])
                    delete_err, delete_result = self.analyze_cumulus_result(delete_result)
                deletion_result['cumulus_collection_deletion'] = delete_err if delete_err is not None else delete_result
            else:
                deletion_result['cumulus_executions_deletion'] = 'NA'
                deletion_result['cumulus_rule_deletion'] = 'NA'
                deletion_result['cumulus_collection_deletion'] = 'NA'

            uds_deletion_result = self.__delete_collection_uds()
            deletion_result['uds_collection_deletion'] = uds_deletion_result if uds_deletion_result is not None else 'succeeded'
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
                'message': deletion_result
            }
        }

    def __delete_collection_rule(self, cumulus_collection_doc, deletion_result):
        if 'cumulus_rule_deletion' in deletion_result and 'statusCode' not in deletion_result['cumulus_rule_deletion']:
            return
        rule_deletion_result = self.__cumulus_collection_query.delete_sqs_rules(cumulus_collection_doc, self.__cumulus_lambda_prefix)
        rule_delete_err, rule_delete_result = self.analyze_cumulus_result(rule_deletion_result)
        deletion_result['cumulus_rule_deletion'] = rule_delete_err if rule_delete_err is not None else rule_delete_result
        return

    def __delete_collection_execution(self, cumulus_collection_doc, deletion_result):
        executions_delete_result = self.__cumulus_collection_query.delete_executions(cumulus_collection_doc, self.__cumulus_lambda_prefix)
        exec_delete_err, exec_delete_result = self.analyze_cumulus_result(executions_delete_result)
        deletion_result['cumulus_executions_deletion'] = exec_delete_err if exec_delete_err is not None else exec_delete_result
        sleep(10)
        return
    def create(self):
        try:
            cumulus_collection_doc = self.__collection_transformer.from_stac(self.__request_body)
            self.__provider_id = self.__provider_id if self.__collection_transformer.output_provider is None else self.__collection_transformer.output_provider
            LOGGER.debug(f'__provider_id: {self.__provider_id}')
            creation_result = 'NA'
            if self.__include_cumulus:
                creation_cumulus_result = self.__cumulus_collection_query.create_collection(cumulus_collection_doc, self.__cumulus_lambda_prefix)
                creation_err, creation_result = self.analyze_cumulus_result(creation_cumulus_result)
                if creation_err is not None:
                    return creation_err
            uds_creation_result = self.__create_collection_uds(cumulus_collection_doc)
            if uds_creation_result is not None:
                return uds_creation_result
            if self.__include_cumulus:
                rule_creation_result = self.__cumulus_collection_query.create_sqs_rules(
                    cumulus_collection_doc,
                    self.__cumulus_lambda_prefix,
                    self.__ingest_sqs_url,
                    self.__provider_id,
                    self.__workflow_name,
                )
                create_rule_err, create_rule_result = self.analyze_cumulus_result(rule_creation_result)
                if create_rule_err is not None:
                    return create_rule_err
            # validation_result = pystac.Collection.from_dict(self.__request_body).validate()
            # cumulus_collection_query = CollectionsQuery('', '')
            #
            # collection_transformer = CollectionTransformer(self.__report_to_ems)
            # cumulus_collection_doc = collection_transformer.from_stac(self.__request_body)
            # self.__provider_id = self.__provider_id if collection_transformer.output_provider is None else collection_transformer.output_provider
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