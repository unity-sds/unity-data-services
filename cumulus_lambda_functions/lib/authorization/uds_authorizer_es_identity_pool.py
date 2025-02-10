import re

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract
from mdps_ds_lib.lib.aws.es_abstract import ESAbstract
from mdps_ds_lib.lib.aws.es_factory import ESFactory
from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class UDSAuthorizorEsIdentityPool(UDSAuthorizorAbstract):

    def __init__(self, es_url: str, es_port=443, es_type='AWS', use_ssl=True) -> None:
        super().__init__()
        self.__es: ESAbstract = ESFactory().get_instance(es_type,
                                                         index=DBConstants.authorization_index,
                                                         base_url=es_url,
                                                         use_ssl=use_ssl,
                                                         port=es_port)

    def add_authorized_group(self, action: [str], resource: [str], tenant: str, venue: str, ldap_group_name: str):
        self.__es.index_one({
            DBConstants.action_key: action,
            DBConstants.resource_key: resource,
            DBConstants.tenant: tenant,
            DBConstants.tenant_venue: venue,
            DBConstants.authorized_group_name_key: ldap_group_name,
        }, f'{tenant}__{venue}__{ldap_group_name}', DBConstants.authorization_index)
        return

    def delete_authorized_group(self, tenant: str, venue: str, ldap_group_name: str):
        self.__es.delete_by_query({
            'query': {
                'bool': {
                    'must': [
                        {'term': {DBConstants.tenant: tenant}},
                        {'term': {DBConstants.tenant_venue: venue}},
                        {'term': {DBConstants.authorized_group_name_key: ldap_group_name}},
                    ]
                }
            }
        })
        return

    def __add_conditions_for_list(self, tenant: str, venue: str, ldap_group_names: list):
        conditions = []
        if tenant is None or tenant == '':
            return conditions
        conditions.append({'term': {DBConstants.tenant: tenant}})
        if venue is None or venue == '':
            return conditions
        conditions.append({'term': {DBConstants.tenant_venue: venue}})
        if ldap_group_names is None or len(ldap_group_names) < 1:
            return conditions
        conditions.append({
            'bool': {
                'should': [
                    {'terms': {DBConstants.authorized_group_name_key: ldap_group_names}}
                ]
            }
        })
        return conditions

    def list_groups(self, tenant: str, venue: str, ldap_group_names: list):
        conditions = self.__add_conditions_for_list(tenant, venue, ldap_group_names)

        if len(conditions) < 1:
            es_dsl = {
                'query': {
                    'match_all': {}
                }
            }
        else:
            es_dsl = {
                'query': {
                    'bool': {
                        'must': conditions
                    }
                }
            }
        es_dsl['sort'] = [
            {DBConstants.tenant: {'order': 'asc'}},
            {DBConstants.tenant_venue: {'order': 'asc'}},
            {DBConstants.authorized_group_name_key: {'order': 'asc'}},
        ]
        result = self.__es.query_pages(es_dsl)
        result = [k['_source'] for k in result['hits']['hits']]
        return result

    def list_authorized_groups_for(self, tenant: str, venue: str):
        result = self.__es.query_pages({
            'query': {
                'bool': {
                    'must': [
                        {'term': {DBConstants.tenant: tenant}},
                        {'term': {DBConstants.tenant_venue: venue}},
                    ]
                }
            },
            'sort': [
                {DBConstants.tenant: {'order': 'asc'}},
                {DBConstants.tenant_venue: {'order': 'asc'}},
                {DBConstants.authorized_group_name_key: {'order': 'asc'}},
            ]
        })
        result = [k['_source'] for k in result['hits']['hits']]
        return result

    def update_authorized_group(self, action: [str], resource: [str], tenant: str, venue: str, ldap_group_name: str):
        self.__es.update_one({
            DBConstants.action_key: action,
            DBConstants.resource_key: resource,
            DBConstants.tenant: tenant,
            DBConstants.tenant_venue: venue,
            DBConstants.authorized_group_name_key: ldap_group_name,
        }, f'{tenant}__{venue}__{ldap_group_name}', DBConstants.authorization_index)
        return

    def is_authorized_for_collection(self, action: str, collection_id: str, ldap_groups: list, tenant: str, venue: str):
        authorization_dsl = {
            '_source': [DBConstants.resource_key],
            'size': 9999,
            'query': {
                'bool': {
                    'must': [
                        {'terms': {DBConstants.authorized_group_name_key: ldap_groups}},
                        {'term': {DBConstants.action_key: action}},
                        {'term': {DBConstants.tenant: tenant}},
                        {'term': {DBConstants.tenant_venue: venue}},
                    ]
                }
            }
        }
        LOGGER.debug(f'authorization_dsl: {authorization_dsl}')
        authorized_collection_map = self.__es.query(authorization_dsl)
        LOGGER.debug(f'authorized_collection_map: {authorized_collection_map}')
        authorized_collection_map = [k['_source'][DBConstants.resource_key] for k in authorized_collection_map['hits']['hits']]
        authorized_collection_map = [item for sublist in authorized_collection_map for item in sublist]
        for each_collection_regex in authorized_collection_map:
            LOGGER.debug(f'comparing regex: {each_collection_regex} vs {collection_id}')
            version_regex = re.compile(each_collection_regex, re.IGNORECASE)
            if version_regex.match(collection_id):
                return True
        return False

    def get_authorized_collections(self, action: str, ldap_groups: list, tenant: str = '', venue: str = ''):
        authorization_dsl = {
            '_source': [DBConstants.resource_key],
            'size': 9999,
            'query': {
                'bool': {
                    'must': [
                        {'terms': {DBConstants.authorized_group_name_key: ldap_groups}},
                        {'term': {DBConstants.action_key: action}},
                    ]
                }
            }
        }
        if tenant != '':
            authorization_dsl['query']['bool']['must'].append({'term': {DBConstants.tenant: tenant}})
        if venue != '':
            authorization_dsl['query']['bool']['must'].append({'term': {DBConstants.tenant_venue: venue}})
        authorized_collection_map = self.__es.query(authorization_dsl)
        authorized_collection_map = [k['_source'][DBConstants.resource_key] for k in authorized_collection_map['hits']['hits']]
        authorized_collection_map = [item for sublist in authorized_collection_map for item in sublist]
        return authorized_collection_map

