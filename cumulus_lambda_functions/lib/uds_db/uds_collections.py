import logging
from collections import namedtuple
from datetime import datetime

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from mdps_ds_lib.lib.aws.es_abstract import ESAbstract
from mdps_ds_lib.lib.aws.es_factory import ESFactory
from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
# LOGGER = logging.getLogger(__name__)
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


CollectionIdentifier = namedtuple('CollectionIdentifier', ['urn', 'nasa', 'project', 'tenant', 'venue', 'id'])


class UdsCollections:
    collection_id = 'collection_id'
    bbox = 'bbox'
    granule_count = 'granule_count'
    start_time = 'start_time'
    end_time = 'end_time'

    def __init__(self, es_url, es_port=443, es_type='AWS', use_ssl=True):
        self.__es: ESAbstract = ESFactory().get_instance(es_type,
                                                         index=DBConstants.collections_index,
                                                         base_url=es_url,
                                                         use_ssl=use_ssl,
                                                         port=es_port)

    @staticmethod
    def decode_identifier(incoming_identifier: str) -> CollectionIdentifier:
        collection_identifier_parts = incoming_identifier.split(':')
        if len(collection_identifier_parts) < 6:
            raise ValueError(f'invalid collection: {collection_identifier_parts}')
        return CollectionIdentifier._make(collection_identifier_parts[0:6])

    def __bbox_to_polygon(self, bbox: list):
        if len(bbox) != 4:
            raise ValueError(f'not bounding box: {bbox}')
        # ['min lon', 'min lat', 'max lon', 'max lat']
        polygon = [
            [bbox[1], bbox[0]],  # min lat, min lon
            [bbox[1], bbox[2]],  # min lat, max lon
            [bbox[3], bbox[2]],  # max lat, max lon
            [bbox[3], bbox[0]],  # max lat, min lon
            [bbox[1], bbox[0]],  # min lat, min lon
        ]
        return polygon

    def delete_collection(self, collection_id: str):
        self.__es.delete_by_query({
            'query': {'term': {self.collection_id: collection_id}}
        }, DBConstants.collections_index)
        return self

    def add_collection(self, collection_id: str, start_time: int, end_time: int, bbox: list, granules_count: int=0):

        indexing_dict = {
            self.collection_id: collection_id,
            self.granule_count: granules_count,
            self.start_time: start_time,
            self.end_time: end_time,
        }
        # NOTE: a pint is not a polygon
        if len(set(bbox)) > 2:  # TODO a line is good enough for polygon?
            bbox_geoshape = {
                'type': 'polygon',
                'coordinates': [self.__bbox_to_polygon(bbox)]
            }
            LOGGER.debug(f'geo-shape: {bbox_geoshape}')
            indexing_dict[self.bbox] = bbox_geoshape

        self.__es.index_one(indexing_dict, collection_id, DBConstants.collections_index)
        return self

    def get_collection(self, collection_id: str):
        authorized_collection_ids_dsl = {
            'size': 20,
            'query': {
                'bool': {
                    'must': [
                        {'term': {DBConstants.collection_id: {'value': collection_id}}}
                    ]
                }
            },
            'sort': [
                {DBConstants.collection_id: {'order': 'asc'}}
            ]
        }
        LOGGER.debug(f'authorized_collection_ids_dsl: {authorized_collection_ids_dsl}')
        authorized_collection_ids = self.__es.query(authorized_collection_ids_dsl, DBConstants.collections_index)
        authorized_collection_ids = [k['_source'] for k in authorized_collection_ids['hits']['hits']]
        return authorized_collection_ids

    def get_collections(self, collection_regex: list):
        # temp_dsl = {
        #     'query': {'match_all': {}},
        #     'sort': [
        #         {DBConstants.collection_id: {'order': 'asc'}}
        #     ]
        # }
        # LOGGER.debug(f'temp_dsl: {temp_dsl}')
        # temp_result = self.__es.query_pages(temp_dsl, DBConstants.collections_index)
        # LOGGER.debug(f'temp_result: {temp_result}')
        authorized_collection_ids_dsl = {
            'query': {
                'bool': {
                    'should': [
                        {'regexp': {DBConstants.collection_id: {
                            'value': k,
                            'case_insensitive': True
                        }}} for k in collection_regex
                    ]
                }
            },
            'sort': [
                {DBConstants.collection_id: {'order': 'asc'}}
            ]
        }
        LOGGER.debug(f'authorized_collection_ids_dsl: {authorized_collection_ids_dsl}')
        authorized_collection_ids = self.__es.query_pages(authorized_collection_ids_dsl, DBConstants.collections_index)
        authorized_collection_ids = [k['_source'] for k in authorized_collection_ids['hits']['hits']]
        return authorized_collection_ids
