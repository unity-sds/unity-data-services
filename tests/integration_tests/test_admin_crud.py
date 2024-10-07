import base64
import json
import os
from datetime import datetime
from unittest import TestCase

import requests
from dotenv import load_dotenv

from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin


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
        return

    def test_setup_es(self):
        es_setup_url = f'{self._url_prefix}/admin/system/es_setup/'
        print(f'es_setup_url: {es_setup_url}')
        s = requests.session()
        s.trust_env = False
        response = s.put(url=es_setup_url, headers={'Authorization': f'Bearer {self.cognito_login.token}'}, verify=False)
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        return

    def test_list_admin_list_01(self):
        collection_url = f'{self._url_prefix}/admin/auth'
        s = requests.session()
        s.trust_env = False
        print(collection_url)
        response = s.get(url=collection_url, headers={'Authorization': f'Bearer {self.cognito_login.token}'}, verify=False)
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = json.loads(response.content.decode())
        print(json.dumps(response_json, indent=4))
        return

    def test_add_admin_01(self):
        collection_url = f'{self._url_prefix}/admin/auth'
        tenant, tenant_venue = 'uds_local_test', 'DEV1'
        tenant, tenant_venue = 'MAIN_PROJECT', 'DEV'
        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{tenant}:{tenant_venue}:.*"],
            "tenant": tenant,
            # "venue": f"DEV1-{int(datetime.utcnow().timestamp())}",
            "venue": tenant_venue,
            "group_name": "Unity_Viewer"
        }
        s = requests.session()
        s.trust_env = False
        print(collection_url)
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = response.content.decode()
        print(response_json)
        return

    def test_delete_admin_01(self):
        collection_url = f'{self._url_prefix}/admin/auth'
        admin_add_body = {
            "tenant": "uds_local_test",
            "venue": "DEV1-1674680116",
            "group_name": "Unity_Viewer"
        }
        s = requests.session()
        s.trust_env = False
        response = s.delete(url=collection_url, headers={
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = response.content.decode()
        print(response_json)
        return

