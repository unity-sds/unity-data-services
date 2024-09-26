import base64
import json
import os
from unittest import TestCase

import pystac
import requests
from dotenv import load_dotenv

from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin


class TestDapaStac(TestCase):
    def test_collection_01(self):
        load_dotenv()
        cognito_login = CognitoLogin()\
            .with_client_id(os.environ.get('CLIENT_ID', ''))\
            .with_cognito_url(os.environ.get('COGNITO_URL', ''))\
            .with_verify_ssl(False)\
            .start(base64.standard_b64decode(os.environ.get('USERNAME')).decode(), base64.standard_b64decode(os.environ.get('PASSWORD')).decode())
        collection_url = f'{os.environ.get("UNITY_URL")}/am-uds-dapa/collections'
        response = requests.get(url=collection_url, headers={'Authorization': f'Bearer {cognito_login.token}'}, verify=False)
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = json.loads(response.content.decode())
        self.assertTrue(len(response_json['features']) > 0, f'empty collections. Need collections to compare')
        for each_feature in response_json['features']:
            validation_result = pystac.Collection.from_dict(each_feature).validate()
            self.assertTrue(isinstance(validation_result, list), f'wrong validation for : {json.dumps(each_feature, indent=4)}. details: {validation_result}')
        return

    def test_granules_01(self):
        load_dotenv()
        cognito_login = CognitoLogin()\
            .with_client_id(os.environ.get('CLIENT_ID', ''))\
            .with_cognito_url(os.environ.get('COGNITO_URL', ''))\
            .with_verify_ssl(False)\
            .start(base64.standard_b64decode(os.environ.get('USERNAME')).decode(), base64.standard_b64decode(os.environ.get('PASSWORD')).decode())
        collection_url = f'{os.environ.get("UNITY_URL")}/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items'
        response = requests.get(url=collection_url, headers={'Authorization': f'Bearer {cognito_login.token}'}, verify=False)
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = json.loads(response.content.decode())
        self.assertTrue(len(response_json['features']) > 0, f'empty granules. Need collections to compare')
        for each_feature in response_json['features']:
            validation_result = pystac.Item.from_dict(each_feature).validate()
            self.assertTrue(isinstance(validation_result, list), f'wrong validation for : {json.dumps(each_feature, indent=4)}. details: {validation_result}')
        return
