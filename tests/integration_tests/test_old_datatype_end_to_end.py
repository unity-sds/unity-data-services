import base64
import json
import os
import tempfile
from sys import argv
from time import sleep
from unittest import TestCase

import pystac
import requests
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from pystac import Link, Catalog, Asset, Item, ItemCollection

from cumulus_lambda_functions.docker_entrypoint.__main__ import choose_process

from mdps_ds_lib.lib.utils.file_utils import FileUtils

from mdps_ds_lib.lib.cumulus_stac.unity_collection_stac import UnityCollectionStac

from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin
from dotenv import load_dotenv


class TestOldDataEndToEnd(TestCase):
    # 1. setup admin for the test venue
    # 2. create a custom metadata for the venue
    # 3. create a collection
    # 4. push granules to cnm w/ custom metadata
    # 5. get granules w/ custom metadata

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
        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'SNDR-SNPP_ATMS@L1B$OUTPUT'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.03.26.14.40'.replace('.', '')  # '2402011200'
        self.granule_id = 'abcd.1234.efgh.test_file05'
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

    def test_01_create_collection(self):
        post_url = f'{self._url_prefix}/collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        dapa_collection = UnityCollectionStac() \
            .with_id(temp_collection_id) \
            .with_graule_id_regex(".*") \
            .with_granule_id_extraction_regex( "(.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title("test_file01.nc") \
            .with_process("snpp.level1") \
            .with_provider('unity') \
            .add_file_type("test_file01.nc", "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type("test_file01.nc", ".*\.nc$", 'protected', 'data', 'item') \
            .add_file_type("test_file01.nc.cas", ".*\.nc\.cas$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.cmr.xml", ".*\.cmr\.xml$", 'private', 'metadata', 'item')
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
        self.assertEqual(collection_created_result.status_code, 200,
                         f'wrong status code. {collection_created_result.text}')
        collection_created_result = json.loads(collection_created_result.text)
        self.assertEqual(collection_created_result['id'], temp_collection_id, f'wrong id')
        print(collection_created_result)
        return

    def test_02_execute_cnm(self):
        """

{"type": "Catalog", "id": "NA", "stac_version": "1.0.0", "description": "NA", "links": [{"rel": "root", "href": "/var/folders/33/xhq97d6s0dq78wg4h2smw23m0000gq/T/tmpwhti32mb/catalog.json", "type": "application/json"}, {"rel": "item", "href": "some_granules/test_file01.nc.stac.json", "type": "application/json"}]}
{'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'stac_version': '1.0.0', 'id': 'URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01', 'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000], 'c_data2': [False, True, True, False, True], 'c_data3': ['Bellman Ford'], 'start_datetime': '2016-01-31T18:00:00.009057Z', 'end_datetime': '2016-01-31T19:59:59.991043Z', 'created': '2016-02-01T02:45:59.639000Z', 'updated': '2022-03-23T15:48:21.578000Z', 'datetime': '1970-01-01T00:00:00Z'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [], 'assets': {'data': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc', 'title': 'main data'}, 'metadata__cas': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc.cas', 'title': 'metadata cas'}, 'metadata__stac': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc.stac.json', 'title': 'metadata stac'}}, 'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [], 'collection': 'URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703'}]}

        :return:
        """
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        cas_metadata = '''<?xml version="1.0" encoding="UTF-8" ?>
        <cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">
            <keyval type="scalar">
                <key>AggregateDir</key>
                <val>snppatmsl1b</val>
            </keyval>
            <keyval type="vector">
                <key>AutomaticQualityFlag</key>
                <val>Passed</val>
            </keyval>
            <keyval type="vector">
                <key>BuildId</key>
                <val>v02.56.00</val>
            </keyval>
            <keyval type="vector">
                <key>CollectionLabel</key>
                <val>L1BMw_nominal</val>
            </keyval>
            <keyval type="scalar">
                <key>DataGroup</key>
                <val>sndr</val>
            </keyval>
            <keyval type="scalar">
                <key>EndDateTime</key>
                <val>2016-01-14T11:06:00.000Z</val>
            </keyval>
            <keyval type="scalar">
                <key>EndTAI93</key>
                <val>726923169.000</val>
            </keyval>
            <keyval type="scalar">
                <key>FileFormat</key>
                <val>nc4</val>
            </keyval>
            <keyval type="scalar">
                <key>FileLocation</key>
                <val>/sYURHI</val>
            </keyval>
            <keyval type="scalar">
                <key>Filename</key>
                <val>test_file12.nc</val>
            </keyval>
            <keyval type="vector">
                <key>GranuleNumber</key>
                <val>111</val>
            </keyval>
            <keyval type="vector">
                <key>InputFiles</key>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.01.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.02.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.03.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.04.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.05.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.06.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.07.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.08.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.09.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.10.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.11.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.12.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.13.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.14.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.15.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.16.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.17.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.18.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.19.nc</val>
                <val>SNDR.SNPP.ATMS.L1A.nominal2.20.nc</val>
                <val>SNDR.SNPP.L1bMw.apf.171115000000.xml</val>
                <val>SNDR.SNPP.L1bMw.template.201217000000.nc</val>
            </keyval>
            <keyval type="scalar">
                <key>JobId</key>
                <val>f163835c-9945-472f-bee2-2bc12673569f</val>
            </keyval>
            <keyval type="scalar">
                <key>ModelId</key>
                <val>urn:npp:SnppAtmsL1b</val>
            </keyval>
            <keyval type="scalar">
                <key>NominalDate</key>
                <val>2016-01-14</val>
            </keyval>
            <keyval type="vector">
                <key>ProductName</key>
                <val>SNDR.SNPP.ATMS.20160114T1100.m06.g111.L1B.L1BMw_nominal.v03_07.D.150520120000.nc</val>
            </keyval>
            <keyval type="scalar">
                <key>ProductType</key>
                <val>SNDR_SNPP_ATMS_L1B</val>
            </keyval>
            <keyval type="scalar">
                <key>ProductionDateTime</key>
                <val>2015-05-20T12:00:00.000Z</val>
            </keyval>
            <keyval type="vector">
                <key>ProductionLocation</key>
                <val>Sounder SIPS: JPL/Caltech (Dev)</val>
            </keyval>
            <keyval type="vector">
                <key>ProductionLocationCode</key>
                <val>D</val>
            </keyval>
            <keyval type="scalar">
                <key>RequestId</key>
                <val>12566</val>
            </keyval>
            <keyval type="scalar">
                <key>StartDateTime</key>
                <val>2016-01-14T11:00:00.000Z</val>
            </keyval>
            <keyval type="scalar">
                <key>StartTAI93</key>
                <val>726922809.000</val>
            </keyval>
            <keyval type="scalar">
                <key>TaskId</key>
                <val>8c3ae101-8f7c-46c8-b5c6-63e7b6d3c8cd</val>
            </keyval>
        </cas:metadata>
        '''
        s3 = AwsS3()
        s3.set_s3_url(
            f's3://uds-sbx-cumulus-staging/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc')
        s3.upload_bytes('sample_file'.encode())
        s3.set_s3_url(
            f's3://uds-sbx-cumulus-staging/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc.cas')
        s3.upload_bytes(cas_metadata.encode())

        upload_result = {'type': 'FeatureCollection', 'features': [{
            'type': 'Feature', 'stac_version': '1.0.0',
            'id': f'{temp_collection_id}:{self.granule_id}',
            'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000], 'c_data2': [False, True, True, False, True],
                           'c_data3': ['Bellman Ford'], 'start_datetime': '2016-01-31T18:00:00.009057Z',
                           'end_datetime': '2016-01-31T19:59:59.991043Z', 'created': '2016-02-01T02:45:59.639000Z',
                           'updated': '2022-03-23T15:48:21.578000Z', 'datetime': '1970-01-01T00:00:00Z'},
            'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [],
            'assets': {
                f'{self.granule_id}.nc': {
                'href': f's3://uds-sbx-cumulus-staging/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc',
                'title': f'{self.granule_id}.nc',
                'roles': ['data'],
                },
                f'{self.granule_id}.nc.cas': {
                'href': f's3://uds-sbx-cumulus-staging/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc.cas',
                'title': f'{self.granule_id}.nc.cas',
                'roles': ['metadata'],
                },
            },
            'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [],
            'collection': temp_collection_id}]}

        os.environ['PASSWORD_TYPE'] = 'BASE64'
        os.environ['DAPA_API'] = os.environ.get("UNITY_URL")
        os.environ['DAPA_API_PREIFX_KEY'] = os.environ.get("UNITY_STAGE", "sbx-uds-dapa")

        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'unity'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'
        # os.environ['DELAY_SECOND'] = '125'
        # os.environ['REPEAT_TIMES'] = '2'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('CATALOG')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            input_file_path = os.path.join(tmp_dir_name, 'uploaded_files.json')
            FileUtils.write_json(input_file_path, upload_result)
            os.environ['UPLOADED_FILES_JSON'] = input_file_path
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            catalog_result_str = choose_process()
            catalog_result = json.loads(catalog_result_str)
            print(catalog_result)
            self.assertTrue(isinstance(catalog_result, list))
            catalog_result = catalog_result[0]
            self.assertTrue('cataloging_request_status' in catalog_result, f'missing cataloging_request_status')
            self.assertTrue('status_result' in catalog_result, f'missing status_result')
            self.assertEqual(catalog_result['cataloging_request_status'], {'message': 'processing'}, f'mismatched cataloging_request_status value')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
            # TODO update this after it is deployed to MCP Test
            status_result = catalog_result['status_result']

            # self.assertTrue('cataloged' in status_result, f'missing cataloged')
            self.assertTrue('missing_granules' in status_result, f'missing missing_granules')
            self.assertTrue('registered_granules' in status_result, f'missing registered_granules')
            # self.assertTrue(isinstance(status_result['cataloged'], bool),
            #                 f'cataloged is not boolean: {status_result["cataloged"]}')
        return

    def test_03_retrieve_granule(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?limit=2'
        # post_url = f'{self._url_prefix}/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items?limit=2&offset=URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02'
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        print(response_json)
        self.assertTrue(len(response_json['features']) > 0, f'empty granules. Need collections to compare')
        for each_feature in response_json['features']:
            stac_item = pystac.Item.from_dict(each_feature)
            validation_result = stac_item.validate()
            self.assertTrue(isinstance(validation_result, list),
                            f'wrong validation for : {json.dumps(each_feature, indent=4)}. details: {validation_result}')
        return
