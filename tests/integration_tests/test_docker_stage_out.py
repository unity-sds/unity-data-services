import logging
from datetime import datetime

from mdps_ds_lib.stage_in_out.upload_granules_by_complete_catalog_s3 import \
    UploadGranulesByCompleteCatalogS3

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

logging.basicConfig(level=10, format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")

import json
import os
import tempfile
from sys import argv
from unittest import TestCase

from pystac import Item, Asset, Catalog, Link, ItemCollection

from mdps_ds_lib.lib.constants import Constants

from cumulus_lambda_functions.docker_entrypoint.__main__ import choose_process
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.lib.utils.file_utils import FileUtils


class TestDockerStageOut(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tenant = 'UDS_MY_LOCAL_ARCHIVE_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_UNIT_COLLECTION'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.08.29.09.00'.replace('.', '')  # '2402011200'

    def not_in_used_test_03_upload(self):
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'

        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
        os.environ['STAGING_BUCKET'] = 'uds-test-cumulus-staging'

        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        os.environ['GRANULES_UPLOAD_TYPE'] = 'S3'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('UPLOAD')

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['UPLOAD_DIR'] = tmp_dir_name
            with open(os.path.join(tmp_dir_name, 'test_file01.nc'), 'w') as ff:
                ff.write('sample_file')
            with open(os.path.join(tmp_dir_name, 'test_file01.nc.cas'), 'w') as ff:
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
            upload_result = choose_process()
            print(upload_result)
            self.assertEqual(1, len(upload_result), 'wrong length of upload_result features')
            upload_result = upload_result[0]
            self.assertTrue('assets' in upload_result, 'missing assets')
            self.assertTrue('metadata' in upload_result['assets'], 'missing assets#metadata')
            self.assertTrue('href' in upload_result['assets']['metadata'], 'missing assets#metadata#href')
            self.assertTrue(
                upload_result['assets']['metadata']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/'))
            self.assertTrue('data' in upload_result['assets'], 'missing assets#data')
            self.assertTrue('href' in upload_result['assets']['data'], 'missing assets#data#href')
            self.assertTrue(upload_result['assets']['data']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/'))
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def not_in_used_test_03_upload_catalog(self):
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'

        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
        os.environ['STAGING_BUCKET'] = 'uds-test-cumulus-staging'

        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        os.environ['GRANULES_UPLOAD_TYPE'] = 'CATALOG_S3'

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('UPLOAD')

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['UPLOAD_DIR'] = ''  # not needed
            os.environ['CATALOG_FILE'] = os.path.join(tmp_dir_name, 'catalog.json')
            with open(os.path.join(tmp_dir_name, 'test_file01.nc'), 'w') as ff:
                ff.write('sample_file')
            with open(os.path.join(tmp_dir_name, 'test_file01.nc.cas'), 'w') as ff:
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
            stac_item = Item(id='NA',
                             geometry={
                                "type": "Point",
                                "coordinates": [0.0, 0.0]
                             },
                             bbox=[0.0, 0.0, 0.0, 0.0],
                             datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                             properties={
                                 "start_datetime": "2016-01-31T18:00:00.009057Z",
                                 "end_datetime": "2016-01-31T19:59:59.991043Z",
                                 "created": "2016-02-01T02:45:59.639000Z",
                                 "updated": "2022-03-23T15:48:21.578000Z",
                                 "datetime": "2022-03-23T15:48:19.079000Z"
                             },
                             collection='NA',
                             assets={
                                'data': Asset(os.path.join(tmp_dir_name, 'test_file01.nc'), title='main data'),
                                'metadata__cas': Asset(os.path.join(tmp_dir_name, 'test_file01.nc.cas'), title='metadata cas'),
                                'metadata__stac': Asset(os.path.join(tmp_dir_name, 'test_file01.nc.stac.json'), title='metadata stac'),
                             })
            with open(os.path.join(tmp_dir_name, 'test_file01.nc.stac.json'), 'w') as ff:
                ff.write(json.dumps(stac_item.to_dict(False, False)))
            catalog = Catalog(
                id='NA',
                description='NA')
            catalog.set_self_href(os.environ['CATALOG_FILE'])
            catalog.add_link(Link('child', os.path.join(tmp_dir_name, 'test_file01.nc.stac.json'), 'application/json'))
            with open(os.environ['CATALOG_FILE'], 'w') as ff:
                ff.write(json.dumps(catalog.to_dict(False, False)))

            upload_result = choose_process()
            print(upload_result)
            self.assertEqual(1, len(upload_result), 'wrong length of upload_result features')
            upload_result = upload_result[0]
            self.assertTrue('assets' in upload_result, 'missing assets')
            self.assertTrue('metadata__cas' in upload_result['assets'], 'missing assets#metadata__cas')
            self.assertTrue('href' in upload_result['assets']['metadata__cas'], 'missing assets#metadata__cas#href')
            self.assertTrue(
                upload_result['assets']['metadata__cas']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/'))
            self.assertTrue('data' in upload_result['assets'], 'missing assets#data')
            self.assertTrue('href' in upload_result['assets']['data'], 'missing assets#data#href')
            self.assertTrue(upload_result['assets']['data']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/'))
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_03_upload_complete_catalog(self):
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['RESULT_PATH_PREFIX'] = 'integration_test/stage_out'
        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
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
                                 bbox=[0.0, 0.0, 0.0, 0.0],
                                 datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                                 properties={
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
                                  f"{os.environ['RESULT_PATH_PREFIX']}/successful_features_{starting_time}",
                                  )]
            s3_keys = sorted(s3_keys)
            print(f's3_keys: {s3_keys}')
            self.assertTrue(len(s3_keys) > 0, f'empty files in S3')
            local_file = s3.set_s3_url(f's3://{os.environ["STAGING_BUCKET"]}/{s3_keys[-1][0]}').download(tmp_dir_name)
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(local_file))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), total_files, f'wrong length: {successful_feature_collection}')
        return

    def test_03_02_upload_complete_catalog(self):
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
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
                                 bbox=[0.0, 0.0, 0.0, 0.0],
                                 datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                                 properties={
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
                                  f"{UploadGranulesByCompleteCatalogS3.DEFAULT_RESULT_PATH_PREFIX}/successful_features_{starting_time}",
                                  )]
            s3_keys = sorted(s3_keys)
            print(f's3_keys: {s3_keys}')
            self.assertTrue(len(s3_keys) > 0, f'empty files in S3')
            local_file = s3.set_s3_url(f's3://{os.environ["STAGING_BUCKET"]}/{s3_keys[-1][0]}').download(tmp_dir_name)
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(local_file))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), total_files, f'wrong length: {successful_feature_collection}')
        return

    def test_03_03_upload_auxiliary_files(self):
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        os.environ['GRANULES_UPLOAD_TYPE'] = 'UPLOAD_AUXILIARY_FILE_AS_GRANULE'
        os.environ['COLLECTION_ID'] = temp_collection_id
        os.environ['STAGING_BUCKET'] = 'uds-sbx-cumulus-staging'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['RESULT_PATH_PREFIX'] = 'stage_out'
        os.environ['PARALLEL_COUNT'] = '1'

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('UPLOAD')

        starting_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_DIRECTORY'] = os.path.join(tmp_dir_name, 'output_dir')
            FileUtils.mk_dir_p(os.environ.get('OUTPUT_DIRECTORY'))

            real_base_dir = os.path.join(tmp_dir_name, 'auxiliary_base')
            FileUtils.mk_dir_p(real_base_dir)
            os.environ['BASE_DIRECTORY'] = real_base_dir

            with open(os.path.join(tmp_dir_name, 'excluding_file.json'), 'w') as ff:
                ff.write('{"message": "excluding file"}')
            with open(os.path.join(real_base_dir, 'test_file_0.json'), 'w') as ff:
                ff.write('{"message": "some file at root"}')
            sub_folders = [
                os.path.join(real_base_dir, 'son'),
                os.path.join(real_base_dir, 'daughter'),
                os.path.join(real_base_dir, os.path.join('son', 'grandson')),
                os.path.join(real_base_dir, os.path.join('son', 'granddaughter')),
                os.path.join(real_base_dir, os.path.join('daughter', 'grandson')),
                os.path.join(real_base_dir, os.path.join('daughter', 'granddaughter')),
            ]
            for i, each_sub_folder in enumerate(sub_folders):
                FileUtils.mk_dir_p(each_sub_folder)
                with open(os.path.join(each_sub_folder, f'test_file_{i}.json'), 'w') as ff:
                    ff.write(json.dumps({"message": f"some file at {each_sub_folder}"}))
            FileUtils.mk_dir_p(os.path.join(real_base_dir, 'nephew'))  # should not throw error for empty folders
            FileUtils.mk_dir_p(os.path.join(real_base_dir, os.path.join('nephew', 'grandson')))  # should not throw error for empty folders
            total_files = len(sub_folders) + 1
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')

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
            self.assertTrue(f'{result_key}.stac.json' in upload_result['assets'], f'missing assets#metadata asset: test_file_0.json')
            self.assertTrue('href' in upload_result['assets'][f'{result_key}.stac.json'], 'missing assets#metadata__cas#href')
            self.assertTrue(upload_result['assets'][f'{result_key}.stac.json']['href'].startswith(f's3://{os.environ["STAGING_BUCKET"]}/{os.environ["COLLECTION_ID"]}/'), f"wrong HREF (no S3?): upload_result['assets'][f'{result_key}.stac.json']['href']")
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
            with open(os.environ['OUTPUT_FILE'], 'r') as ff:
                print(ff.read())
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
                                  f"{os.environ['RESULT_PATH_PREFIX']}/successful_features_{starting_time}",
                                  )]
            s3_keys = sorted(s3_keys)
            print(f's3_keys: {s3_keys}')
            self.assertTrue(len(s3_keys) > 0, f'empty files in S3')
            local_file = s3.set_s3_url(f's3://{os.environ["STAGING_BUCKET"]}/{s3_keys[-1][0]}').download(tmp_dir_name)
            successful_feature_collection = ItemCollection.from_dict(FileUtils.read_json(local_file))
            successful_feature_collection = list(successful_feature_collection.items)
            self.assertEqual(len(successful_feature_collection), total_files, f'wrong length: {successful_feature_collection}')
        return

    def test_03_upload_complete_catalog_invalid_bucket(self):
        os.environ['VERIFY_SSL'] = 'FALSE'

        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
        os.environ['STAGING_BUCKET'] = 'invalid_bucket'

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
                                 bbox=[0.0, 0.0, 0.0, 0.0],
                                 datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                                 properties={
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
                                     f'{filename}.nc.stac.json': Asset(os.path.join('.', f'{filename}.nc.stac.json'), title='test_file01.nc.stac.json',  roles=['metadata']),
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
            self.assertEqual(len(successful_feature_collection), 0, f'wrong length: {successful_feature_collection}')

            self.assertTrue(FileUtils.file_exist(child_links[1]), f'missing file: {child_links[1]}')
            failed_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[1]))
            failed_feature_collection = list(failed_feature_collection.items)
            self.assertEqual(len(failed_feature_collection), total_files, f'wrong length: {failed_feature_collection}')

            upload_result = failed_feature_collection[0].to_dict(False, False)
            print(f'example feature: {upload_result}')
            self.assertTrue('properties' in upload_result, 'missing properties')
            self.assertTrue('upload_error' in upload_result['properties'], 'missing upload_error')
            self.assertTrue('An error occurred (NoSuchBucket)'in upload_result['properties']['upload_error'], f"wrong upload_error: {upload_result['properties']['upload_error']}")

            self.assertTrue('assets' in upload_result, 'missing assets')
            result_key = [k for k in upload_result['assets'].keys()][0]
            self.assertTrue(result_key.startswith('test_file'), f'worng asset key: {result_key}')
            result_key_prefix = result_key.split('.')[0]

            self.assertTrue(f'{result_key_prefix}.nc.cas' in upload_result['assets'], f'missing assets#metadata asset: {result_key_prefix}.nc.cas')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc.cas'], 'missing assets#metadata__cas#href')
            self.assertTrue(f'{result_key_prefix}.nc' in upload_result['assets'], f'missing assets#data: {result_key_prefix}.nc')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc'], 'missing assets#data#href')
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
        return

    def test_03_upload_complete_catalog_missing_data(self):
        os.environ['VERIFY_SSL'] = 'FALSE'

        os.environ['COLLECTION_ID'] = 'NEW_COLLECTION_EXAMPLE_L1B___9'
        os.environ['STAGING_BUCKET'] = 'invalid_bucket'

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
                                 bbox=[0.0, 0.0, 0.0, 0.0],
                                 datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                                 properties={
                                     "start_datetime": "2016-01-31T18:00:00.009057Z",
                                     "end_datetime": "2016-01-31T19:59:59.991043Z",
                                     "created": "2016-02-01T02:45:59.639000Z",
                                     "updated": "2022-03-23T15:48:21.578000Z",
                                     "datetime": "2022-03-23T15:48:19.079000Z"
                                 },
                                 href=os.path.join('some_granules', f'{filename}.nc.stac.json'),
                                 collection='NA',
                                 assets={
                                     f'{filename}.nc': Asset(os.path.join('.', f'{filename}.nc'), title='test_file01.nc', roles=['data1']),
                                     f'{filename}.nc.cas': Asset(os.path.join('.', f'{filename}.nc.cas'), title='test_file01.nc.cas', roles=['metadata']),
                                     f'{filename}.nc.stac.json': Asset(os.path.join('.', f'{filename}.nc.stac.json'), title='test_file01.nc.stac.json',  roles=['metadata']),
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
            self.assertEqual(len(successful_feature_collection), 0, f'wrong length: {successful_feature_collection}')

            self.assertTrue(FileUtils.file_exist(child_links[1]), f'missing file: {child_links[1]}')
            failed_feature_collection = ItemCollection.from_dict(FileUtils.read_json(child_links[1]))
            failed_feature_collection = list(failed_feature_collection.items)
            self.assertEqual(len(failed_feature_collection), total_files, f'wrong length: {failed_feature_collection}')

            upload_result = failed_feature_collection[0].to_dict(False, False)
            print(f'example feature: {upload_result}')
            self.assertTrue('properties' in upload_result, 'missing properties')
            self.assertTrue('upload_error' in upload_result['properties'], 'missing upload_error')
            self.assertTrue('missing "data" in assets'in upload_result['properties']['upload_error'], f"wrong upload_error: {upload_result['properties']['upload_error']}")

            self.assertTrue('assets' in upload_result, 'missing assets')
            result_key = [k for k in upload_result['assets'].keys()][0]
            self.assertTrue(result_key.startswith('test_file'), f'worng asset key: {result_key}')
            result_key_prefix = result_key.split('.')[0]

            self.assertTrue(f'{result_key_prefix}.nc.cas' in upload_result['assets'], f'missing assets#metadata asset: {result_key_prefix}.nc.cas')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc.cas'], 'missing assets#metadata__cas#href')
            self.assertTrue(f'{result_key_prefix}.nc' in upload_result['assets'], f'missing assets#data: {result_key_prefix}.nc')
            self.assertTrue('href' in upload_result['assets'][f'{result_key_prefix}.nc'], 'missing assets#data#href')
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
        return
