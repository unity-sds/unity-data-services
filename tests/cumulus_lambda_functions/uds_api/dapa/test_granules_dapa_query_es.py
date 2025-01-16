import os
from unittest import TestCase

from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.uds_api.dapa.granules_dapa_query_es import GranulesDapaQueryEs


class TestGranulesDapaQueryEs(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.custom_metadata_body = {
            'tag': {'type': 'keyword'},
            'c_data1': {'type': 'long'},
            'c_data2': {'type': 'boolean'},
            'c_data3': {'type': 'keyword'},
        }

        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'KKK-09'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.03.20.14.40'.replace('.', '')  # '2402011200'
        self.collection_version = '001'
        return

    def test_start_01(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        self.tenant = 'UDS_LOCAL_TEST_3'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'DDD-01'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '001'

        collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        granule_id = f'{collection_id}:test_file09'

        granules_dapa_query = GranulesDapaQueryEs(collection_id, 10, '1736291597733,URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file10', None, None, None, f'localhost/api-prefix')
        granules_result = granules_dapa_query.start()
        print(granules_result)
        print([k['id'] for k in granules_result['body']['features']])
        # ['URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file20', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file19', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file14', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file17', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file18', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file12', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file13', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file15', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file06', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file01']
        # ['URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file05', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file03', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file09', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file16', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file11', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file04', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file08', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file02', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file07', 'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001:test_file10']
        return

    def test_get_single_granule_01(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        granule_id = f'{collection_id}:test_file09'

        mock_feature = {
            'archive_status': 'cnm_r_failed',
            'archive_error_message': 'testing 1 2 3',
            'archive_error_code': 'VALIDATION_ERROR',

            "type": "Feature",
            "stac_version": "1.0.0",
            "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001:test_file09",
            "properties": {
                "datetime": "2024-11-26T23:37:15.288000Z",
                "start_datetime": "2016-01-31T18:00:00.009000Z",
                "end_datetime": "2016-01-31T19:59:59.991000Z",
                "created": "1970-01-01T00:00:00Z",
                "updated": "2024-11-26T23:38:01.692000Z",
                "status": "completed",
                "provider": "unity",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    0.0,
                    0.0
                ]
            },
            "links": [
                {
                    "rel": "collection",
                    "href": "."
                }
            ],
            "assets": {
                "test_file09.nc": {
                    "href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001:test_file09/test_file09.nc",
                    "title": "test_file09.nc",
                    "description": "size=0;checksumType=md5;checksum=00000000000000000000000000000000;",
                    "file:size": 0,
                    "file:checksum": "00000000000000000000000000000000",
                    "roles": [
                        "data"
                    ]
                },
                "test_file09.nc.cas": {
                    "href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001:test_file09/test_file09.nc.cas",
                    "title": "test_file09.nc.cas",
                    "description": "size=0;checksumType=md5;checksum=00000000000000000000000000000000;",
                    "file:size": 0,
                    "file:checksum": "00000000000000000000000000000000",
                    "roles": [
                        "metadata"
                    ]
                },
                "test_file09.nc.stac.json": {
                    "href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001:test_file09/test_file09.nc.stac.json",
                    "title": "test_file09.nc.stac.json",
                    "description": "size=0;checksumType=md5;checksum=00000000000000000000000000000000;",
                    "file:size": 0,
                    "file:checksum": "00000000000000000000000000000000",
                    "roles": [
                        "metadata"
                    ]
                },
                "test_file09.cmr.xml": {
                    "href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001:test_file09/test_file09.cmr.xml",
                    "title": "test_file09.cmr.xml",
                    "description": "size=1716;checksumType=md5;checksum=f842ba4e23e76ae81014a01c820b01f7;",
                    "file:size": 1716,
                    "file:checksum": "f842ba4e23e76ae81014a01c820b01f7",
                    "roles": [
                        "metadata"
                    ]
                }
            },
            "bbox": {
                "type": "envelope",
                "coordinates": [
                    [
                        -180.0,
                        90.0
                    ],
                    [
                        180.0,
                        -90.0
                    ]
                ]
            },
            "stac_extensions": [
                "https://stac-extensions.github.io/file/v2.1.0/schema.json"
            ],
            "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:KKK-09___001",
            "event_time": 1732664287722
        }

        granules_db_index = GranulesDbIndex()
        granules_db_index.add_entry(self.tenant, self.tenant_venue, mock_feature, granule_id)
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
