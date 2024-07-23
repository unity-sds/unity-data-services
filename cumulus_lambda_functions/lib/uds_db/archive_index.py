from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from cumulus_lambda_functions.lib.json_validator import JsonValidator
from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.aws.es_abstract import ESAbstract

from cumulus_lambda_functions.lib.aws.es_factory import ESFactory
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class UdsArchiveConfigIndex:
    basic_schema = {
        'type': 'object',
        'required': ['daac_collection_id', 'daac_sns_topic_arn', 'daac_data_version', 'collection', 'ss_username', 'archiving_types'],
        'properties': {
            'daac_collection_id': {'type': 'string'},
            'daac_sns_topic_arn': {'type': 'string'},
            'daac_data_version': {'type': 'string'},
            'collection': {'type': 'string'},
            'ss_username': {'type': 'string'},
            'archiving_types': {'type': 'array', 'items': {'type': 'object'}},
        }
    }
    def __init__(self, es_url, es_port=443):
        self.__es: ESAbstract = ESFactory().get_instance('AWS',
                                                         index='TODO',
                                                         base_url=es_url,
                                                         port=es_port)
        self.__tenant, self.__venue = '', ''

    def percolate_document(self, document_id):
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{self.__tenant}_{self.__venue}'.lower().strip()
        current_alias = self.__es.get_alias(write_alias_name)
        current_index_name = f'{write_alias_name}__v0' if current_alias == {} else [k for k in current_alias.keys()][0]
        read_alias_perc_name = f'{DBConstants.granules_read_alias_prefix}_{self.__tenant}_{self.__venue}_perc'.lower().strip()
        dsl = {

            # '_source': ['ss_name', 'ss_type', 'ss_username'],
            'query': {
                'percolate': {
                    'field': 'ss_query',
                    'index': current_index_name,
                    'id': document_id,
                }
            },
            # 'sort': [{'ss_name': {'order': 'asc'}}]
        }
        try:
            percolated_result = self.__es.query(dsl, querying_index=read_alias_perc_name)
        except Exception as e:
            if e.error == 'resource_not_found_exception':
                LOGGER.debug(f'unable to find document_id: {document_id} on index: {current_index_name}')
                return None
            LOGGER.exception(f'error while percolating')
            raise e
        percolated_result = [k['_source'] for k in percolated_result['hits']['hits']]
        return percolated_result

    def set_tenant_venue(self, tenant, venue):
        self.__tenant, self.__venue = tenant, venue
        return self

    def get_config(self, collection_id, username=None):
        read_alias_name = f'{DBConstants.granules_read_alias_prefix}_{self.__tenant}_{self.__venue}_perc'.lower().strip()
        conditions = [{"term": {"collection": {"value": collection_id}}}]
        if username is not None:
            conditions.append({"term": {"ss_username": {"value": username}}})
        result = self.__es.query({
            'size': 9999,
            'query': {
                'bool': {
                    'must': conditions
                }
            }
        }, read_alias_name)
        return [k['_source'] for k in result['hits']['hits']]

    def add_new_config(self, ingesting_dict: dict):
        result = JsonValidator(self.basic_schema).validate(ingesting_dict)
        if result is not None:
            raise ValueError(f'input ingesting_dict has basic_schema validation errors: {result}')
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{self.__tenant}_{self.__venue}_perc'.lower().strip()
        ingesting_dict['daac_collection_name'] = ingesting_dict.pop('daac_collection_id')
        ingesting_dict['ss_query'] = {
                "bool": {
                    "must": [{
                        "prefix": {"collection": {"value": ingesting_dict['collection']} }
                    }]
                }
            }
        result = self.__es.index_one(ingesting_dict, f"{ingesting_dict['daac_collection_name']}__{ingesting_dict['collection']}", index=write_alias_name)
        return

    def delete_config(self, collection_id, daac_collection_id):
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{self.__tenant}_{self.__venue}_perc'.lower().strip()
        self.__es.delete_by_query({
            'size': 9999,
            'query': {
                'bool': {
                    'must': [
                        { "term": {"collection": {"value": collection_id}} },
                        {"term": {"daac_collection_name": {"value": daac_collection_id}}},
                    ]
                }
            }
        }, write_alias_name)
        return

    def update_config(self, collection_id, daac_collection_id, daac_sns_topic_arn, username):
        write_alias_name = f'{DBConstants.granules_write_alias_prefix}_{self.__tenant}_{self.__venue}_perc'.lower().strip()
        result = self.__es.update_one({
            "collection": collection_id,
            "daac_collection_name": daac_collection_id,
            "daac_sns_topic_arn": daac_sns_topic_arn,
            "ss_query": {
                "bool": {
                    "must": [{
                        "term": {"collection": {"value": collection_id}}
                    }]
                }
            },
            "ss_username": username,
        }, f'{daac_collection_id}__{collection_id}', index=write_alias_name)
        return
