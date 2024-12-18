import base64
import json
import os
import random
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from sys import argv
from time import sleep
from unittest import TestCase

import requests
from dotenv import load_dotenv
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.cognito_login.cognito_login import CognitoLogin
from mdps_ds_lib.lib.utils.file_utils import FileUtils
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stage_in_out.upoad_granules_factory import UploadGranulesFactory
from pystac import Catalog, Asset, Link, ItemCollection, Item


class TestStageOutIngestion(TestCase):
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
        self.collection_name = 'DDD'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.03.20.14.40'.replace('.', '')  # '2402011200'
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
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:William'
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

    def test_03_upload_complete_catalog_role_as_key(self):
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['RESULT_PATH_PREFIX'] = ''
        os.environ['PROJECT'] = self.tenant
        os.environ['VENUE'] = self.tenant_venue
        os.environ['STAGING_BUCKET'] = 'uds-sbx-cumulus-staging'

        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        # os.environ['GRANULES_UPLOAD_TYPE'] = 'UPLOAD_S3_BY_STAC_CATALOG'
        # defaulted to this value

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('UPLOAD')

        starting_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['UPLOAD_DIR'] = ''  # not needed
            os.environ['OUTPUT_DIRECTORY'] = os.path.join(tmp_dir_name, 'output_dir')
            FileUtils.mk_dir_p(os.environ.get('OUTPUT_DIRECTORY'))
            os.environ['CATALOG_FILE'] = os.path.join(tmp_dir_name, 'catalog.json')
            total_files = 10
            # os.environ['PARALLEL_COUNT'] = str(total_files)
            granules_dir = os.path.join(tmp_dir_name, 'some_granules')
            FileUtils.mk_dir_p(granules_dir)
            catalog = Catalog(
                id='NA',
                description='NA')
            catalog.set_self_href(os.environ['CATALOG_FILE'])

            for i in range(1, total_files+1):
                filename = f'test_file{i:02d}'
                with open(os.path.join(granules_dir, f'{filename}.nc'), 'w') as ff:
                    ff.write('sample_file')
                with open(os.path.join(granules_dir, f'{filename}.nc.cas'), 'w') as ff:
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
                stac_item = Item(id=filename,
                                 geometry={
                                    "type": "Point",
                                    "coordinates": [0.0, 0.0]
                                 },
                                 bbox=[0.0, 0.0, 0.1, 0.1],
                                 datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                                 properties={
                                     "start_datetime": "2016-01-31T18:00:00.009057Z",
                                     "end_datetime": "2016-01-31T19:59:59.991043Z",
                                     "created": "2016-02-01T02:45:59.639000Z",
                                     "updated": "2022-03-23T15:48:21.578000Z",
                                     "datetime": "2022-03-23T15:48:19.079000Z"
                                 },
                                 href=os.path.join('some_granules', f'{filename}.nc.stac.json'),
                                 collection=f'{self.collection_name}-{i:02d}',
                                 assets={
                                    f'data': Asset(os.path.join('.', f'{filename}.nc'), title='test_file01.nc', roles=['data']),
                                    f'metadata1': Asset(os.path.join('.', f'{filename}.nc.cas'), title='test_file01.nc.cas', roles=['metadata']),
                                    f'metadata2': Asset(os.path.join('.', f'{filename}.nc.stac.json'), title='test_file01.nc.stac.json', roles=['metadata']),
                                 })
                with open(os.path.join(granules_dir, f'{filename}.nc.stac.json'), 'w') as ff:
                    ff.write(json.dumps(stac_item.to_dict(False, False)))
                catalog.add_link(Link('item', os.path.join('some_granules', f'{filename}.nc.stac.json'), 'application/json'))
            print(json.dumps(catalog.to_dict(False, False)))
            with open(os.environ['CATALOG_FILE'], 'w') as ff:
                ff.write(json.dumps(catalog.to_dict(False, False)))

            upload_result = UploadGranulesFactory().get_class(os.getenv('GRANULES_UPLOAD_TYPE', UploadGranulesFactory.UPLOAD_S3_BY_STAC_CATALOG)).upload()
            upload_result = json.loads(upload_result)
            print(upload_result)
            """
            {'type': 'Catalog', 'id': 'NA', 'stac_version': '1.0.0', 'description': 'NA', 'links': [{'rel': 'root', 'href': '/var/folders/33/xhq97d6s0dq78wg4h2smw23m0000gq/T/tmprew515jo/catalog.json', 'type': 'application/json'}, {'rel': 'item', 'href': '/var/folders/33/xhq97d6s0dq78wg4h2smw23m0000gq/T/tmprew515jo/successful_features.json', 'type': 'application/json'}, {'rel': 'item', 'href': '/var/folders/33/xhq97d6s0dq78wg4h2smw23m0000gq/T/tmprew515jo/failed_features.json', 'type': 'application/json'}]}
            """
            self.assertTrue('type' in upload_result, 'missing type')
            self.assertEqual(upload_result['type'], 'Catalog', 'missing type')
            upload_result = Catalog.from_dict(upload_result)
            child_links = [k.href for k in upload_result.get_links(rel='item')]
            self.assertEqual(len(child_links), 2, f'wrong length: {child_links}')
            self.assertTrue(FileUtils.file_exist(child_links[0]), f'missing file: {child_links[0]}')
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[0]))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), total_files, f'wrong length: {successful_feature_collection}')

            self.assertTrue(FileUtils.file_exist(child_links[1]), f'missing file: {child_links[1]}')
            failed_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[1]))
            failed_feature_collection = list(failed_feature_collection.items)
            self.assertEqual(len(failed_feature_collection), 0, f'wrong length: {failed_feature_collection}')

            upload_result = successful_feature_collection[0].to_dict(False, False)
            print(f'example feature: {upload_result}')
            self.assertTrue('assets' in upload_result, 'missing assets')
            result_key = [k for k in upload_result['assets'].keys()][0]
            print(f'result_key: {result_key}')
            self.assertEqual(result_key, 'data', f'worng asset key: {result_key}')
            self.assertTrue(f'metadata1' in upload_result['assets'], f'missing assets#metadata asset: metadata1')
            self.assertTrue('href' in upload_result['assets'][f'metadata1'], 'missing assets#metadata__cas#href')
            self.assertTrue(upload_result['assets'][f'metadata1']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/URN:NASA:UNITY:{os.environ["PROJECT"]}:{os.environ["VENUE"]}:{self.collection_name}'))
            self.assertTrue(f'data' in upload_result['assets'], f'missing assets#data: data')
            self.assertTrue('href' in upload_result['assets'][f'data'], 'missing assets#data#href')
            self.assertTrue(upload_result['assets'][f'data']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/URN:NASA:UNITY:{os.environ["PROJECT"]}:{os.environ["VENUE"]}:{self.collection_name}'))
            """
            Example output: 
            {
                'type': 'FeatureCollection', 
                'features': [{
                    'type': 'Feature', 
                    'stac_version': '1.0.0', 
                    'id': 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
                    'properties': {'start_datetime': '2016-01-31T18:00:00.009057Z',
                                'end_datetime': '2016-01-31T19:59:59.991043Z', 'created': '2016-02-01T02:45:59.639000Z',
                                'updated': '2022-03-23T15:48:21.578000Z', 'datetime': '1970-01-01T00:00:00Z'},
                    'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [], 
                    'assets': {'data': {
                        'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc',
                        'title': 'main data'}, 'metadata__cas': {
                        'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas',
                        'title': 'metadata cas'}, 'metadata__stac': {
                        'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.stac.json',
                        'title': 'metadata stac'}}, 
                    'bbox': [0.0, 0.0, 0.0, 0.0], 
                    'stac_extensions': [],
                    'collection': 'NEW_COLLECTION_EXAMPLE_L1B___9'}]}
            """
            s3 = AwsS3()
            s3_keys = [k for k in s3.get_child_s3_files(os.environ['STAGING_BUCKET'],
                                  f"stage_out/successful_features_{starting_time}",
                                  )]
            s3_keys = sorted(s3_keys)
            print(f's3_keys: {s3_keys}')
            self.assertTrue(len(s3_keys) > 0, f'empty files in S3')
            local_file = s3.set_s3_url(f's3://{os.environ["STAGING_BUCKET"]}/{s3_keys[-1][0]}').download(tmp_dir_name)
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(local_file))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), total_files, f'wrong length: {successful_feature_collection}')
        return

    def test_single_granule_get(self):
        post_url = f'{self.uds_url}collections/URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}-01___001/items/URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}-01___001:test_file01'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
        }
        print(post_url)
        query_result = requests.get(url=post_url,
                                    headers=headers,
                                    )
        response_json = json.loads(query_result.text)
        print(json.dumps(response_json, indent=4))
        self.assertEqual(query_result.status_code, 200, f'wrong status code. {query_result.text}')
        return
