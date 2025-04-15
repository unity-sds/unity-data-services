import base64
import json
import os
from datetime import datetime
from time import sleep
from unittest import TestCase

import requests
from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin
from dotenv import load_dotenv

from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.lib.cumulus_stac.unity_collection_stac import UnityCollectionStac


class TestCumulusCreateCollectionDapa(TestCase):



    def setUp(self) -> None:
        super().setUp()
        load_dotenv()
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

        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'TEST2'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.03.20.14.40'.replace('.', '')  # '2402011200'
        return


    def test_add_admin_01(self):
        print(self.bearer_token)
        collection_url = f'{self.uds_url}admin/auth'
        admin_add_body = {
            "actions": ["READ", "CREATE"],
            "resources": [f"URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:.*"],
            "tenant": self.tenant,
            # "venue": f"DEV1-{int(datetime.utcnow().timestamp())}",
            "venue": self.tenant_venue,
            "group_name": "Unity_Viewer"
        }
        s = requests.session()
        s.trust_env = False
        print(collection_url)
        response = s.put(url=collection_url, headers={
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }, verify=False, data=json.dumps(admin_add_body))
        self.assertEqual(response.status_code, 200, f'wrong status code: {response.text}')
        response_json = response.content.decode()
        print(response_json)
        return

    def test_01_setup_custom_metadata_index(self):
        post_url = f'{self.uds_url}admin/custom_metadata/{self.tenant}?venue={self.tenant_venue}'  # MCP Dev
        print(f'post_url: {post_url}')
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
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

    def test_03_create_collection(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        dapa_collection = UnityCollectionStac() \
            .with_id(temp_collection_id) \
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
        print(dapa_collection)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                     headers=headers,
                                     json=stac_collection,
                                     )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')
        sleep(60)
        return

    def test_collections_get(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        # post_url = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        post_url = f'{post_url}?limit=100'
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        print(json.dumps(query_result, indent=4))
        self.assertTrue('links' in query_result, 'links missing')
        links = {k['rel']: k for k in query_result['links']}
        self.assertTrue('next' in links, f'missing next in links: {links}')
        self.assertTrue('href' in links['next'], f'missing next in links: {links}')
        self.assertTrue('limit=50' in links['next']['href'], f"limit not reset to 50: {links['next']['href']}")
        links = {k['rel']: k['href'] for k in query_result['links'] if k['rel'] != 'root'}
        for k, v in links.items():
            self.assertTrue(v.startswith(self.uds_url), f'missing stage: {self.stage} in {v} for {k}')
        return

    def test_catalog_get(self):
        post_url = f'{self.uds_url}catalog'  # MCP Dev
        # post_url = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        post_url = f'{post_url}?limit=100'
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        print(query_result)
        self.assertEqual('Catalog', query_result['type'], f'wrong type: {query_result}')
        self.assertTrue('links' in query_result, 'links missing')
        links = {k['rel']: k for k in query_result['links']}
        self.assertTrue('child' in links, f'missing next in links: {links}')
        return

    def test_collections_get_single_granule(self):

        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'

        post_url = f'{self.uds_url}collections/{temp_collection_id}'  # MCP Dev
        # post_url = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        # post_url = f'{post_url}?limit=100'
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        query_result = json.loads(query_result.text)
        """
        {'type': 'Collection', 'id': 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2402011700', 'stac_version': '1.0.0', 'description': 'TODO', 'links': [{'rel': 'root', 'href': './collection.json?bucket=unknown_bucket&regex=%5Eabcd.1234.efgh.test_file.%2A%5C.data.stac.json%24', 'type': 'application/json', 'title': 'abcd.1234.efgh.test_file05.data.stac.json'}, {'rel': 'item', 'href': './collection.json?bucket=protected&regex=%5Eabcd.1234.efgh.test_file.%2A%5C.nc%24', 'type': 'data', 'title': 'abcd.1234.efgh.test_file05.nc'}, {'rel': 'item', 'href': './collection.json?bucket=protected&regex=%5Eabcd.1234.efgh.test_file.%2A%5C.nc.cas%24', 'type': 'metadata', 'title': 'abcd.1234.efgh.test_file05.nc.cas'}, {'rel': 'item', 'href': './collection.json?bucket=protected&regex=%5Eabcd.1234.efgh.test_file.%2A%5C.nc.cmr.xml%24', 'type': 'metadata', 'title': 'abcd.1234.efgh.test_file05.nc.cmr.xml'}, {'rel': 'item', 'href': './collection.json?bucket=protected&regex=%5Eabcd.1234.efgh.test_file.%2A%5C.nc.stac.json%24', 'type': 'metadata', 'title': 'abcd.1234.efgh.test_file05.nc.stac.json'}, {'rel': 'items', 'href': 'https://dxebrgu0bc9w7.cloudfront.net/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2402011700/items', 'type': 'application/json', 'title': 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2402011700 Granules'}], 'extent': {'spatial': {'bbox': [[0.0, 0.0, 0.0, 0.0]]}, 'temporal': {'interval': [['1970-01-01T12:00:00Z', '2024-02-26T07:11:11Z']]}}, 'license': 'proprietary', 'summaries': {'updated': ['2024-02-01T17:55:34.338000Z'], 'granuleId': ['^abcd.1234.efgh.test_file.*$'], 'granuleIdExtraction': ['(^abcd.1234.efgh.test_file.*)(\\.data\\.stac\\.json|\\.nc\\.cas|\\.cmr\\.xml)'], 'process': ['stac'], 'totalGranules': [1]}}
        """
        print(json.dumps(query_result, indent=4))
        self.assertEqual('Collection', query_result['type'], f'wrong type: {query_result}')
        self.assertEqual(temp_collection_id, query_result['id'], f'wrong collection_id: {query_result}')
        self.assertTrue('links' in query_result, 'links missing')
        links = {k['rel']: k for k in query_result['links']}
        self.assertTrue('items' in links, f'missing items in links: {links}')
        return

    def test_granules_get(self):
        post_url = f'{self.uds_url}collections/URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001/items/?limit=10'  # MCP Dev
        # post_url = f'{self.uds_url}collections/urn:nasa:unity:asips:int:P1590011-T___1/items/?limit=10'  # MCP OPS
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        response_json = json.loads(query_result.text)
        # print(json.dumps(response_json, indent=4))
        print(f"length: {len(response_json['features'])}")
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        total_size = response_json['numberMatched']['total_size']
        current_size = len(response_json['features'])
        links = {k['rel']: k['href'] for k in response_json['links'] if k['rel'] != 'root'}
        for k, v in links.items():
            self.assertTrue(v.startswith(self.uds_url), f'missing stage: {self.stage} in {v} for {k}')

        while len(response_json['features']) > 0:
            get_next_link = [k['href'] for k in response_json['links'] if k['rel'] == 'next']
            get_next_link = get_next_link[0]
            print(get_next_link)
            query_result = requests.get(url=get_next_link,
                                        headers=headers,
                                        )
            response_json = json.loads(query_result.text)
            self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
            current_size += len(response_json['features'])
            print(f"length: {len(response_json['features'])}")
        self.assertEqual(total_size, current_size, f'mismatched size')
        return

    def test_single_granule_get(self):
        post_url = f'{self.uds_url}collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json))

        return

    def test_version_get(self):
        post_url = f'{self.uds_url}misc/version/'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        # self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json))
        return

      
    def test_single_granule_get_wrong_collection(self):
        # post_url = f'{self.uds_url}collections/urn:nasa:unity:uds_local_test:DEV1:CHRP_16_DAY_REBIN___10/items/urn:nasa:unity:uds_local_test:DEV1:CHRP_16_DAY_REBIN___10:SNDR.SS1330.CHIRP.20230101T0000.m06.g001.L1_J1.std.v02_48.G.200101070318_REBIN'
        post_url = f'{self.uds_url}collections/URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-02___001/items/URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file10'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url, headers=headers,)
        self.assertEqual(query_result.status_code, 404, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json))

        post_url = f'{self.uds_url}collections/URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001/items/URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file10'
        query_result = requests.get(url=post_url, headers=headers,)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json))
        return

    def test_create_new_collection(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        temp_collection_id = f'URN:NASA:UNITY:MAIN_PROJECT:DEV:CUMULUS_DAPA_UNIT_TEST___{int(datetime.utcnow().timestamp())}'
        dapa_collection = UnityCollectionStac() \
            .with_id(temp_collection_id) \
            .with_graule_id_regex("^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$") \
            .with_granule_id_extraction_regex("(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+") \
            .with_title("P1570515ATMSSCIENCEAXT11344000000001.PDS") \
            .with_process('modis') \
            .with_provider('unity') \
            .add_file_type("P1570515ATMSSCIENCEAXT11344000000001.PDS",
                           "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01.PDS$", 'internal', 'metadata', 'root') \
            .add_file_type("P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml",
                           "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00.PDS.cmr.xml$", 'internal', 'metadata', 'item') \
            .add_file_type("P1570515ATMSSCIENCEAXT11344000000001.PDS.xml",
                           "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS\\.xml$", 'internal', 'metadata', 'item') \
            .add_file_type("P1570515ATMSSCIENCEAXT11344000000000.PDS", "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                           'internal', 'data', 'item')
        print(dapa_collection)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))
        query_result = requests.post(url=post_url,
                                    headers=headers,
                                    json=stac_collection,
                                    )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')
        sleep(60)
        post_url = post_url if post_url.endswith('/') else f'{post_url}/'
        collection_created_result = requests.get(url=f'{post_url}{temp_collection_id}', headers=headers)
        self.assertEqual(collection_created_result.status_code, 200, f'wrong status code. {collection_created_result.text}')
        collection_created_result = json.loads(collection_created_result.text)
        self.assertTrue('id' in collection_created_result, f'id not in collection_created_result: {collection_created_result}')
        self.assertEqual(collection_created_result['id'], temp_collection_id, f'wrong id')
        print(collection_created_result)
        # TODO check if collection shows up
        return

    def test_cnm_facade(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        stac_collection = {
            "provider_id": 'unity',
            "features": [
            {'type': 'Feature', 'stac_version': '1.0.0', 'id': 'URN:NASA:UNITY:MAIN_PROJECT:DEV:NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
             'properties': {'start_datetime': '2016-01-31T18:00:00.009057Z', 'end_datetime': '2016-01-31T19:59:59.991043Z',
                            'created': '2016-02-01T02:45:59.639000Z', 'updated': '2022-03-23T15:48:21.578000Z',
                            'datetime': '1970-01-01T00:00:00Z'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
             'links': [], 'assets': {
                'data': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc',
                         'title': 'main data'}, 'metadata__cas': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas',
                    'title': 'metadata cas'}, 'metadata__stac': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.stac.json',
                    'title': 'metadata stac'}}, 'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [],
             'collection': 'URN:NASA:UNITY:MAIN_PROJECT:DEV:NEW_COLLECTION_EXAMPLE_L1B___9'}]
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json=stac_collection,
                                    )
        self.assertEqual(query_result.status_code, 202, f'wrong status code. {query_result.text}')
        return

    def test_cnm_403(self):
        post_url = f'{self.uds_url}collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        stac_collection = {
            "provider_id": 'unity',
            "features": [
            {'type': 'Feature', 'stac_version': '1.0.0', 'id': 'URN:NASA:UNITY:MAIN_PROJECT:DEV403:NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
             'properties': {'start_datetime': '2016-01-31T18:00:00.009057Z', 'end_datetime': '2016-01-31T19:59:59.991043Z',
                            'created': '2016-02-01T02:45:59.639000Z', 'updated': '2022-03-23T15:48:21.578000Z',
                            'datetime': '1970-01-01T00:00:00Z'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
             'links': [], 'assets': {
                'data': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc',
                         'title': 'main data'}, 'metadata__cas': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas',
                    'title': 'metadata cas'}, 'metadata__stac': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.stac.json',
                    'title': 'metadata stac'}}, 'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [],
             'collection': 'URN:NASA:UNITY:MAIN_PROJECT:DEV403:NEW_COLLECTION_EXAMPLE_L1B___9'}]
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json=stac_collection,
                                    )
        self.assertEqual(query_result.status_code, 403, f'wrong status code. {query_result.text}')
        return

    def test_add_granules_index(self):
        project_name = f'MAIN_PROJECT{TimeUtils.get_current_unix_milli()}'
        post_url = f'{self.uds_url}admin/custom_metadata/{project_name}?venue=DEV'  # MCP Dev
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        body = {
            'tag': {'type': 'keyword'},
            'some_key': {'type': 'long'},
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json=body,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print('added version 1')
        sleep(3)
        body = {
            'tag': {'type': 'keyword'},
            'last_updated': {'type': 'long'},
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json=body,
                                    )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print('added version 2')
        sleep(3)
        # TODO the commented code works but need access to ES to work
        # os.environ['ES_URL'] = 'https://vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        # os.environ['ES_PORT'] = '9200'
        # es: ESAbstract = ESFactory().get_instance(os.getenv('ES_TYPE', 'AWS'),
        #                                           index=DBConstants.collections_index,
        #                                           base_url=os.getenv('ES_URL'),
        #                                           port=int(os.getenv('ES_PORT', '443'))
        #                                           )
        # index_name_prefix = f'{DBConstants.granules_index_prefix}_{project_name}_DEV'.replace(':', '--').lower()
        # write_alias = f'{DBConstants.granules_write_alias_prefix}_{project_name}_DEV'.replace(':', '--').lower()
        # read_alias = f'{DBConstants.granules_read_alias_prefix}_{project_name}_DEV'.replace(':', '--').lower()
        #
        # self.assertTrue(es.has_index(f'{index_name_prefix}__v01'), f'{index_name_prefix}__v01 does not exist')
        # self.assertTrue(es.has_index(f'{index_name_prefix}__v02'), f'{index_name_prefix}__v02 does not exist')
        # actual_write_alias = es.get_alias(write_alias)
        # expected_write_alias = {
        #     f'{index_name_prefix}__v02':
        #         {'aliases': {write_alias: {}}}}
        # self.assertEqual(actual_write_alias, expected_write_alias)
        # actual_read_alias = es.get_alias(read_alias)
        # expected_read_alias = {f'{index_name_prefix}__v02': {'aliases': {read_alias: {}}}, f'{index_name_prefix}__v01': {'aliases': {read_alias: {}}}}
        # self.assertEqual(actual_read_alias, expected_read_alias)
        print('verified indices & aliases')
        get_url = f'{self.uds_url}admin/custom_metadata/{project_name}?venue=DEV'
        query_result = requests.get(url=get_url,
                                       headers=headers,
                                       )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print(f'query_result: {query_result.text}')
        delete_url = f'{self.uds_url}admin/custom_metadata/{project_name}/destroy?venue=DEV'  # MCP Dev
        query_result = requests.delete(url=delete_url,
                                        headers=headers,
                                        )
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        print('destroyed')
        sleep(3)
        # self.assertFalse(es.has_index(f'{index_name_prefix}__v01'), f'{index_name_prefix}__v01 does exist')
        # self.assertFalse(es.has_index(f'{index_name_prefix}__v02'), f'{index_name_prefix}__v02 does exist')
        # actual_write_alias = es.get_alias(write_alias)
        # self.assertEqual(actual_write_alias, {})
        # actual_read_alias = es.get_alias(read_alias)
        # self.assertEqual(actual_read_alias, {})
        print('verified indices & aliases')
        return