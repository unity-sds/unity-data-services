import json
import os

from cumulus_lambda_functions.daac_archiver.ddb_mws.catalia_auth_db import CataliaAuthDb
from cumulus_lambda_functions.daac_archiver.ddb_mws.catalia_daac_handshakes_db import CataliaDaacHandshakesDb
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_fast_api.fast_api_utils import FastApiUtils
from fastapi import HTTPException

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class InternalDDBConnector:
    def __init__(self):
        required_env = ['CATALYA_DAAC_AGREEMENT_DB_NAME', 'CATALYA_DB_NAME']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.cad = CataliaAuthDb(os.getenv('CATALYA_DB_NAME'))
        self.cdhsd = CataliaDaacHandshakesDb(os.getenv('CATALYA_DAAC_AGREEMENT_DB_NAME'))
        self.auth_info = {}
        self.configured_daac_configs = []

    def __archive_methods_initiator_internal(self, collection_id, daac_collection_id):
        if daac_collection_id is None:
            self.configured_daac_configs = self.cdhsd.search(collection_id)
            configured_daac_ids = [] if len(self.configured_daac_configs) < 1 else [k[self.cdhsd.target_project] for k in self.configured_daac_configs]
        else:
            configured_daac_ids = [daac_collection_id]

        authorized_daacs = [] if len(configured_daac_ids) < 1 else self.cad.get_authorized_daac_full(self.auth_info.get('ldap_groups'), collection_id, configured_daac_ids)
        if len(authorized_daacs) < 1:
            LOGGER.debug(f'user: {self.auth_info["username"]} is not authorized for {collection_id}')
            raise HTTPException(status_code=403, detail=json.dumps({
                'message': 'not authorized to execute this action'
            }))
        return authorized_daacs

    def archive_methods_initiator(self, request, collection_id, daac_collection_id):
        LOGGER.debug(f'started archive_methods_initiator.')
        self.auth_info = FastApiUtils.get_authorization_info(request)
        return self.__archive_methods_initiator_internal(collection_id, daac_collection_id)


    def archive_methods_initiator_manual_algorithm(self, username, alg_name, alg_version, request, collection_id, daac_collection_id):
        # Get user groups from the forwarded authorizer context
        auth_info = FastApiUtils.get_authorization_info(request)
        user_groups = auth_info.get('ldap_groups', [])
        self.auth_info = {
            'username': username,
            'ldap_groups': user_groups
        }
        LOGGER.debug(f'self.auth_info: {self.auth_info}')
        username_based_authorized_daacs = self.__archive_methods_initiator_internal(collection_id, daac_collection_id)
        LOGGER.debug(f'username_based_authorized_daacs: {username_based_authorized_daacs}')
        self.auth_info['ldap_groups'] = [f'{alg_name}___{alg_version}']
        algorithm_based_authorized_daacs = self.__archive_methods_initiator_internal(collection_id, daac_collection_id)
        LOGGER.debug(f'algorithm_based_authorized_daacs: {algorithm_based_authorized_daacs}')
        # Intersection: Only allow DAAC collections authorized by BOTH user groups AND algorithm
        authorized_daacs = list(set(username_based_authorized_daacs) & set(algorithm_based_authorized_daacs))
        LOGGER.debug(f'authorized_daacs: {authorized_daacs}')
        LOGGER.debug(f'Username authorized: {username_based_authorized_daacs}, Algorithm authorized: {algorithm_based_authorized_daacs}, Final: {authorized_daacs}')
        if len(authorized_daacs) < 1:
            LOGGER.debug(f'user: {username} is not authorized for {collection_id} based on {user_groups} and {alg_name} + {alg_version}')
            raise HTTPException(status_code=403, detail=json.dumps({
                'message': f'user: {username} is not authorized for {collection_id} based on {user_groups} and {alg_name} + {alg_version}'
            }))

        return authorized_daacs