import json
import os

from mdps_ds_lib.lib.cumulus_stac.item_transformer import ItemTransformer
from cumulus_lambda_functions.lib.cql_parser import CqlParser

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from cumulus_lambda_functions.cumulus_wrapper.query_granules import GranulesQuery
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class GranulesDapaQuery:
    def __init__(self, collection_id, limit, offset, datetime, filter_input, pagination_links):
        self.__pagination_links = pagination_links
        self.__limit = limit
        self.__offset = offset
        self.__filter_input = filter_input
        page_number = (offset // limit) + 1
        if 'CUMULUS_LAMBDA_PREFIX' not in os.environ:
            raise EnvironmentError('missing key: CUMULUS_LAMBDA_PREFIX')
        self.__granules_index = GranulesDbIndex()
        self.__cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
        self.__cumulus = GranulesQuery('https://na/dev', 'NA')
        self.__cumulus.with_limit(limit)
        self.__cumulus.with_page_number(page_number)
        self.__cumulus.with_collection_id(collection_id)
        self.__collection_id = collection_id
        self.__get_time_range(datetime)
        self.__get_filter(filter_input)
        self.__es_granules_result = None  # this is where Elasticsearch granules result is stored

    def __custom_metadata_query(self):
        if self.__filter_input is None:
            return self
        LOGGER.debug(f'filter_input: {self.__filter_input}')
        dsl_query = CqlParser().transform(self.__filter_input)
        LOGGER.debug(f'CqlParser result: {dsl_query}')
        custom_metadata_query_dsl = {
            'from': self.__offset,
            'size': self.__limit,
            'query': {
                'bool': {
                    'must': [

                        dsl_query,
                    ]
                }
            }
        }

        LOGGER.debug(f'custom_metadata_query_dsl: {custom_metadata_query_dsl}')
        collection_identifier = UdsCollections.decode_identifier(self.__collection_id)
        LOGGER.debug(f'custom_metadata_query_dsl: {custom_metadata_query_dsl}')
        custom_metadata_result = GranulesDbIndex().dsl_search(collection_identifier.tenant, collection_identifier.venue,
                                                              custom_metadata_query_dsl)
        LOGGER.debug(f'custom_metadata_result: {custom_metadata_result}')
        custom_metadata_result = [k['_source'] for k in custom_metadata_result['hits']['hits']]
        self.__es_granules_result = {k['granule_id']: k for k in custom_metadata_result}
        return self


    def __get_time_range(self, datetime: str):
        if datetime is None:
            return self
        if '/' not in datetime:
            self.__cumulus.with_time(datetime)
            return self
        split_time_range = [k.strip() for k in datetime.split('/')]
        if split_time_range[0] == '..':
            self.__cumulus.with_time_to(split_time_range[1])
            return
        if split_time_range[1] == '..':
            self.__cumulus.with_time_from(split_time_range[0])
            return
        self.__cumulus.with_time_range(split_time_range[0], split_time_range[1])
        return self

    def __get_filter(self, filter_input: str):
        """
        https://portal.ogc.org/files/96288#rc_filter
        https://portal.ogc.org/files/96288#simple-cql_comparison-predicates

        { "eq": [ { "property": "city" }, "Toronto" ] }

        {
          "like": [
            { "property": "name" },
            "Smith."
          ],
          "singleChar": ".",
          "nocase": true
        }

{
  "in": {
     "value": { "property": "cityName" },
     "list": [ "Toronto", "Franfurt", "Tokyo", "New York" ],
     "nocase": false
  }
}
        :return:
        """
        if filter_input is None:
            return self
        filter_event = json.loads(filter_input)
        if 'in' not in filter_event:
            return self
        schema = {
            "type": {
                "required": ["in"],
                "properties": {
                    "in": {
                        "type": "object",
                        "required": ["value", "list"],
                        "properties": {
                            "value": {
                                "type": "object",
                                "required": ["property"],
                                "properties": {
                                    "property": {"type": "string"}
                                }
                            },
                            "list": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
        filter_event_validator_result = JsonValidator(schema).validate(filter_event)
        if filter_event_validator_result is not None:
            LOGGER.error(f'invalid event: {filter_event_validator_result}. event: {filter_event}')
            return self
        search_key = filter_event['in']['value']['property']
        search_values = filter_event['in']['value']['list']
        self.__cumulus.with_filter(search_key, search_values)
        return self

    def __get_size(self):
        try:
            cumulus_size = self.__cumulus.get_size(self.__cumulus_lambda_prefix)
        except:
            LOGGER.exception(f'cannot get cumulus_size')
            cumulus_size = {'total_size': -1}
        return cumulus_size

    def __get_custom_metadata(self, cumulus_result) -> dict:
        custom_meta_query_conditions = [{
            'bool': {
                'must': [  # TODO split if array is more than 1024
                    {'term': {'collection_id': self.__collection_id}},
                    {'term': {'granule_id': k['granuleId']}},
                ]
            }
        } for k in cumulus_result['results']]
        custom_metadata_query_dsl = {
            '_source': {
                'exclude': ['collection_id']
            },
            'sort': [{'granule_id': {'order': 'ASC'}}],
            'query': {
                'bool': {
                    'should': custom_meta_query_conditions
                }
            }
        }
        collection_identifier = UdsCollections.decode_identifier(self.__collection_id)
        LOGGER.debug(f'custom_metadata_query_dsl: {custom_metadata_query_dsl}')
        custom_metadata_result = GranulesDbIndex().dsl_search(collection_identifier.tenant, collection_identifier.venue, custom_metadata_query_dsl)
        LOGGER.debug(f'custom_metadata_result: {custom_metadata_result}')
        custom_metadata_result = [k['_source'] for k in custom_metadata_result['hits']['hits']]
        custom_metadata_result = {k['granule_id']: k for k in custom_metadata_result}
        return custom_metadata_result

    def start(self):
        try:
            self.__custom_metadata_query()
            if self.__es_granules_result is not None:
                # already queried custom metadata.
                # just need to find those granule ids from Cumulus.
                self.__get_filter('granules_id', [k for k in self.__es_granules_result.keys()])
            cumulus_result = self.__cumulus.query_direct_to_private_api(self.__cumulus_lambda_prefix, False)
            if 'server_error' in cumulus_result:
                return {
                    'statusCode': 500,
                    'body': {'message': cumulus_result['server_error']}
                }
            if 'client_error' in cumulus_result:
                return {
                    'statusCode': 400,
                    'body': {'message': cumulus_result['client_error']}
                }
            cumulus_size = self.__get_size()
            LOGGER.debug(f'cumulus_result: {cumulus_result}')
            custom_metadata_result = self.__get_custom_metadata(cumulus_result)
            main_result_dict = {k['granuleId']: k for k in cumulus_result['results']}
            for k, v in main_result_dict.items():
                if k in custom_metadata_result:
                    if 'granule_id' in custom_metadata_result[k]:
                        custom_metadata_result[k].pop('granule_id')
                    v['custom_metadata'] = custom_metadata_result[k]
            combined_cumulus_result = [ItemTransformer().to_stac(k) for k in main_result_dict.values()]
            return {
                'statusCode': 200,
                'body': {
                    'numberMatched': cumulus_size['total_size'],
                    'numberReturned': len(cumulus_result['results']),
                    'stac_version': '1.0.0',
                    'type': 'FeatureCollection',  # TODO correct name?
                    'links': self.__pagination_links,
                    'features': combined_cumulus_result
                }
            }
        except Exception as e:
            LOGGER.exception(f'unexpected error')
            return {
                'statusCode': 500,
                'body': {'message': f'unpredicted error: {str(e)}'}
            }
