import json
import logging

import requests

from cumulus_lambda_functions.lib.json_validator import JsonValidator

LOGGER = logging.getLogger()

COGNITO_RESULT_SCHEMA = {
    'type': 'object',
    'required': ['AuthenticationResult'],
    'properties': {
        'AuthenticationResult': {
            'type': 'object',
            'required': ['AccessToken', 'ExpiresIn', 'IdToken'],
            'properties': {
                'AccessToken': {'type': 'string'},
                'ExpiresIn': {'type': 'number'},
                'IdToken': {'type': 'string'},
                'RefreshToken': {'type': 'string'},
                'TokenType': {'type': 'string'},
            }
        }
    }
}


class CognitoLogin:
    def __init__(self):
        self.__verify_ssl = True
        self.__client_id = None
        self.__cognito_url = None
        self.__token = ''

    @property
    def verify_ssl(self):
        return self.__verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, val):
        """
        :param val:
        :return: None
        """
        self.__verify_ssl = val
        return

    @property
    def client_id(self):
        return self.__client_id

    @client_id.setter
    def client_id(self, val):
        """
        :param val:
        :return: None
        """
        self.__client_id = val
        return

    @property
    def cognito_url(self):
        return self.__cognito_url

    @cognito_url.setter
    def cognito_url(self, val):
        """
        :param val:
        :return: None
        """
        self.__cognito_url = val
        return

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, val):
        """
        :param val:
        :return: None
        """
        self.__token = val
        return

    def with_client_id(self, client_id: str):
        self.client_id = client_id
        return self

    def with_cognito_url(self, cognito_url: str):
        self.cognito_url = cognito_url
        return self

    def with_verify_ssl(self, verify_ssl: bool):
        self.verify_ssl = verify_ssl
        return self

    def start(self, username: str, dwssap: str):
        """
curl -X POST --data @cognito.jpl.aws.json
-H 'X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth'
-H 'Content-Type: application/x-amz-json-1.1' "https://cognito-idp.us-west-2.amazonaws.com/"|jq


        :param username:
        :param dwssap:
        :return:
        """
        if self.__client_id is None or self.__cognito_url is None:
            raise ValueError(f'missing client_id or cognito_url. set them first')
        header = {
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
            'Content-Type': 'application/x-amz-json-1.1',
        }
        login_body = {
            'AuthParameters': {
                'USERNAME': username,
                'PASSWORD': dwssap,
            },
            'AuthFlow': 'USER_PASSWORD_AUTH',
            'ClientId': self.__client_id
        }
        response = requests.post(url=self.__cognito_url, headers=header, verify=self.__verify_ssl,
                                 data=json.dumps(login_body))
        if response.status_code > 400:
            raise RuntimeError(
                f'Cognito ends in error. status_code: {response.status_code}. url: {self.__cognito_url}. details: {response.text}')
        login_result = json.loads(response.content.decode('utf-8'))
        result = JsonValidator(COGNITO_RESULT_SCHEMA).validate(login_result)
        if result is not None:
            raise ValueError(f'pds metadata has validation errors: {result}')
        self.__token = login_result['AuthenticationResult']['AccessToken']
        return self
