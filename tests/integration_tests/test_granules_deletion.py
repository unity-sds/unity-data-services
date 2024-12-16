import base64
import json
import os
from unittest import TestCase

import requests
from dotenv import load_dotenv
from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin


class TestGranulesDeletion(TestCase):
    def setUp(self) -> None:
        super().setUp()
        load_dotenv()
        self._url_prefix = f'{os.environ.get("UNITY_URL")}/{os.environ.get("UNITY_STAGE", "sbx-uds-dapa")}'
        self.cognito_login = CognitoLogin() \
            .with_client_id(os.environ.get('CLIENT_ID', '')) \
            .with_cognito_url(os.environ.get('COGNITO_URL', '')) \
            .with_verify_ssl(False) \
            .start(base64.standard_b64decode(os.environ.get('USERNAME')).decode(),
                   base64.standard_b64decode(os.environ.get('PASSWORD')).decode())
        self.bearer_token = self.cognito_login.token
        self.stage = os.environ.get("UNITY_URL").split('/')[-1]
        self.uds_url = f'{os.environ.get("UNITY_URL")}/{os.environ.get("UNITY_STAGE", "sbx-uds-dapa")}/'
        self.custom_metadata_body = {
            'tag': {'type': 'keyword'},
            'c_data1': {'type': 'long'},
            'c_data2': {'type': 'boolean'},
            'c_data3': {'type': 'keyword'},
        }

        self.tenant = 'UDS_LOCAL_TEST_3'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'AAA-04'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '08'.replace('.', '')  # '2402011200'
        return

    def test_delete_all(self):
        collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___001'
        post_url = f'{self.uds_url}collections/{collection_id}/items/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))
        self.assertTrue(len(response_json['features']) > 0, f'empty collection :(')
        deleting_granule_id = response_json['features'][0]['id']

        post_url = f'{self.uds_url}collections/{collection_id}/items/{deleting_granule_id}'  # MCP Dev
        print(post_url)
        query_result = requests.delete(url=post_url,
                                       headers=headers,
                                       )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))

        post_url = f'{self.uds_url}collections/{collection_id}/items/'  # MCP Dev
        query_result = requests.get(url=post_url, headers=headers,)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))
        return
