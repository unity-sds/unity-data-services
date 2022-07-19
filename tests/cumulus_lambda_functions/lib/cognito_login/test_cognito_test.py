import unittest

from cumulus_lambda_functions.lib.cognito_login.cognito_login import CognitoLogin
from cumulus_lambda_functions.lib.utils.file_utils import FileUtils


class TestCognitoLogin(unittest.TestCase):
    def test_01(self):
        sample_login_cred = FileUtils.read_json('/Users/wphyo/Projects/unity/cumulus_lambda_functions/cognito.jpl.aws.json')  # TODO need this to be set before the test is run
        sample_login_cred = sample_login_cred['AuthParameters']
        cognito_login = CognitoLogin()\
            .with_client_id('7a1fglm2d54eoggj13lccivp25')\
            .with_cognito_url('https://cognito-idp.us-west-2.amazonaws.com')\
            .start(sample_login_cred['USERNAME'], sample_login_cred['PASSWORD'])
        self.assertNotEqual(cognito_login.token, None, 'token is None. login failed')
        self.assertNotEqual(cognito_login.token, '', 'token is None. login failed')
        return
