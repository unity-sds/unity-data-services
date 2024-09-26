import base64
import json
import os
import tempfile
from datetime import datetime
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
        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_COLLECTION'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.04.25.11.00'.replace('.', '')  # '2402011200'

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
        self.granule_id = 'abcd.1234.efgh.test_file05'
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
        os.environ['STAGING_BUCKET'] = 'uds-sbx-cumulus-staging'

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

    def test_04_upload_many_granules(self):
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
        # os.environ['RESULT_PATH_PREFIX'] = 'integration_test/stag_eout'
        os.environ['STAGING_BUCKET'] = 'uds-sbx-cumulus-staging'
        os.environ['COLLECTION_ID'] = temp_collection_id

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
            total_files = 20
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
                                 href=os.path.join('some_granules', f'{filename}.nc.stac.json'),
                                 collection='NA',
                                 assets={
                                    f'{filename}.nc': Asset(os.path.join('.', f'{filename}.nc'), title='test_file01.nc', roles=['data']),
                                    f'{filename}.nc.cas': Asset(os.path.join('.', f'{filename}.nc.cas'), title='test_file01.nc.cas', roles=['metadata']),
                                    f'{filename}.nc.stac.json': Asset(os.path.join('.', f'{filename}.nc.stac.json'), title='test_file01.nc.stac.json', roles=['metadata']),
                                 })
                with open(os.path.join(granules_dir, f'{filename}.nc.stac.json'), 'w') as ff:
                    ff.write(json.dumps(stac_item.to_dict(False, False)))
                catalog.add_link(Link('item', os.path.join('some_granules', f'{filename}.nc.stac.json'), 'application/json'))
            print(json.dumps(catalog.to_dict(False, False)))
            with open(os.environ['CATALOG_FILE'], 'w') as ff:
                ff.write(json.dumps(catalog.to_dict(False, False)))

            upload_result_str = choose_process()
            upload_result = json.loads(upload_result_str)
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
            self.assertTrue(result_key.startswith('test_file'), f'worng asset key: {result_key}')
            result_key_prefix = result_key.split('.')[0]
            self.assertTrue(f'{result_key_prefix}.nc.cas' in upload_result['assets'], f'missing assets#metadata asset: {result_key_prefix}.nc.cas')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc.cas'], 'missing assets#metadata__cas#href')
            self.assertTrue(upload_result['assets'][f'{result_key_prefix}.nc.cas']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/{os.environ["COLLECTION_ID"]}/'))
            self.assertTrue(f'{result_key_prefix}.nc' in upload_result['assets'], f'missing assets#data: {result_key_prefix}.nc')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc'], 'missing assets#data#href')
            self.assertTrue(upload_result['assets'][f'{result_key_prefix}.nc']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/{os.environ["COLLECTION_ID"]}/'))
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
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


    def test_06_retrieve_granule(self):
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
            self.assertTrue('c_data3' in stac_item.properties, f'missing custom_metadata: {each_feature}')
        return
