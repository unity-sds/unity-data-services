import os
from unittest import TestCase

from cumulus_lambda_functions.lib.cognito_login.cognito_token_retriever import CognitoTokenRetriever
from cumulus_lambda_functions.lib.constants import Constants


class TestCognitoTokenRetriever(TestCase):
    def test_param_store_01(self):
        # os.environ['AWS_ACCESS_KEY_ID'] = 'dd'
        # os.environ['AWS_SECRET_ACCESS_KEY'] = 'ddd'
        # os.environ['AWS_SESSION_TOKEN'] = 'ddd'
        # os.environ['AWS_REGION'] = 'us-west-2'


        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        # os.environ[Constants.USERNAME] = 'usps_username'
        # os.environ[Constants.PASSWORD] = 'usps_password'
        os.environ[Constants.PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.CLIENT_ID] = '7a1fglm2d54eoggj13lccivp25'  # JPL Cloud
        os.environ[Constants.CLIENT_ID] = '6ir9qveln397i0inh9pmsabq1'  # MCP Test Cloud

        os.environ[Constants.COGNITO_URL] = 'https://cognito-idp.us-west-2.amazonaws.com'
        result = CognitoTokenRetriever().start()
        self.assertTrue(len(result) > 0, 'empty token')
        return
