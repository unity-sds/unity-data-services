import os
from copy import deepcopy

from cumulus_lambda_functions.granules_to_es.granules_index_mapping import GranulesIndexMapping
from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from mdps_ds_lib.lib.aws.es_abstract import ESAbstract

from mdps_ds_lib.lib.aws.es_factory import ESFactory

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class GranulesDbIndex:
    def __init__(self):
        required_env = ['ES_URL']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__es: ESAbstract = ESFactory().get_instance(os.getenv('ES_TYPE', 'AWS'),
                                                         index=DBConstants.collections_index,
                                                         base_url=os.getenv('ES_URL'),
                                                         port=int(os.getenv('ES_PORT', '443')),
                                                         use_ssl=os.getenv('ES_USE_SSL', 'TRUE').strip() is True,
                                                         )
        # self.__default_fields = {
        #     "granule_id": {"type": "keyword"},
        #     "collection_id": {"type": "keyword"},
        #     "event_time": {"type": "long"}
        # }
        self.__default_fields = GranulesIndexMapping.stac_mappings
        self.__ss_fields = GranulesIndexMapping.percolator_mappings

    @staticmethod
    def to_es_bbox(bbox_array):
        # lon = x, lat = y
        # lon, lat, lon, lat
        # -180, -90, 180, 90
        # x can be 170 to -170
        # 170, 0, -170, 10
        # latitude must be between -90.0 and 90.0
        # longitude must be between -180.0 and 180.0
        minX, minY, maxX, maxY = bbox_array

        # Ensure the values are properly sorted
        # if minX > maxX:
        #     minX, maxX = maxX, minX
        if minY > maxY:
            minY, maxY = maxY, minY

        return {
            "type": "envelope",
            "coordinates": [[minX, maxY], [maxX, minY]],
            # "coordinates": [
            #     [bbox_array[0], bbox_array[3]],  # Top-left corner (minLon, maxLat)
            #     [bbox_array[2], bbox_array[1]]   # Bottom-right corner (maxLon, minLat)
            # ]
        }

    @staticmethod
    def from_es_bbox(bbox_envelope_obj: dict):
        missing_keys = [k for k in ['type', 'coordinates'] if k not in bbox_envelope_obj]
        if len(missing_keys) > 0:
            raise ValueError(f'invalid bbox_envelope_obj, missing {missing_keys}: {bbox_envelope_obj}')
        if bbox_envelope_obj['type'] != 'envelope':
            raise ValueError(f'bbox_envelope_obj is not envelope: {bbox_envelope_obj}')
        return [
        bbox_envelope_obj["coordinates"][0][0],       # minLon
        bbox_envelope_obj["coordinates"][1][1],   # minLat
        bbox_envelope_obj["coordinates"][1][0],   # maxLon
        bbox_envelope_obj["coordinates"][0][1]        # maxLat
    ]

    @property
    def default_fields(self):
        return self.__default_fields

    @default_fields.setter
    def default_fields(self, val):
        """
        :param val:
        :return: None
        """
        self.__default_fields = val
        return

    def __add_custom_mappings(self, es_mapping: dict, include_perc=False):
        potential_ss_fields = {} if not include_perc else self.__ss_fields
        customized_es_mapping = deepcopy(self.default_fields)
        customized_es_mapping = {
            **potential_ss_fields,
            **self.default_fields,
        }
        customized_es_mapping['properties']['properties'] = {
            **es_mapping,
            **self.default_fields['properties']['properties'],
        }
        return customized_es_mapping

    def get_custom_metadata_fields(self, es_mapping: dict):
        LOGGER.debug(f'get_custom_metadata_fields#es_mapping: {es_mapping}')
        if [k for k in es_mapping.keys() if k == 'properties']:
            custom_metadata_fields = {k: v for k, v in es_mapping['properties']['properties']['properties'].items() if
                                      k not in self.default_fields['properties']['properties']}
            return custom_metadata_fields
        if [k for k in es_mapping.keys() if k == 'mappings']:
            return self.get_custom_metadata_fields(es_mapping['mappings'])
        for k, v in es_mapping.items():
            return self.get_custom_metadata_fields(v['mappings'])
        raise ValueError(f'unknown format: {es_mapping}')

    def create_new_index(self, tenant, tenant_venue, es_mapping: dict):
        # TODO validate es_mapping
        # get current version from alias
        # if not found, create a new alias
        # get base definition.
        # add custom definition
        # create new version
        # throw error and return if fails
        # add new index to read alias
        # add new index to write alias
        # add delete current index from write alias
        tenant = tenant.replace(':', '--')
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()

        current_alias = self.__es.get_alias(write_alias_name)
        # {'meta_labels_v2': {'aliases': {'metadata_labels': {}}}}
        current_index_name = f'{write_alias_name}__v0' if current_alias == {} else [k for k in current_alias.keys()][0]
        new_version = int(current_index_name.split('__')[-1][1:]) + 1
        new_index_name = f'{DBConstants.granules_index_prefix}_{tenant}_{tenant_venue}__v{new_version:02d}'.lower().strip()
        LOGGER.debug(f'new_index_name: {new_index_name}')
        customized_es_mapping = self.__add_custom_mappings(es_mapping)
        index_mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 2
            },
            "mappings": {
                "dynamic": "strict",
                "properties": customized_es_mapping,
            }
        }
        self.__es.create_index(new_index_name, index_mapping)
        self.__es.create_alias(new_index_name, read_alias_name)
        self.__es.swap_index_for_alias(write_alias_name, current_index_name, new_index_name)

        write_perc_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}_perc'.lower().strip()
        read_perc_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}_perc'.lower().strip()
        current_perc_alias = self.__es.get_alias(write_perc_alias_name)
        current_perc_index_name = f'{write_alias_name}_perc__v0' if current_perc_alias == {} else [k for k in current_perc_alias.keys()][0]
        new_perc_index_name = f'{DBConstants.granules_index_prefix}_{tenant}_{tenant_venue}_perc__v{new_version:02d}'.lower().strip()
        customized_perc_es_mapping = self.__add_custom_mappings(es_mapping, True)
        LOGGER.debug(f'customized_perc_es_mapping: {customized_perc_es_mapping}')
        perc_index_mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 2
            },
            "mappings": {
                "dynamic": "strict",
                "properties": customized_perc_es_mapping,
            }
        }
        self.__es.create_index(new_perc_index_name, perc_index_mapping)
        self.__es.create_alias(new_perc_index_name, read_perc_alias_name)
        self.__es.swap_index_for_alias(write_perc_alias_name, current_perc_index_name, new_perc_index_name)
        try:
            self.__es.migrate_index_data(current_perc_index_name, new_perc_index_name)
        except:
            LOGGER.exception(f'failed to migrate index data: {(current_perc_index_name, new_perc_index_name)}')
        return

    def get_latest_index_name(self, tenant, tenant_venue):
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        write_alias_name = self.__es.get_alias(write_alias_name)
        if len(write_alias_name) != 1:
            raise ValueError(f'missing index for {tenant}_{tenant_venue}. {write_alias_name}')
        latest_index_name = [k for k in write_alias_name.keys()][0]
        return latest_index_name

    def get_latest_index(self, tenant, tenant_venue):
        latest_index_name = self.get_latest_index_name(tenant, tenant_venue)
        index_mapping = self.__es.get_index_mapping(latest_index_name)
        if index_mapping is None:
            raise ValueError(f'missing index: {latest_index_name}')
        return index_mapping

    def delete_index(self, tenant, tenant_venue):
        tenant = tenant.replace(':', '--')
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        write_alias_name = self.__es.get_alias(write_alias_name)
        if len(write_alias_name) != 1:
            raise ValueError(f'missing index for {tenant}_{tenant_venue}. {write_alias_name}')
        latest_index_name = [k for k in write_alias_name.keys()][0]
        prev_version = int(latest_index_name.split('__v')[-1]) - 1
        if prev_version < 1:
            LOGGER.warn(f'no previous index to point write index. {latest_index_name}')
        else:
            LOGGER.debug(f'updating write alias to previous index')
            prev_index_name = f'{latest_index_name.split("__v")[0]}__v{prev_version:02d}'.lower().strip()
            self.__es.swap_index_for_alias(write_alias_name, latest_index_name, prev_index_name)
        self.__es.delete_index(latest_index_name)
        return

    def destroy_indices(self, tenant, tenant_venue):
        # TODO assuming that both read and write aliases are destroyed once indices are destroyed.
        tenant = tenant.replace(':', '--')
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        actual_read_alias = self.__es.get_alias(read_alias_name)
        for each_index in actual_read_alias.keys():
            LOGGER.debug(f'deleting index: {each_index}')
            self.__es.delete_index(each_index)
        return

    def get_entry(self, tenant: str, tenant_venue: str, doc_id: str, ):
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        result = self.__es.query_by_id(doc_id, read_alias_name)
        if result is None:
            raise ValueError(f"no such granule: {doc_id}")
        return result

    def __query_by_id_local(self, tenant: str, tenant_venue: str, doc_id: str, ):
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        dsl = {
            'size': 9999,
            'sort': [
                {'properties.datetime': {'order': 'desc'}},
                {'id': {'order': 'asc'}}
            ],
            'query': {
                'term': {'_id': doc_id}
            }
        }
        result = self.__es.query(dsl, read_alias_name)
        if result is None or len(result['hits']['hits']) < 1:
            return []
        return result['hits']['hits']

    def __delete_old_entries(self, dsl_result):
        for each_granule in dsl_result:
            LOGGER.debug(f"deleting {each_granule['_id']} from {each_granule['_index']}")
            delete_result = self.__es.delete_by_query({
                'query': {'term': {'id': each_granule['_id']}}
            }, each_granule['_index'])
            LOGGER.debug(f'delete_result: {delete_result}')
            if delete_result is None:
                raise ValueError(f"error deleting {each_granule}")
        return

    def delete_entry(self, tenant: str, tenant_venue: str, doc_id: str, ):
        result = self.__query_by_id_local(tenant, tenant_venue, doc_id)
        if len(result) < 1:
            raise ValueError(f"no such granule: {doc_id}")
        self.__delete_old_entries(result)
        return result

    def update_entry(self, tenant: str, tenant_venue: str, json_body: dict, doc_id: str, ):
        # find existing doc_id
        # if not found, throw error. Cannot update
        # if found, check index.
        # if latest index, proceed with update
        # if older index, proceed with get + delete
        # tweak meta locally, and add it.
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        json_body['event_time'] = TimeUtils.get_current_unix_milli()
        existing_entries = self.__query_by_id_local(tenant, tenant_venue, doc_id)
        if len(existing_entries) < 1:
            raise ValueError(f'unable to update {doc_id} as it is not found. ')
        latest_index_name = self.get_latest_index_name(tenant, tenant_venue)
        existing_entry = existing_entries[0]
        if existing_entry['_index'] == latest_index_name:
            LOGGER.debug(f'{doc_id} in latest index: {latest_index_name}. continuing with update')
            self.__es.update_one(json_body, doc_id, index=write_alias_name)  # TODO assuming granule_id is prefixed with collection id
            self.__delete_old_entries(existing_entries[1:])
            return
        LOGGER.debug(f'{doc_id} in older index: {latest_index_name} v. {existing_entry["_index"]}')
        new_doc = {**existing_entry['_source'], **json_body}
        self.__es.index_one(new_doc, doc_id, index=write_alias_name)  # TODO assuming granule_id is prefixed with collection id
        self.__delete_old_entries(existing_entries)
        return

    def add_entry(self, tenant: str, tenant_venue: str, json_body: dict, doc_id: str, ):
        # find existing doc_id
        # if not found, add it
        # if found, and it is in latest index, add it.
        # if found, and it is in older index, add current one, and delete the older one.

        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        json_body['event_time'] = TimeUtils.get_current_unix_milli()
        existing_entries = self.__query_by_id_local(tenant, tenant_venue, doc_id)
        if len(existing_entries) < 1:
            self.__es.index_one(json_body, doc_id, index=write_alias_name)  # TODO assuming granule_id is prefixed with collection id
            return
        latest_index_name = self.get_latest_index_name(tenant, tenant_venue)
        existing_entry = existing_entries[0]
        if existing_entry['_index'] == latest_index_name:
            self.__es.index_one(json_body, doc_id, index=write_alias_name)  # TODO assuming granule_id is prefixed with collection id
            self.__delete_old_entries(existing_entries[1:])
            return
        self.__es.index_one(json_body, doc_id, index=write_alias_name)  # TODO assuming granule_id is prefixed with collection id
        self.__delete_old_entries(existing_entries)
        # TODO validate custom metadata vs the latest index to filter extra items
        return

    def get_size(self, tenant: str, tenant_venue: str, collection_id: str):
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        search_dsl = {
            'query': {'bool': {'must': [{
                'term': {'collection': collection_id}
            }]}},
            'size': 0
        }
        search_result = self.__es.query(search_dsl, querying_index=read_alias_name)
        return self.__es.get_result_size(search_result)

    def dsl_search(self, tenant: str, tenant_venue: str, search_dsl: dict):
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{tenant}_{tenant_venue}'.lower().strip()
        if 'sort' not in search_dsl:  # We cannot paginate w/o sort. So, max is 10k items:
            # This also assumes "size" should be part of search_dsl
            search_result = self.__es.query(search_dsl, querying_index=read_alias_name)
            LOGGER.debug(f'search_finished: {len(search_result["hits"]["hits"])}')
            return search_result
        # we can run paginate search
        original_size = search_dsl['size'] if 'size' in search_dsl else 20
        total_size = -999
        result = []
        duplicates = set([])
        while len(result) < original_size:
            search_dsl['size'] = (original_size - len(result)) * 2
            search_result = self.__es.query_pages(search_dsl, querying_index=read_alias_name)
            if total_size == -999:
                total_size = self.__es.get_result_size(search_result)
            if len(search_result['hits']['hits']) < 1:
                break
            for each in search_result['hits']['hits']:
                if each['_id'] not in duplicates:
                    duplicates.add(each['_id'])
                    result.append(each)
            search_dsl['search_after'] = search_result['hits']['hits'][-1]['sort']

        LOGGER.debug(f'search_finished: {len(result)}')
        if len(result) > original_size:
            result = result[:original_size]
        return {
            'hits': {
                "total": {
                    "value": total_size,
                },
                'hits': result
            }
        }



