from unittest import TestCase
import base64
import json
import os
import tempfile
from datetime import datetime
from sys import argv
from unittest import TestCase

import requests
from mdps_ds_lib.lib.aws.aws_cognito import AwsCognito
from mdps_ds_lib.lib.cumulus_stac.unity_collection_stac import UnityCollectionStac

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
from dotenv import load_dotenv
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin
from mdps_ds_lib.lib.utils.file_utils import FileUtils
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stage_in_out.upoad_granules_factory import UploadGranulesFactory
from pystac import Catalog, Asset, Link, ItemCollection, Item



class TestUserGroupAA(TestCase):
    """
    Steps:

    # Admin points to a:x a:y b:x b:y with CRUD
    # MMM points to a:x as CRUD, b:y as R
    # NNN points to a:y as R and b:x as CRUD

    # Add wphyo to Admin
    # Create 1 collection on all 4 combo
    # remove wphyo from Admin
    # Add wphyo to MMM
    # Try adding a new collection to a:x - success
    # Try adding a new collection to a:y - failure
    # Try adding a new collection to b:x - failure
    # Try adding a new collection to b:y - failure
    # Try getting a collecion from a:x - success
    # Try getting a collecion from a:y - failure
    # Try getting a collecion from b:y - failure
    # Try getting a collecion from b:y - success
    # Remove wphyo from MMM
    # Add wphyo to NNN
    # Try adding a new collection to a:x - failure
    # Try adding a new collection to a:y - failure
    # Try adding a new collection to b:x - success
    # Try adding a new collection to b:y - failure
    # Try getting a collecion from a:x - failure
    # Try getting a collecion from a:y - success
    # Try getting a collecion from b:y - success
    # Try getting a collecion from b:y - failure
    # Remove wphyo from NNN
    # Add wphyo to Admin (which is original)

    """
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
        self.sample_user = 'wphyo'
        self.tenant_a, self.tenant_b = 'AAA', 'BBB'
        self.tenant_venue_x, self.tenant_venue_y = 'XXX', 'YYY'
        self.group_admin, self.group_m, self.group_n = 'Unity_Viewer', 'MMM', 'NNN'
        self.collection_name, self.collection_version = 'UNIT_TEST', '001'

        self.cognito = AwsCognito(os.environ.get("COGNITO_USER_POOL_ID"))

        return



    def test_add_admin_group_00(self):
        result = self.cognito.add_group(self.group_m)
        result = self.cognito.add_group(self.group_n)
        result = self.cognito.remove_user_from_group(self.sample_user, self.group_m)
        result = self.cognito.remove_user_from_group(self.sample_user, self.group_n)
        result = self.cognito.add_user_to_group(self.sample_user, self.group_admin)
        return

    def test_add_admin(self):
        collection_url = f'{self.uds_url}admin/auth'
        print(collection_url)

        s = requests.session()
        s.trust_env = False

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:.*"],
            "tenant": self.tenant_a,
            "venue": self.tenant_venue_x,
            "group_name": self.group_admin
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:.*"],
            "tenant": self.tenant_a,
            "venue": self.tenant_venue_y,
            "group_name": self.group_admin
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:.*"],
            "tenant": self.tenant_b,
            "venue": self.tenant_venue_x,
            "group_name": self.group_admin
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:.*"],
            "tenant": self.tenant_b,
            "venue": self.tenant_venue_y,
            "group_name": self.group_admin
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())
        return

    def test_add_m(self):
        collection_url = f'{self.uds_url}admin/auth'
        print(collection_url)

        s = requests.session()
        s.trust_env = False

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:.*"],
            "tenant": self.tenant_a,
            "venue": self.tenant_venue_x,
            "group_name": self.group_m
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        admin_add_body = {
            "actions": ["READ"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:.*"],
            "tenant": self.tenant_b,
            "venue": self.tenant_venue_y,
            "group_name": self.group_m
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())
        return

    def test_add_n(self):
        collection_url = f'{self.uds_url}admin/auth'
        print(collection_url)

        s = requests.session()
        s.trust_env = False

        admin_add_body = {
            "actions": ["READ"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:.*"],
            "tenant": self.tenant_a,
            "venue": self.tenant_venue_y,
            "group_name": self.group_n
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:.*"],
            "tenant": self.tenant_b,
            "venue": self.tenant_venue_x,
            "group_name": self.group_n
        }
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        print(response.content.decode())

        return

    def test_main_create_collection_all_4_tenant_venue(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        dapa_collection = UnityCollectionStac() \
            .with_graule_id_regex("^test_file.*$") \
            .with_granule_id_extraction_regex("(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title("test_file01.nc") \
            .with_process('stac') \
            .with_provider('unity') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'protected', 'data', 'item') \
            .add_file_type("test_file01.nc.cas", "^test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.cmr.xml", "^test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.stac.json", "^test_file.*\\.nc.stac.json$", 'protected', 'metadata', 'item')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')
        return

    def test_update_user_group_01(self):
        result = self.cognito.remove_user_from_group(self.sample_user, self.group_admin)
        result = self.cognito.add_user_to_group(self.sample_user, self.group_m)
        return

    def test_add_get_collections_01(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        dapa_collection = UnityCollectionStac() \
            .with_graule_id_regex("^test_file.*$") \
            .with_granule_id_extraction_regex("(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title("test_file01.nc") \
            .with_process('stac') \
            .with_provider('unity') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'protected', 'data', 'item') \
            .add_file_type("test_file01.nc.cas", "^test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.cmr.xml", "^test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.stac.json", "^test_file.*\\.nc.stac.json$", 'protected', 'metadata', 'item')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))
        return

    def test_update_user_group_02(self):
        result = self.cognito.remove_user_from_group(self.sample_user, self.group_m)
        result = self.cognito.add_user_to_group(self.sample_user, self.group_n)
        return

    def test_add_get_collections_02(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        dapa_collection = UnityCollectionStac() \
            .with_graule_id_regex("^test_file.*$") \
            .with_granule_id_extraction_regex("(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title("test_file01.nc") \
            .with_process('stac') \
            .with_provider('unity') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'protected', 'data', 'item') \
            .add_file_type("test_file01.nc.cas", "^test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.cmr.xml", "^test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.stac.json", "^test_file.*\\.nc.stac.json$", 'protected', 'metadata', 'item')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        dapa_collection.with_id(temp_collection_id)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_a}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_x}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant_b}:{self.tenant_venue_y}:{self.collection_name}___{self.collection_version}'
        query_result = requests.get(url=f'{post_url}{temp_collection_id}/', headers=headers)
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')
        print(json.loads(query_result.text))
        return

    def test_update_user_group_03(self):
        result = self.cognito.remove_user_from_group(self.sample_user, self.group_n)
        result = self.cognito.add_user_to_group(self.sample_user, self.group_admin)
        result = self.cognito.delete_group(self.group_m)
        result = self.cognito.delete_group(self.group_n)
        return
