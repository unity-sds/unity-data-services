import os
from unittest import TestCase

from cumulus_lambda_functions.uds_api.dapa.granules_dapa_query_es import GranulesDapaQueryEs


class TestGranulesDapaQueryEs(TestCase):
    def test_get_single_granule_01(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        collection_id = 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208'
        granule_id = 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53'
        granules_dapa_query = GranulesDapaQueryEs(collection_id, 1, None, None, None, None, f'localhost/api-prefix')
        granules_result = granules_dapa_query.get_single_granule(granule_id)
        print(granules_result)
        sample = {
            'type': 'Feature',
            'stac_version': '1.0.0',
            'id': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53',
            'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000], 'c_data2': [False, True, True, False, True], 'c_data3': ['Bellman Ford'], 'soil10': {'0_0': 0, '0_1': 1, '0_2': 0}, 'datetime': '2024-10-01T13:12:11.810000Z', 'start_datetime': '2016-01-31T18:00:00.009000Z', 'end_datetime': '2016-01-31T19:59:59.991000Z', 'created': '1970-01-01T00:00:00Z', 'updated': '2024-10-01T13:12:55.423000Z', 'status': 'completed', 'provider': 'unity', 'archive_status': 'cnm_r_failed', 'archive_error_message': '[{"uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json", "error": "mismatched size: 11 v. -1"}]', 'archive_error_code': 'VALIDATION_ERROR'},
            'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}, 'links': [{'rel': 'collection', 'href': '.'}, {'rel': 'self', 'href': '/Users/wphyo/Projects/unity/unity-data-services/tests/cumulus_lambda_functions/uds_api/dapa/localhost/api-prefix/collections/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/items/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53', 'type': 'application/json', 'title': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53'}], 'assets': {'abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json', 'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json', 'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1, 'file:checksum': 'unknown', 'roles': ['data']}, 'abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml', 'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml', 'description': 'size=1812;checksumType=md5;checksum=38c9d99e56312b595faa5e99df30b175;', 'file:size': 1812, 'file:checksum': '38c9d99e56312b595faa5e99df30b175', 'roles': ['metadata']}, 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json', 'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json', 'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1, 'file:checksum': 'unknown', 'roles': ['metadata']}, 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas', 'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas', 'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1, 'file:checksum': 'unknown', 'roles': ['metadata']}}, 'bbox': [-180.0, -90.0, 180.0, 90.0], 'stac_extensions': ['https://stac-extensions.github.io/file/v2.1.0/schema.json'], 'collection': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208'}
        self.assertTrue('properties' in granules_result, 'missing properties in granule')
        self.assertTrue('archive_status' in granules_result['properties'], 'missing archive_status in granule>properties')
        self.assertTrue('archive_error_message' in granules_result['properties'], 'missing archive_error_message in granule>properties')
        self.assertTrue('archive_error_code' in granules_result['properties'], 'missing archive_error_code in granule>properties')
        self.assertFalse('archive_status' in granules_result, 'missing archive_status in granule')
        self.assertFalse('archive_error_message' in granules_result, 'missing archive_error_message in granule')
        self.assertFalse('archive_error_code' in granules_result, 'missing archive_error_code in granule')

        return

    def test_start_01(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        collection_id = 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208'
        granule_id = 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53'
        granules_dapa_query = GranulesDapaQueryEs(collection_id, 10, None, None, None, None, f'localhost/api-prefix')
        granules_result = granules_dapa_query.start()
        print(granules_result)
        sample = {
            'statusCode': 200,
            'body': {
                'numberMatched': {'total_size': 6},
                'numberReturned': 6, 'stac_version': '1.0.0',
                'type': 'FeatureCollection', 'links': [],
                'features': [
                    {'type': 'Feature', 'stac_version': '1.0.0',
                     'id': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5',
                     'properties': {'datetime': '2024-08-29T12:25:05.457000Z', 'start_datetime': '2024-08-29T12:23:10.254000Z', 'end_datetime': '2024-08-29T12:23:10.254000Z', 'created': '1970-01-01T00:00:00Z', 'updated': '2024-08-29T12:25:43.367000Z', 'status': 'completed', 'provider': 'unity'},
                     'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
                     'links': [{'rel': 'collection', 'href': '.'}, {'rel': 'self', 'href': '/Users/wphyo/Projects/unity/unity-data-services/tests/cumulus_lambda_functions/uds_api/dapa/localhost/api-prefix/collections/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522/items/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5', 'type': 'application/json', 'title': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5'}],
                     'assets': {'test_file_5.json': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5/test_file_5.json', 'title': 'test_file_5.json', 'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1, 'file:checksum': 'unknown', 'roles': ['data']}, 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5.cmr.xml': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5.cmr.xml', 'title': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5.cmr.xml', 'description': 'size=1860;checksumType=md5;checksum=5e41aa2c00d8be37dd8d4919cde35232;', 'file:size': 1860, 'file:checksum': '5e41aa2c00d8be37dd8d4919cde35232', 'roles': ['metadata']}, 'test_file_5.json.stac.json': {'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522:test_file_5/test_file_5.json.stac.json', 'title': 'test_file_5.json.stac.json', 'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1, 'file:checksum': 'unknown', 'roles': ['metadata']}}, 'bbox': [-180.0, -90.0, 180.0, 90.0], 'stac_extensions': ['https://stac-extensions.github.io/file/v2.1.0/schema.json'], 'collection': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2408290522'},
                    {'type': 'Feature', 'stac_version': '1.0.0',
                     'id': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53',
                     'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000],
                                    'c_data2': [False, True, True, False, True], 'c_data3': ['Bellman Ford'],
                                    'soil10': {'0_0': 0, '0_1': 1, '0_2': 0}, 'datetime': '2024-10-01T13:12:11.810000Z',
                                    'start_datetime': '2016-01-31T18:00:00.009000Z',
                                    'end_datetime': '2016-01-31T19:59:59.991000Z', 'created': '1970-01-01T00:00:00Z',
                                    'updated': '2024-10-01T13:12:55.423000Z', 'status': 'completed',
                                    'provider': 'unity',
                                    'archive_status': 'cnm_r_failed',
                                    'archive_error_message': '[{"uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json", "error": "mismatched size: 11 v. -1"}]',
                                    'archive_error_code': 'VALIDATION_ERROR'},
                     'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
                     'links': [{'rel': 'collection', 'href': '.'},
                               {'rel': 'self',
                                'href': '/Users/wphyo/Projects/unity/unity-data-services/tests/cumulus_lambda_functions/uds_api/dapa/localhost/api-prefix/collections/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/items/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53',
                                'type': 'application/json',
                                'title': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53'}],
                     'assets': {'abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json': {
                         'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json',
                         'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.data.stac.json',
                         'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1,
                         'file:checksum': 'unknown', 'roles': ['data']},
                         'abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml': {
                             'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml',
                             'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.cmr.xml',
                             'description': 'size=1812;checksumType=md5;checksum=38c9d99e56312b595faa5e99df30b175;',
                             'file:size': 1812, 'file:checksum': '38c9d99e56312b595faa5e99df30b175',
                             'roles': ['metadata']}, 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json': {
                             'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json',
                             'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.stac.json',
                             'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1,
                             'file:checksum': 'unknown', 'roles': ['metadata']},
                         'abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas': {
                             'href': 's3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208/URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208:abcd.1234.efgh.test_file-24.08.13.13.53/abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas',
                             'title': 'abcd.1234.efgh.test_file-24.08.13.13.53.nc.cas',
                             'description': 'size=-1;checksumType=md5;checksum=unknown;', 'file:size': -1,
                             'file:checksum': 'unknown', 'roles': ['metadata']}},
                     'bbox': [-180.0, -90.0, 180.0, 90.0],
                     'stac_extensions': ['https://stac-extensions.github.io/file/v2.1.0/schema.json'],
                     'collection': 'URN:NASA:UNITY:UDS_MY_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2409301208'}
                    ]}}

        self.assertTrue('statusCode' in granules_result, 'missing statusCode')
        self.assertEqual(granules_result['statusCode'], 200, 'mismatch statusCode')
        self.assertTrue('body' in granules_result, 'missing body')
        granules_result = granules_result['body']
        self.assertTrue('features' in granules_result, 'missing features in body')
        granules_result = granules_result['features']
        if len(granules_result) < 1:
            print('features is empty array')
            return
        granule_1 = granules_result[0]
        self.assertTrue('properties' in granule_1, 'missing properties in granule')
        self.assertTrue('archive_status' in granule_1['properties'], 'missing archive_status in granule>properties')
        self.assertTrue('archive_error_message' in granule_1['properties'], 'missing archive_error_message in granule>properties')
        self.assertTrue('archive_error_code' in granule_1['properties'], 'missing archive_error_code in granule>properties')
        self.assertFalse('archive_status' in granule_1, 'missing archive_status in granule')
        self.assertFalse('archive_error_message' in granule_1, 'missing archive_error_message in granule')
        self.assertFalse('archive_error_code' in granule_1, 'missing archive_error_code in granule')
        return
