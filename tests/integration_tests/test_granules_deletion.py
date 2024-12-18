import base64
import json
import os
from time import sleep
from unittest import TestCase

import requests
from dotenv import load_dotenv
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
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
        self.collection_name = 'AAA-03'  # 'uds_collection'  # 'sbx_collection'
        # self.collection_version = '08'.replace('.', '')  # '2402011200'
        return

    def test_01_setup_permissions(self):
        collection_url = f'{self._url_prefix}/admin/auth'
        admin_add_body = {
            "actions": ["READ", "CREATE", "DELETE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:.*"],
            "tenant": self.tenant,
            "venue": self.tenant_venue,
            "group_name": "Unity_Viewer"
        }
        s = requests.session()
        s.trust_env = False
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = response.content.decode()
        print(response_json)
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

        asset_urls = [v['href'] for k, v in response_json['features'][0]['assets'].items()]
        print(asset_urls)
        post_url = f'{self.uds_url}collections/{collection_id}/items/{deleting_granule_id}/actual'  # MCP Dev
        print(post_url)
        query_result = requests.delete(url=post_url,
                                       headers=headers,
                                       )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))
        sleep(30)
        post_url = f'{self.uds_url}collections/{collection_id}/items/'  # MCP Dev
        query_result = requests.get(url=post_url, headers=headers,)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))

        s3 = AwsS3()
        for each_url in asset_urls:
            self.assertFalse(s3.set_s3_url(each_url).exists(s3.target_bucket, s3.target_key), f'file still exists: {each_url}')
        return
