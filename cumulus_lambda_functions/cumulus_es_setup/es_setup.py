import os

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from mdps_ds_lib.lib.aws.es_abstract import ESAbstract

from mdps_ds_lib.lib.aws.es_factory import ESFactory

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
from cumulus_lambda_functions.cumulus_es_setup import es_mappings
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class SetupESIndexAlias:
    def __init__(self):
        required_env = ['ES_URL']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__es: ESAbstract = ESFactory().get_instance(os.getenv('ES_TYPE', 'AWS'),
                                                         index=DBConstants.collections_index,
                                                         base_url=os.getenv('ES_URL'),
                                                         use_ssl=os.getenv('ES_USE_SSL', 'TRUE').strip() is True,
                                                         port=int(os.getenv('ES_PORT', '443'))
                                                         )

    def get_index_mapping(self, index_name: str):
        if not hasattr(es_mappings, index_name):
            raise ValueError(f'missing index_name: {index_name}')
        index_json = getattr(es_mappings, index_name)
        return index_json

    def start(self):
        if not hasattr(es_mappings, 'alias_pointer'):
            raise ValueError(f'missing alias_pointer')
        alias_json = getattr(es_mappings, 'alias_pointer')
        alias_json = [k['add'] for k in alias_json['actions']]
        for each_action in alias_json:
            try:
                current_index = each_action['index']
                current_alias = each_action['alias']
                LOGGER.debug(f'working on {current_index}')
                index_json = self.get_index_mapping(current_index)
                self.__es.create_index(current_index, index_json)
                self.__es.create_alias(current_index, current_alias)
            except:
                LOGGER.exception(f'failed to create index / alias for: {each_action}')
        return self
