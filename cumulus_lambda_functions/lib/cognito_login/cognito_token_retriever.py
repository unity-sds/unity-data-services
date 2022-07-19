import base64
import logging
import os

from cumulus_lambda_functions.lib.aws.aws_param_store import AwsParamStore
from cumulus_lambda_functions.lib.cognito_login.cognito_login import CognitoLogin
from cumulus_lambda_functions.lib.constants import Constants

LOGGER = logging.getLogger()


class CognitoTokenRetriever:
    def __get_username_dwssap(self):
        username = os.environ[Constants.USERNAME]
        dwssap = os.environ[Constants.PASSWORD]
        if Constants.PASSWORD_TYPE not in os.environ:
            LOGGER.debug('no PASSWORD_TYPE set in ENV. assuming PLAIN STR')
            return username, dwssap
        dwssap_type = os.environ[Constants.PASSWORD_TYPE]
        if dwssap_type == Constants.PLAIN_STR:
            LOGGER.debug('PLAIN_STR in ENV. returning PLAIN STR')
            return username, dwssap
        if dwssap_type == Constants.BASE64_STR:
            LOGGER.debug('BASE64_STR in ENV. decoding & returning')
            username = base64.standard_b64decode(username.encode('utf-8')).decode('utf-8')
            dwssap = base64.standard_b64decode(dwssap.encode('utf-8')).decode('utf-8')
            return username, dwssap
        if dwssap_type == Constants.PARAM_STORE:
            LOGGER.debug('PARAM_STORE in ENV. retrieving value from Param Store')
            username_param_store = AwsParamStore().get_param(username)
            dwssap_param_store = AwsParamStore().get_param(dwssap)
            if username_param_store is None or dwssap_param_store is None:
                raise ValueError(f'NULL username or password from Param Store. Set the value in {username} AND {dwssap}')
            return username_param_store, dwssap_param_store
        raise ValueError(f'invalid {Constants.PASSWORD_TYPE}. value: {dwssap_type}')

    def start(self):
        if Constants.UNITY_BEARER_TOKEN in os.environ:
            LOGGER.debug('found UNITY_BEARER_TOKEN. returning UNITY_BEARER_TOKEN from ENV')
            return os.environ[Constants.UNITY_BEARER_TOKEN]
        LOGGER.debug('UNITY_BEARER_TOKEN not found. preparing to login')

        missing_mandatory_env = [k for k in [Constants.CLIENT_ID, Constants.COGNITO_URL, Constants.USERNAME, Constants.PASSWORD] if k not in os.environ]
        if len(missing_mandatory_env) > 0:
            raise ValueError(f'missing mandatory ENV for login: {missing_mandatory_env}')
        username, dwssap = self.__get_username_dwssap()
        cognito_login = CognitoLogin()\
            .with_client_id(os.environ[Constants.CLIENT_ID])\
            .with_cognito_url(os.environ[Constants.COGNITO_URL])\
            .with_verify_ssl(os.environ.get(Constants.VERIFY_SSL, 'TRUE').strip().upper() == 'TRUE')\
            .start(username, dwssap)
        if cognito_login.token is None:
            raise ValueError(f'Unity Token Retrieval failed')
        return cognito_login.token
