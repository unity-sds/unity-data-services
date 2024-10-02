import base64
import json
import os
import tempfile
from sys import argv
from time import sleep
from unittest import TestCase

import pystac
import requests
from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3

from cumulus_lambda_functions.lib.time_utils import TimeUtils
from pystac import Link, Catalog, Asset, Item, ItemCollection

from cumulus_lambda_functions.docker_entrypoint.__main__ import choose_process

from cumulus_lambda_functions.lib.utils.file_utils import FileUtils

from cumulus_lambda_functions.cumulus_stac.unity_collection_stac import UnityCollectionStac

from cumulus_lambda_functions.lib.cognito_login.cognito_login import CognitoLogin
from dotenv import load_dotenv


class TestCustomMetadataEndToEnd(TestCase):
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
        self.tenant = 'UDS_MY_LOCAL_ARCHIVE_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_UNIT_COLLECTION'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.08.29.06.44'.replace('.', '')  # '2402011200'

        self.custom_metadata_body = {
            'tag': {'type': 'keyword'},
            'c_data1': {'type': 'long'},
            'c_data2': {'type': 'boolean'},
            'c_data3': {'type': 'keyword'},
            'soil10': {
                "properties": {
                    "0_0": {"type": "integer"},
                    "0_1": {"type": "integer"},
                    "0_2": {"type": "integer"},
                }
            }
        }
        self.granule_id = 'abcd.1234.efgh.test_file-24.08.13.13.53'
        self.s3_bucket = 'unity-dev-unity-william-test-11'  # 'unity-dev-unity-william-test-11'  # uds-sbx-cumulus-staging
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

    def test_03_pre_insert_500_response(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        daac_config = {
            'daac_collection_id': f'DAAC:MOCK:{self.collection_name}',
            'daac_sns_topic_arn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns',
            'daac_data_version': '9098',
            'archiving_types': [
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},
            ],
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json = daac_config,
                                    )
        print(query_result.text)
        self.assertEqual(query_result.status_code, 500, f'wrong status code. {query_result.text}')
        self.assertTrue('missing version in collection ID' in query_result.text, f'wrong error message: {query_result.text}')
        return
    def test_03_pre_insert(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive'  # MCP Dev
        print(post_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cognito_login.token}',
        }
        daac_config = {
            'daac_collection_id': f'DAAC:MOCK:{self.collection_name}',
            'daac_sns_topic_arn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns',
            'daac_data_version': '9098',
            'archiving_types': [
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},
            ],
        }
        query_result = requests.put(url=post_url,
                                    headers=headers,
                                    json = daac_config,
                                    )
        print(query_result.text)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        self.assertEqual(json.loads(query_result.text), {'message': 'inserted'}, f'wrong body')
        return

    def test_03_create_collection(self):
        post_url = f'{self._url_prefix}/collections/'  # MCP Dev
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        print(post_url)
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        dapa_collection = UnityCollectionStac() \
            .with_id(temp_collection_id) \
            .with_graule_id_regex("^abcd.1234.efgh.test_file.*$") \
            .with_granule_id_extraction_regex("(^abcd.1234.efgh.test_file.*)(\\.data\\.stac\\.json|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title(f"{self.granule_id}.data.stac.json") \
            .with_process('stac') \
            .with_provider('unity') \
            .add_file_type(f"{self.granule_id}.data.stac.json", "^abcd.1234.efgh.test_file.*\\.data.stac.json$", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type(f"{self.granule_id}.nc", "^abcd.1234.efgh.test_file.*\\.nc$", 'protected', 'data', 'item') \
            .add_file_type(f"{self.granule_id}.nc.cas", "^abcd.1234.efgh.test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
            .add_file_type(f"{self.granule_id}.nc.cmr.xml", "^abcd.1234.efgh.test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
            .add_file_type(f"{self.granule_id}.nc.stac.json", "^abcd.1234.efgh.test_file.*\\.nc.stac.json$", 'protected', 'metadata', 'item')
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

    def test_04_upload_sample_granule(self):
        custom_metadata = {
            'tag': '#sample',
            'c_data1': [1, 10, 10**2, 10**3],
            'c_data2': [False, True, True, False, True],
            'c_data3': ['Bellman Ford'],
            'soil10': {
                "0_0": 0,
                "0_1": 1,
                "0_2": 0,
            }
        }
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        os.environ['VERIFY_SSL'] = 'FALSE'

        os.environ['COLLECTION_ID'] = temp_collection_id
        os.environ['STAGING_BUCKET'] = self.s3_bucket

        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        # os.environ['GRANULES_UPLOAD_TYPE'] = 'UPLOAD_S3_BY_STAC_CATALOG'
        # defaulted to this value

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('UPLOAD')

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['UPLOAD_DIR'] = ''  # not needed
            os.environ['CATALOG_FILE'] = os.path.join(tmp_dir_name, 'catalog.json')
            os.environ['OUTPUT_DIRECTORY'] = os.path.join(tmp_dir_name, 'output_dir')
            FileUtils.mk_dir_p(os.environ.get('OUTPUT_DIRECTORY'))
            granules_dir = os.path.join(tmp_dir_name, 'some_granules')
            FileUtils.mk_dir_p(granules_dir)
            with open(os.path.join(granules_dir, f'{self.granule_id}.data.stac.json'), 'w') as ff:
                ff.write('sample_file')
            with open(os.path.join(granules_dir, f'{self.granule_id}.nc.cas'), 'w') as ff:
                ff.write('''<?xml version="1.0" encoding="UTF-8" ?>
                <cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">
                    <keyval type="scalar">
                        <key>AggregateDir</key>
                        <val>snppatmsl1a</val>
                    </keyval>
                    <keyval type="vector">
                        <key>AutomaticQualityFlag</key>
                        <val>Passed</val>
                    </keyval>
                    <keyval type="vector">
                        <key>BuildId</key>
                        <val>v01.43.00</val>
                    </keyval>
                    <keyval type="vector">
                        <key>CollectionLabel</key>
                        <val>L1AMw_nominal2</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>DataGroup</key>
                        <val>sndr</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>EndDateTime</key>
                        <val>2016-01-14T10:06:00.000Z</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>EndTAI93</key>
                        <val>726919569.000</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>FileFormat</key>
                        <val>nc4</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>FileLocation</key>
                        <val>/pge/out</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>Filename</key>
                        <val>SNDR.SNPP.ATMS.L1A.nominal2.02.nc</val>
                    </keyval>
                    <keyval type="vector">
                        <key>GranuleNumber</key>
                        <val>101</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>JobId</key>
                        <val>f163835c-9945-472f-bee2-2bc12673569f</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>ModelId</key>
                        <val>urn:npp:SnppAtmsL1a</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>NominalDate</key>
                        <val>2016-01-14</val>
                    </keyval>
                    <keyval type="vector">
                        <key>ProductName</key>
                        <val>SNDR.SNPP.ATMS.20160114T1000.m06.g101.L1A.L1AMw_nominal2.v03_15_00.D.201214135000.nc</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>ProductType</key>
                        <val>SNDR_SNPP_ATMS_L1A</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>ProductionDateTime</key>
                        <val>2020-12-14T13:50:00.000Z</val>
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
                        <val>1215</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>StartDateTime</key>
                        <val>2016-01-14T10:00:00.000Z</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>StartTAI93</key>
                        <val>726919209.000</val>
                    </keyval>
                    <keyval type="scalar">
                        <key>TaskId</key>
                        <val>8c3ae101-8f7c-46c8-b5c6-63e7b6d3c8cd</val>
                    </keyval>
                </cas:metadata>''')
            stac_item = Item(id=self.granule_id,
                             geometry={
                                 "type": "Point",
                                 "coordinates": [0.0, 0.0]
                             },
                             bbox=[0.0, 0.0, 0.0, 0.0],
                             datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                             properties={
                                 **custom_metadata,
                                 "start_datetime": "2016-01-31T18:00:00.009057Z",
                                 "end_datetime": "2016-01-31T19:59:59.991043Z",
                                 "created": "2016-02-01T02:45:59.639000Z",
                                 "updated": "2022-03-23T15:48:21.578000Z",
                                 "datetime": "2022-03-23T15:48:19.079000Z"
                             },
                             href=os.path.join('some_granules', f'{self.granule_id}.nc.stac.json'),
                             collection=temp_collection_id,
                             assets={
                                 f'{self.granule_id}.data.stac.json': Asset(os.path.join('.', f'{self.granule_id}.data.stac.json'), title=f'{self.granule_id}.data.stac.json', roles=['data']),
                                 f'{self.granule_id}.nc.cas': Asset(os.path.join('.', f'{self.granule_id}.nc.cas'), title=f'{self.granule_id}.nc.cas', roles=['metadata']),
                                 f'{self.granule_id}.nc.stac.json': Asset(os.path.join('.', f'{self.granule_id}.nc.stac.json'), title=f'{self.granule_id}.nc.stac.json', roles=['metadata']),
                             })
            with open(os.path.join(granules_dir, f'{self.granule_id}.nc.stac.json'), 'w') as ff:
                ff.write(json.dumps(stac_item.to_dict(False, False)))
            catalog = Catalog(
                id='NA',
                description='NA')
            catalog.set_self_href(os.environ['CATALOG_FILE'])
            catalog.add_link(
                Link('item', os.path.join('some_granules', f'{self.granule_id}.nc.stac.json'), 'application/json'))
            print(json.dumps(catalog.to_dict(False, False)))
            with open(os.environ['CATALOG_FILE'], 'w') as ff:
                ff.write(json.dumps(catalog.to_dict(False, False)))

            upload_result_str = choose_process()
            upload_result = json.loads(upload_result_str)
            print(upload_result)
            self.assertTrue('type' in upload_result, 'missing type')
            self.assertEqual(upload_result['type'], 'Catalog', 'missing type')
            upload_result = Catalog.from_dict(upload_result)
            child_links = [k.href for k in upload_result.get_links(rel='item')]
            self.assertEqual(len(child_links), 2, f'wrong length: {child_links}')
            self.assertTrue(FileUtils.file_exist(child_links[0]), f'missing file: {child_links[0]}')
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[0]))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), 1,
                             f'wrong length: {successful_feature_collection}')

            self.assertTrue(FileUtils.file_exist(child_links[1]), f'missing file: {child_links[1]}')
            failed_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[1]))
            failed_feature_collection = list(failed_feature_collection.items)
            self.assertEqual(len(failed_feature_collection), 0, f'wrong length: {failed_feature_collection}')

            upload_result = successful_feature_collection[0].to_dict(False, False)
            print(f'example feature: {upload_result}')
            self.assertTrue('assets' in upload_result, 'missing assets')
            self.assertTrue(f'{self.granule_id}.nc.cas' in upload_result['assets'], 'missing assets#metadata__cas')
            self.assertTrue('href' in upload_result['assets'][f'{self.granule_id}.nc.cas'], 'missing assets#metadata__cas#href')
            self.assertTrue(upload_result['assets'][f'{self.granule_id}.nc.cas']['href'].startswith(
                f's3://{os.environ["STAGING_BUCKET"]}/{os.environ["COLLECTION_ID"]}/'))
            self.assertTrue(f'{self.granule_id}.data.stac.json' in upload_result['assets'], 'missing assets#data')
            self.assertTrue('href' in upload_result['assets'][f'{self.granule_id}.data.stac.json'], 'missing assets#data#href')
            self.assertTrue(upload_result['assets'][f'{self.granule_id}.data.stac.json']['href'].startswith(
                f's3://{os.environ["STAGING_BUCKET"]}/{os.environ["COLLECTION_ID"]}/'))
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_05_execute_cnm(self):
        """

{"type": "Catalog", "id": "NA", "stac_version": "1.0.0", "description": "NA", "links": [{"rel": "root", "href": "/var/folders/33/xhq97d6s0dq78wg4h2smw23m0000gq/T/tmpwhti32mb/catalog.json", "type": "application/json"}, {"rel": "item", "href": "some_granules/test_file01.nc.stac.json", "type": "application/json"}]}
{'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'stac_version': '1.0.0', 'id': 'URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01', 'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000], 'c_data2': [False, True, True, False, True], 'c_data3': ['Bellman Ford'], 'start_datetime': '2016-01-31T18:00:00.009057Z', 'end_datetime': '2016-01-31T19:59:59.991043Z', 'created': '2016-02-01T02:45:59.639000Z', 'updated': '2022-03-23T15:48:21.578000Z', 'datetime': '1970-01-01T00:00:00Z'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [], 'assets': {'data': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc', 'title': 'main data'}, 'metadata__cas': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc.cas', 'title': 'metadata cas'}, 'metadata__stac': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703/URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703:test_file01/test_file01.nc.stac.json', 'title': 'metadata stac'}}, 'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [], 'collection': 'URN:NASA:UNITY:uds_sandbox:dev:sbx_collection___70112703'}]}

        :return:
        """
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        upload_result = {'type': 'FeatureCollection', 'features': [{
            'type': 'Feature', 'stac_version': '1.0.0',
            'id': f'{temp_collection_id}:{self.granule_id}',
            'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000], 'c_data2': [False, True, True, False, True],
                           'c_data3': ['Bellman Ford'], 'start_datetime': '2016-01-31T18:00:00.009057Z',
                           'end_datetime': '2016-01-31T19:59:59.991043Z', 'created': '2016-02-01T02:45:59.639000Z',
                           'updated': '2022-03-23T15:48:21.578000Z', 'datetime': '1970-01-01T00:00:00Z'},
            'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [],
            'assets': {
                f'{self.granule_id}.data.stac.json': {
                'href': f's3://{self.s3_bucket}/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.data.stac.json',
                'title': f'{self.granule_id}.data.stac.json',
                'roles': ['data'],
                },
                f'{self.granule_id}.nc.cas': {
                'href': f's3://{self.s3_bucket}/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc.cas',
                'title': f'{self.granule_id}.nc.cas',
                'roles': ['metadata'],
                },
                f'{self.granule_id}.nc.stac.json': {
                'href': f's3://{self.s3_bucket}/{temp_collection_id}/{temp_collection_id}:{self.granule_id}/{self.granule_id}.nc.stac.json',
                'title': f'{self.granule_id}.nc.stac.json',
                'roles': ['metadata'],
                }
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

    def test_06_retrieve_granule(self):
        self.collection_version = '24.08.29.09.00'.replace('.', '')  # '2402011200'
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?limit=20'
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
        print(json.dumps(response_json, indent=4))
        self.assertTrue(len(response_json['features']) > 0, f'empty granules. Need collections to compare')
        has_item = False
        for each_feature in response_json['features']:
            stac_item = pystac.Item.from_dict(each_feature)
            if self.granule_id not in stac_item.id:
                continue
            has_item = True
            print(json.dumps(each_feature, indent=4))
            validation_result = stac_item.validate()
            self.assertTrue(isinstance(validation_result, list),
                            f'wrong validation for : {json.dumps(each_feature, indent=4)}. details: {validation_result}')
            self.assertTrue('c_data3' in stac_item.properties, f'missing custom_metadata: {each_feature}')
        self.assertTrue(has_item, f'missing item: {json.dumps(response_json, indent=4)}')
        return


    def test_06_01_retrieve_granule_filter(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?filter=soil10::0_0 >= 0 AND end_datetime >= \'2016-01-31T11:11:11.000001Z\''
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        print(json.dumps(response_json, indent=4))
        self.assertTrue(len(response_json['features']) > 0, f'empty granules. Need collections to compare')
        for each_feature in response_json['features']:
            stac_item = pystac.Item.from_dict(each_feature)
            validation_result = stac_item.validate()
            self.assertTrue(isinstance(validation_result, list),
                            f'wrong validation for : {json.dumps(each_feature, indent=4)}. details: {validation_result}')
            self.assertTrue('c_data3' in stac_item.properties, f'missing custom_metadata: {each_feature}')
        return

    def test_06_02_retrieve_granule_filter_no_result(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?filter=soil10::0_0 >= 0 AND end_datetime >= \'2016-01-31T20:11:11.000001Z\''
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        print(response_json)
        self.assertTrue(len(response_json['features']) == 0, f'empty granules. Need collections to compare')
        return

    def test_06_03_retrieve_granule_filter_no_result(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?filter=soil10::0_0 >= 1 AND end_datetime >= \'2016-01-31T11:11:11.000001Z\''
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.get(url=post_url,
                                    headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        print(response_json)
        self.assertTrue(len(response_json['features']) == 0, f'empty granules. Need collections to compare')
        return

    def test_07_check_cnm_response(self):
        os.environ['STAGING_BUCKET'] = self.s3_bucket
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        s3 = AwsS3()
        child_files = [k for k in s3.get_child_s3_files(os.environ['STAGING_BUCKET'], f'{temp_collection_id}/{temp_collection_id}:{self.granule_id}')]
        cnm_response = [k for k in child_files if k[0].endswith('.cnm.json')]
        self.assertEqual(len(cnm_response), 1)
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            local_file_path = s3.set_s3_url(f's3://{os.environ["STAGING_BUCKET"]}/{cnm_response[0][0]}').download(tmp_dir_name)
            cnm_response = FileUtils.read_json(local_file_path)
            # NOTE: CNM response do not have collection version
            self.assertEqual(cnm_response['collection'], f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}', f'wrong collection ID')
        return

    def test_08_manual_archive(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        temp_granule_id = f'{temp_collection_id}:{self.granule_id}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/archive/{temp_granule_id}'
        # post_url = f'{self._url_prefix}/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items?limit=2&offset=URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02'
        print(post_url)
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.put(url=post_url,
                                    headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        print(json.dumps(response_json, indent=4))
        return

    def test_01_pagination(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        post_url = f'{self._url_prefix}/collections/{temp_collection_id}/items?limit=2'
        headers = {
            'Authorization': f'Bearer {self.cognito_login.token}',
            'Content-Type': 'application/json',
        }
        query_result = requests.get(url=post_url, headers=headers)
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        response_json = json.loads(query_result.content.decode())
        links = {k['rel']: k for k in response_json['links']}
        print(response_json)
        while 'next' in links:
            print(f"{links['next']}")
            post_url = links['next']['href']
            query_result = requests.get(url=post_url, headers=headers)
            self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
            response_json = json.loads(query_result.content.decode())
            links = {k['rel']: k for k in response_json['links']}
            print(response_json)
        return
