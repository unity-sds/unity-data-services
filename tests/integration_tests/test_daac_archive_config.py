import base64
import json
import os
from unittest import TestCase
import requests

from cumulus_lambda_functions.lib.cognito_login.cognito_login import CognitoLogin
from dotenv import load_dotenv


class TestDapaStac(TestCase):
    def setUp(self) -> None:
        super().setUp()
        load_dotenv()
        self.cognito_login = CognitoLogin() \
            .with_client_id(os.environ.get('CLIENT_ID', '')) \
            .with_cognito_url(os.environ.get('COGNITO_URL', '')) \
            .with_verify_ssl(False) \
            .start(base64.standard_b64decode(os.environ.get('USERNAME')).decode(),
                   base64.standard_b64decode(os.environ.get('PASSWORD')).decode())
        self._url_prefix = f'{os.environ.get("UNITY_URL")}/{os.environ.get("UNITY_STAGE", "sbx-uds-dapa")}'
        self.tenant = 'UDS_LOCAL_DEMO'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_COLLECTION'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.07.19.16.00'.replace('.', '')  # '2402011200'
        self.custom_metadata_body = {
            'tag': {'type': 'keyword'},
            'c_data1': {'type': 'long'},
        }
        return

    def test_01_setup_permissions(self):
        collection_url = f'{self._url_prefix}/admin/auth'
        admin_add_body = {
            "actions": ["READ", "CREATE"],
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

    def test_02_01_setup_custom_metadata_index(self):
        post_url = f'{self._url_prefix}/admin/custom_metadata/{self.tenant}?venue={self.tenant_venue}'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json=self.custom_metadata_body,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = query_result.content.decode()
        print(response_json)
        return

    def test_02_02_get_custom_metadata_fields(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/variables'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        query_result = requests.get(url=post_url,
                                     headers=headers)
        print(query_result.text)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        self.assertEqual(json.loads(query_result.text), self.custom_metadata_body, f'wrong body')
        return

    def test_01_insert(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        daac_config = {
            'daac_collection_id': f'MOCK:DAAC:modified_{self.collection_name}',
            'daac_sns_topic_arn': 'sample_sns',
            'daac_data_version': '123',
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json = daac_config,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        self.assertEqual(json.loads(query_result.text), {'message': 'inserted'}, f'wrong body')
        return

    def test_02_get(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        self.assertTrue('uds_daac_sns_arn' in query_result, f'missing uds_daac_sns_arn')
        return

    def test_03_update(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        daac_config = {
            'daac_collection_id': f'MOCK:DAAC:modified_{self.collection_name}',
            'archiving_types': [
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},
            ],
        }
        query_result = requests.post(url=post_url,
                                    headers=headers,
                                    json = daac_config,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        self.assertEqual(json.loads(query_result.text), {'message': 'updated'}, f'wrong body')
        return

    def test_04_get(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        self.assertTrue('uds_daac_sns_arn' in query_result, f'missing uds_daac_sns_arn')
        return

    def test_05_delete(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        daac_config = {
            'daac_collection_id': f'MOCK:DAAC:modified_{self.collection_name}',
        }
        query_result = requests.delete(url=post_url,
                                    headers=headers,
                                    json = daac_config,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        self.assertEqual(json.loads(query_result.text), {'message': 'deleted'}, f'wrong body')
        return

    def test_06_get(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        print(json.dumps(json.loads(query_result.text), indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        self.assertTrue('uds_daac_sns_arn' in query_result, f'missing uds_daac_sns_arn')
        return