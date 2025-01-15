import json
import os
from copy import deepcopy

from mdps_ds_lib.lib.aws.aws_lambda import AwsLambda
from pystac import Link
from starlette.datastructures import URL

from cumulus_lambda_functions.daac_archiver.daac_archiver_logic import DaacArchiverLogic
from cumulus_lambda_functions.granules_to_es.granules_index_mapping import GranulesIndexMapping
from cumulus_lambda_functions.uds_api.dapa.pagination_links_generator import PaginationLinksGenerator
from mdps_ds_lib.lib.aws.es_middleware import ESMiddleware
from cumulus_lambda_functions.lib.cql_parser import CqlParser
from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class GranulesDapaQueryEs:
    def __init__(self, collection_id, limit, offset, input_datetime, filter_input, pagination_link_obj: PaginationLinksGenerator, base_url):
        self.__collection_cnm_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME', '').strip()
        self.__pagination_link_obj = pagination_link_obj
        self.__input_datetime = input_datetime
        self.__collection_id = collection_id
        self.__limit = limit
        self.__offset = offset
        self.__base_url = base_url
        self.__filter_input = filter_input
        self.__granules_index = GranulesDbIndex()

    def __generate_es_dsl(self):
        query_terms = [
            {'term': {'collection': {'value': self.__collection_id}}}
        ]
        query_terms.extend(self.__get_time_range_terms())
        if self.__filter_input is not None:
            query_terms.append(CqlParser('properties').transform(self.__filter_input))
        query_dsl = {
            'track_total_hits': False,
            'size': self.__limit,
            # "collapse": {"field": "id"},
            'sort': [
                {'properties.datetime': {'order': 'desc'}},
                {'id': {'order': 'asc'}}
            ],
            'query': {
                'bool': {
                    'must': query_terms
                }
            },
        }
        if self.__offset is not None:
            query_dsl['search_after'] = [k.strip() for k in self.__offset.split(',')]
        LOGGER.debug(f'query_dsl: {query_dsl}')
        return query_dsl

    def __get_time_range_terms(self):
        if self.__input_datetime is None:
            return []
        if '/' not in self.__input_datetime:
            return [
                {'range': {'properties.start_datetime': {'lte': self.__input_datetime}}},
                {'range': {'properties.end_datetime': {'gte': self.__input_datetime}}},
            ]
        split_time_range = [k.strip() for k in self.__input_datetime.split('/')]
        if split_time_range[0] == '..':
            return [
                {'range': {'properties.end_datetime': {'gte': split_time_range[1]}}},
            ]
        if split_time_range[1] == '..':
            return [
                {'range': {'properties.start_datetime': {'lte': split_time_range[0]}}},
            ]
        return [
                {'range': {'properties.start_datetime': {'lte': split_time_range[1]}}},
                {'range': {'properties.end_datetime': {'gte': split_time_range[0]}}},
            ]

    def __create_pagination_links(self, page_marker_str):
        if self.__pagination_link_obj is None:
            return []
        new_queries = deepcopy(self.__pagination_link_obj.org_query_params)
        new_queries['limit'] = int(new_queries['limit'] if 'limit' in new_queries else self.__limit)
        current_page = f"{self.__pagination_link_obj.requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        pagination_links = [
            {'rel': 'self', 'href': current_page},
            {'rel': 'root', 'href': self.__pagination_link_obj.base_url},
            # {'rel': 'prev', 'href': self.__get_prev_page()},
        ]
        new_queries = deepcopy(self.__pagination_link_obj.org_query_params)
        limit = int(new_queries['limit'] if 'limit' in new_queries else self.__limit)
        if limit > 0 and page_marker_str != '':
            new_queries['limit'] = limit
            new_queries['offset'] = page_marker_str
            pagination_links.append({'rel': 'next', 'href': f"{self.__pagination_link_obj.requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"})
        return pagination_links

    def archive_single_granule(self, granule_id):
        granules_query_dsl = {
            'query': {'bool': {'must': [{
                'term': {'id': granule_id}
            }]}}
        }
        LOGGER.debug(f'granules_query_dsl: {granules_query_dsl}')
        collection_identifier = UdsCollections.decode_identifier(self.__collection_id)
        granules_query_result = GranulesDbIndex().dsl_search(collection_identifier.tenant,
                                                             collection_identifier.venue,
                                                             granules_query_dsl)
        LOGGER.debug(f'granules_query_result: {granules_query_result}')
        if len(granules_query_result['hits']['hits']) < 1:
            raise ValueError(f'cannot find granule for : {granule_id}')
        each_granules_query_result_stripped = granules_query_result['hits']['hits'][0]['_source']
        daac_archiver = DaacArchiverLogic()
        cnm_response = daac_archiver.get_cnm_response_json_file(list(each_granules_query_result_stripped['assets'].values())[0], granule_id)
        if cnm_response is None:
            LOGGER.error(f'no CNM Response file. Not continuing to DAAC Archiving')
            return
        daac_archiver.send_to_daac_internal(cnm_response)
        return

    def __restructure_each_granule_result(self, each_granules_query_result_stripped):
        if 'event_time' in each_granules_query_result_stripped:
            each_granules_query_result_stripped.pop('event_time')
        if 'bbox' in each_granules_query_result_stripped:
            each_granules_query_result_stripped['bbox'] = GranulesDbIndex.from_es_bbox(each_granules_query_result_stripped['bbox'])
        for each_archiving_key in GranulesIndexMapping.archiving_keys:
            if each_archiving_key in each_granules_query_result_stripped:
                each_granules_query_result_stripped['properties'][each_archiving_key] = each_granules_query_result_stripped.pop(each_archiving_key)
        return

    def get_single_granule(self, granule_id):
        granules_query_dsl = {
            'size': 1,
            'sort': [{'id': {'order': 'asc'}}],
            'query': {'bool': {'must': [{
                'term': {'id': granule_id}
            }]}}
        }
        LOGGER.debug(f'granules_query_dsl: {granules_query_dsl}')
        collection_identifier = UdsCollections.decode_identifier(self.__collection_id)
        granules_query_result = GranulesDbIndex().dsl_search(collection_identifier.tenant,
                                                             collection_identifier.venue,
                                                             granules_query_dsl)
        LOGGER.debug(f'granules_query_result: {granules_query_result}')
        if len(granules_query_result['hits']['hits']) < 1:
            raise ValueError(f'cannot find granule for : {granule_id}')

        each_granules_query_result_stripped = granules_query_result['hits']['hits'][0]['_source']
        self_link = Link(rel='self', target=f'{self.__base_url}/{WebServiceConstants.COLLECTIONS}/{self.__collection_id}/items/{each_granules_query_result_stripped["id"]}', media_type='application/json', title=each_granules_query_result_stripped["id"]).to_dict(False)
        each_granules_query_result_stripped['links'].append(self_link)
        self.__restructure_each_granule_result(each_granules_query_result_stripped)
        return each_granules_query_result_stripped

    def delete_facade(self, current_url: URL, bearer_token: str):
        actual_path = current_url.path
        actual_path = actual_path if actual_path.endswith('/') else f'{actual_path}/'
        actual_path = f'{actual_path}actual'
        LOGGER.info(f'sanity_check')

        actual_event = {
            'resource': actual_path,
            'path': actual_path,
            'httpMethod': 'DELETE',
            'headers': {
                'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Authorization': bearer_token,
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
                'resourcePath': actual_path, 'httpMethod': 'PUT',
                'extendedRequestId': '', 'requestTime': '',
                'path': actual_path, 'accountId': '',
                'protocol': 'HTTP/1.1', 'stage': '', 'domainPrefix': '', 'requestTimeEpoch': 0,
                'requestId': '',
                'identity': {
                    'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None,
                    'sourceIp': '127.0.0.1', 'principalOrgId': None, 'accessKey': None,
                    'cognitoAuthenticationType': None,
                    'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'python-requests/2.28.2',
                    'user': None
                },
                'domainName': current_url.hostname, 'apiId': ''
            },
            'body': json.dumps({}),
            'isBase64Encoded': False
        }
        LOGGER.info(f'actual_event: {actual_event}')
        response = AwsLambda().invoke_function(
            function_name=self.__collection_cnm_lambda_name,
            payload=actual_event,
        )
        LOGGER.debug(f'async function started: {response}')
        return {
            'statusCode': 202,
            'body': {
                'message': 'processing'
            }
        }

    def start(self):
        try:
            granules_query_dsl = self.__generate_es_dsl()
            LOGGER.debug(f'granules_query_dsl: {granules_query_dsl}')
            collection_identifier = UdsCollections.decode_identifier(self.__collection_id)
            granules_query_result = GranulesDbIndex().dsl_search(collection_identifier.tenant,
                                                                  collection_identifier.venue,
                                                                  granules_query_dsl)
            LOGGER.debug(f'granules_query_result: {granules_query_result}')
            result_size = ESMiddleware.get_result_size(granules_query_result)
            granules_query_result_stripped = [k['_source'] for k in granules_query_result['hits']['hits']]
            for each_granules_query_result_stripped in granules_query_result_stripped:
                self_link = Link(rel='self', target=f'{self.__base_url}/{WebServiceConstants.COLLECTIONS}/{self.__collection_id}/items/{each_granules_query_result_stripped["id"]}', media_type='application/json', title=each_granules_query_result_stripped["id"]).to_dict(False)
                each_granules_query_result_stripped['links'].append(self_link)
                self.__restructure_each_granule_result(each_granules_query_result_stripped)

            pagination_link = '' if len(granules_query_result['hits']['hits']) < 1 else ','.join([k if isinstance(k, str) else str(k) for k in granules_query_result['hits']['hits'][-1]['sort']])
            return {
                'statusCode': 200,
                'body': {
                    'numberMatched': {'total_size': result_size},
                    'numberReturned': len(granules_query_result['hits']['hits']),
                    'stac_version': '1.0.0',
                    'type': 'FeatureCollection',  # TODO correct name?
                    'links': self.__create_pagination_links(pagination_link),
                    'features': granules_query_result_stripped
                }
            }
        except Exception as e:
            LOGGER.exception(f'unexpected error')
            return {
                'statusCode': 500,
                'body': {'message': f'unpredicted error: {str(e)}'}
            }
