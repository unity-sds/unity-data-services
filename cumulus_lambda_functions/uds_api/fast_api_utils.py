import base64
import json
import os

from cumulus_lambda_functions.lib.constants import Constants

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from fastapi import APIRouter, HTTPException, Request, Response

from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class FastApiUtils:
    @staticmethod
    def get_authorization_info(request: Request):
        """
        :return:
        """
        action = request.method
        resource = request.url.path
        bearer_token = request.headers.get('Authorization', '')
        LOGGER.debug(f'raw bearer_token: {bearer_token}')
        username_part = bearer_token.split('.')[1]
        jwt_decoded = base64.standard_b64decode(f'{username_part}========'.encode()).decode()
        LOGGER.debug(f'jwt_decoded: {jwt_decoded}')
        jwt_decoded = json.loads(jwt_decoded)
        ldap_groups = jwt_decoded['cognito:groups']
        username = jwt_decoded['username']
        return {
            'username': username,
            'ldap_groups': list(set(ldap_groups)),
            'action': action,
            'resource': resource,
        }

    @staticmethod
    def get_api_base_prefix():
        return os.environ.get(Constants.DAPA_API_PREIFX_KEY) if Constants.DAPA_API_PREIFX_KEY in os.environ else WebServiceConstants.API_PREFIX
