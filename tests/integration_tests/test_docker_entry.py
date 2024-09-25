import logging

logging.basicConfig(level=10, format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")

import math
from unittest.mock import patch, MagicMock
import json
import os
import tempfile
from glob import glob
from sys import argv
from unittest import TestCase

from pystac import Item, Asset, Catalog, Link, ItemCollection

from mdps_ds_lib.lib.constants import Constants

from cumulus_lambda_functions.docker_entrypoint.__main__ import choose_process
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.lib.utils.file_utils import FileUtils


class TestDockerEntry(TestCase):
    def test_01_search_part_01(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030'
        os.environ['LIMITS'] = '4000'
        os.environ['DATE_FROM'] = '1990-01-14T08:00:00Z'
        os.environ['DATE_TO'] = '2022-01-14T11:59:59Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            search_result_str = choose_process()
            search_result = json.loads(search_result_str)
            self.assertTrue('type' in search_result, f'missing type in search_result')
            item_collections = ItemCollection.from_dict(search_result)
            # self.assertTrue(isinstance(search_result, list), f'search_result is not list: {search_result}')
            self.assertEqual(len(item_collections.items), 4000, f'wrong length')
            search_result = set([k.id for k in item_collections.items])
            self.assertEqual(len(search_result), 4000, f'wrong length. not unique')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
            self.assertEqual(sorted(json.dumps(FileUtils.read_json(os.environ['OUTPUT_FILE']))), sorted(search_result_str), f'not identical result')
        return

    def test_01_search_part_02(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'SNDR_SNPP_ATMS_L1A___1'
        os.environ['LIMITS'] = '100'
        os.environ['DATE_FROM'] = '2016-01-14T08:00:00Z'
        os.environ['DATE_TO'] = '2016-01-14T11:59:59Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        print(search_result)
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        # self.assertTrue(isinstance(search_result, list), f'search_result is not list: {search_result}')
        self.assertEqual(len(item_collections.items), 20, f'wrong length')
        search_result = set([k.id for k in item_collections.items])
        self.assertEqual(len(search_result),20, f'wrong length. not unique')
        return

    def test_01_search_part_03(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'L0_SNPP_ATMS_SCIENCE___1'
        os.environ['LIMITS'] = '-1'
        os.environ['DATE_FROM'] = '1990-01-14T08:00:00Z'
        os.environ['DATE_TO'] = '2022-01-14T11:59:59Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        # self.assertTrue(isinstance(search_result, list), f'search_result is not list: {search_result}')
        self.assertEqual(len(item_collections.items), 4381, f'wrong length')
        search_result = set([k.id for k in item_collections.items])
        self.assertEqual(len(search_result), 4381, f'wrong length. not unique')
        return

    def test_01_search_part_04(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'L0_SNPP_ATMS_SCIENCE___1'
        os.environ['LIMITS'] = '347'
        os.environ['DATE_FROM'] = '1990-01-14T08:00:00Z'
        os.environ['DATE_TO'] = '2022-01-14T11:59:59Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        self.assertEqual(len(item_collections.items), 347, f'wrong length')
        search_result = set([k.id for k in item_collections.items])
        self.assertEqual(len(search_result), 347, f'wrong length. not unique')
        return

    def test_01_search_part_05(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['API_PREFIX'] = 'sbx-uds-2-dapa'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '71g0c73jl77gsqhtlfg2ht388c'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev'
        os.environ['COLLECTION_ID'] = 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030'
        os.environ['LIMITS'] = '37'
        os.environ['DATE_FROM'] = '1990-01-14T08:00:00Z'
        os.environ['DATE_TO'] = '2024-01-14T11:59:59Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'UNITY'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        self.assertEqual(len(item_collections.items), 37, f'wrong length')
        return

    def test_01_1_search_cmr_part_01(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'C1996881146-POCLOUD'  # 'C1666605425-PODAAC'  # C1996881146-POCLOUD
        os.environ['LIMITS'] = '2120'
        os.environ['DATE_FROM'] = '2002-06-01T12:06:00.000Z'
        os.environ['DATE_TO'] = '2011-10-04T06:51:45.000Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'CMR'
        os.environ['CMR_BASE_URL'] = 'https://cmr.earthdata.nasa.gov'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        self.assertEqual(len(item_collections.items), 2120, f'wrong length')
        return

    def test_01_1_search_cmr_part_02(self):
        """
        :return:
        """
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['COLLECTION_ID'] = 'C1996881146-POCLOUD'  # 'C1666605425-PODAAC'  # C1996881146-POCLOUD
        os.environ['LIMITS'] = '23'
        os.environ['DATE_FROM'] = '2002-06-01T12:06:00.000Z'
        os.environ['DATE_TO'] = '2011-10-04T06:51:45.000Z'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['GRANULES_SEARCH_DOMAIN'] = 'CMR'
        os.environ['CMR_BASE_URL'] = 'https://cmr.earthdata.nasa.gov'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('SEARCH')
        search_result = choose_process()
        search_result = json.loads(search_result)
        self.assertTrue('type' in search_result, f'missing type in search_result')
        item_collections = ItemCollection.from_dict(search_result)
        self.assertEqual(len(item_collections.items), 23, f'wrong length')
        return

    def test_04_catalog(self):
        upload_result = [{'id': 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file01', 'collection': 'NEW_COLLECTION_EXAMPLE_L1B___9', 'assets': {'metadata': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas'}, 'data': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc'}}}]
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'
        os.environ['UPLOADED_FILES_JSON'] = json.dumps(upload_result)
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('CATALOG')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            catalog_result_str = choose_process()
            catalog_result = json.loads(catalog_result_str)
            self.assertEqual('registered', catalog_result, 'wrong status')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_04_catalog_from_file(self):
        upload_result = [{'id': 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file01', 'collection': 'NEW_COLLECTION_EXAMPLE_L1B___9', 'assets': {'metadata': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas'}, 'data': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc'}}}]
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'
        os.environ['DELAY_SECOND'] = '35'
        os.environ['REPEAT_TIMES'] = '3'
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
            self.assertTrue('cataloging_request_status' in catalog_result, f'missing cataloging_request_status')
            self.assertTrue('status_result' in catalog_result, f'missing status_result')
            self.assertEqual(catalog_result['cataloging_request_status'], 'registered', f'mismatched cataloging_request_status value')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')

            status_result = catalog_result['status_result']

            self.assertTrue('cataloged' in status_result, f'missing cataloged')
            self.assertTrue('missing_granules' in status_result, f'missing missing_granules')
            self.assertTrue('registered_granules' in status_result, f'missing registered_granules')
            self.assertTrue(isinstance(status_result['cataloged'], bool), f'cataloged is not boolean: {status_result["cataloged"]}')
            # Example result: {'cataloging_request_status': 'registered', 'status_result': {'cataloged': False, 'missing_granules': ['NEW_COLLECTION_EXAMPLE_L1B___9:test_file01'], 'registered_granules': []}}
        return

    def test_04_catalog_from_file_item_collection(self):
        upload_result = {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'stac_version': '1.0.0', 'id': 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
             'properties': {'start_datetime': '2016-01-31T18:00:00.009057Z', 'end_datetime': '2016-01-31T19:59:59.991043Z',
                            'created': '2016-02-01T02:45:59.639000Z', 'updated': '2022-03-23T15:48:21.578000Z',
                            'datetime': '1970-01-01T00:00:00Z'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
             'links': [], 'assets': {
                'data': {'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc',
                         'title': 'main data'}, 'metadata__cas': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.cas',
                    'title': 'metadata cas'}, 'metadata__stac': {
                    'href': 's3://uds-test-cumulus-staging/NEW_COLLECTION_EXAMPLE_L1B___9/NEW_COLLECTION_EXAMPLE_L1B___9:test_file01/test_file01.nc.stac.json',
                    'title': 'metadata stac'}}, 'bbox': [0.0, 0.0, 0.0, 0.0], 'stac_extensions': [],
             'collection': 'NEW_COLLECTION_EXAMPLE_L1B___9'}]}
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'
        # os.environ['DELAY_SECOND'] = '5'
        # os.environ['REPEAT_TIMES'] = '3'
        os.environ['DELAY_SECOND'] = '35'
        os.environ['REPEAT_TIMES'] = '3'
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
            self.assertTrue('cataloging_request_status' in catalog_result, f'missing cataloging_request_status')
            self.assertTrue('status_result' in catalog_result, f'missing status_result')
            self.assertEqual(catalog_result['cataloging_request_status'], 'registered', f'mismatched cataloging_request_status value')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
            # TODO update this after it is deployed to MCP Test
            status_result = catalog_result['status_result']

            self.assertTrue('cataloged' in status_result, f'missing cataloged')
            self.assertTrue('missing_granules' in status_result, f'missing missing_granules')
            self.assertTrue('registered_granules' in status_result, f'missing registered_granules')
            self.assertTrue(isinstance(status_result['cataloged'], bool), f'cataloged is not boolean: {status_result["cataloged"]}')
        return

    def test_04_catalog_from_file_item_collection_large(self):
        upload_result = FileUtils.read_json('./stage-out-results.json')
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ[Constants.CLIENT_ID] = '71g0c73jl77gsqhtlfg2ht388c'  # MCP Dev
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'
        os.environ['CHUNK_SIZE'] = '250'
        # os.environ['DELAY_SECOND'] = '5'
        # os.environ['REPEAT_TIMES'] = '3'

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
            self.assertTrue(isinstance(catalog_result, list), f'catalog_result is not list. {catalog_result}')
            self.assertEqual(len(catalog_result), math.ceil(len(upload_result['features']) / 250), f'mismatched catalog_result count')

            catalog_result = catalog_result[0]
            self.assertTrue('cataloging_request_status' in catalog_result, f'missing cataloging_request_status')
            self.assertTrue('status_result' in catalog_result, f'missing status_result')
            self.assertEqual(catalog_result['cataloging_request_status'], {'message': 'processing'}, f'mismatched cataloging_request_status value')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')

            status_result = catalog_result['status_result']
            # TODO disabling this as we are not waiting for them to be registered.
            # self.assertTrue('cataloged' in status_result, f'missing cataloged')
            # self.assertTrue('missing_granules' in status_result, f'missing missing_granules')
            # self.assertTrue('registered_granules' in status_result, f'missing registered_granules')
            # self.assertTrue(isinstance(status_result['cataloged'], bool), f'cataloged is not boolean: {status_result["cataloged"]}')
        return
