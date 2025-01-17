import json
import os
from copy import deepcopy
from time import sleep
from unittest import TestCase

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
from mdps_ds_lib.lib.aws.es_abstract import ESAbstract
from mdps_ds_lib.lib.aws.es_factory import ESFactory

from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex


class TestGranulesDbIndex(TestCase):
    def test_01(self):
        os.environ['ES_URL'] = 'dummy'
        granules_index = GranulesDbIndex()
        expected = custom_metadata_body = {
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
        granule_index_mapping = {'unity_granule_uds_black_dev__v01': {'mappings': {'dynamic': 'strict', 'properties': {'archive_error_code': {'type': 'keyword'}, 'archive_error_message': {'type': 'text'}, 'archive_status': {'type': 'keyword'}, 'assets': {'type': 'object', 'dynamic': 'false'}, 'bbox': {'type': 'geo_shape'}, 'collection': {'type': 'keyword'}, 'event_time': {'type': 'long'}, 'geometry': {'type': 'geo_shape'}, 'id': {'type': 'keyword'}, 'links': {'properties': {'href': {'type': 'keyword'}, 'rel': {'type': 'keyword'}, 'title': {'type': 'text'}, 'type': {'type': 'keyword'}}}, 'properties': {'dynamic': 'false', 'properties': {'c_data1': {'type': 'long'}, 'c_data2': {'type': 'boolean'}, 'c_data3': {'type': 'keyword'}, 'created': {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"}, 'datetime': {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"}, 'end_datetime': {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"}, 'provider': {'type': 'keyword'}, 'soil10': {'properties': {'0_0': {'type': 'integer'}, '0_1': {'type': 'integer'}, '0_2': {'type': 'integer'}}}, 'start_datetime': {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"}, 'status': {'type': 'keyword'}, 'tag': {'type': 'keyword'}, 'updated': {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"}}}, 'stac_extensions': {'type': 'keyword'}, 'stac_version': {'type': 'keyword'}, 'type': {'type': 'keyword'}}}}}
        custom_metadata = granules_index.get_custom_metadata_fields(granule_index_mapping)
        print(custom_metadata)
        self.assertEqual(custom_metadata, expected)
        return

    def test_02(self):
        os.environ['ES_URL'] = 'https://vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        self.tenant = 'UDS_LOCAL_TEST_3'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        search_dsl = {
            'track_total_hits': True,
            'size': 20,
            'sort': [
                {'properties.datetime': {'order': 'desc'}},
                {'id': {'order': 'asc'}}
            ],
            'query': {
                'bool': {
                    'must': {'term': {'collection': {'value': f'URN:NASA:UNITY:UDS_LOCAL_TEST_3:DEV:DDD-01___001'}}}
                }
            },
        }
        granules_index = GranulesDbIndex()
        query_result = granules_index.dsl_search(self.tenant, self.tenant_venue, search_dsl)
        print(json.dumps(query_result, indent=4))
        # self.assertEqual(custom_metadata, expected)
        return

    def test_complete(self):
        """
        Steps:
        1. Create index 1
        2. Add doc 1
        3. Add doc 2
        4. Create index 2
        5. Add doc 3
        6. Update doc 1
        7. make sure index 1: doc 1 is disappeared
        8. Update doc 3
        9. make sure index 2 : doc 3 is updated
        10. Create index 3
        11. Update doc 4
        12. It should throw error.
        13. Update doc 2. Make sure index 1 : doc 2 is removed
        14. Update doc 3. Make sure index 2 : doc 3 is removed


        :return:
        """
        os.environ['ES_URL'] = 'https://vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        granules_db_index = GranulesDbIndex()
        es: ESAbstract = ESFactory().get_instance('AWS',
                                                  index=DBConstants.collections_index,
                                                  base_url=os.getenv('ES_URL'),
                                                  port=int(os.getenv('ES_PORT', '443'))
                                                  )

        self.tenant = 'UDS_LOCAL_UNIT_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'UNIT'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_UNIT_TEST_1'
        self.collection_version = '001'
        collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        self.custom_metadata_body1 = {
            'tag': {'type': 'keyword'},
            'c_data1': {'type': 'long'},
        }
        self.custom_metadata_body2 = {
            'tag': {'type': 'keyword'},
            'c_data2': {'type': 'long'},
        }
        self.custom_metadata_body3 = {
            'tag': {'type': 'keyword'},
            'c_data3': {'type': 'long'},
        }

        granule_id1 = f'{collection_id}:test_file01'
        granule_id2 = f'{collection_id}:test_file02'
        granule_id3 = f'{collection_id}:test_file03'
        granule_id4 = f'{collection_id}:test_file04'

        mock_feature1 = {
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
        mock_feature2 = deepcopy(mock_feature1)
        mock_feature3 = deepcopy(mock_feature1)
        mock_feature4 = deepcopy(mock_feature1)
        mock_feature1['id'] = granule_id1
        mock_feature2['id'] = granule_id2
        mock_feature3['id'] = granule_id3
        mock_feature4['id'] = granule_id4

        new_index_name1 = f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}__v01'.lower().strip()
        new_index_name2 = f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}__v02'.lower().strip()
        new_index_name3 = f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}__v03'.lower().strip()

        if es.has_index(new_index_name1):
            es.delete_index(new_index_name1)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v01'.lower().strip())
        if es.has_index(new_index_name2):
            es.delete_index(new_index_name2)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v02'.lower().strip())
        if es.has_index(new_index_name3):
            es.delete_index(new_index_name3)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v03'.lower().strip())


        ####   index v1 ####
        granules_db_index.create_new_index(self.tenant, self.tenant_venue, self.custom_metadata_body1)
        sleep(2)
        self.assertTrue(es.has_index(new_index_name1), f'missing {new_index_name1}')

        granules_db_index.add_entry(self.tenant, self.tenant_venue, mock_feature1, granule_id1)
        sleep(2)
        check_result = es.query_by_id(granule_id1, new_index_name1)
        self.assertTrue(check_result is not None, f'granule_id1 - new_index_name1 {check_result}')

        granules_db_index.add_entry(self.tenant, self.tenant_venue, mock_feature2, granule_id2)
        sleep(2)
        check_result = es.query_by_id(granule_id2, new_index_name1)
        self.assertTrue(check_result is not None, f'granule_id2 - new_index_name1 {check_result}')

        ####   index v2 ####
        granules_db_index.create_new_index(self.tenant, self.tenant_venue, self.custom_metadata_body2)
        sleep(2)
        self.assertTrue(es.has_index(new_index_name2), f'missing {new_index_name2}')

        granules_db_index.add_entry(self.tenant, self.tenant_venue, mock_feature3, granule_id3)
        sleep(2)
        check_result = es.query_by_id(granule_id3, new_index_name2)
        self.assertTrue(check_result is not None, f'granule_id3 - new_index_name2 {check_result}')

        check_result = es.query_by_id(granule_id3, new_index_name1)
        self.assertTrue(check_result is None, f'granule_id3 - new_index_name1 is not None{check_result}')

        granules_db_index.update_entry(self.tenant, self.tenant_venue, {'archive_status': 'cnm_s_failed'}, granule_id1)
        sleep(2)
        check_result = es.query_by_id(granule_id1, new_index_name2)
        self.assertTrue(check_result is not None, f'granule_id1 - new_index_name2 {check_result}')

        check_result = es.query_by_id(granule_id1, new_index_name1)
        self.assertTrue(check_result is None, f'granule_id1 - new_index_name1 is not None{check_result}')

        granules_db_index.update_entry(self.tenant, self.tenant_venue, {'archive_status': 'cnm_s_successful'}, granule_id3)
        sleep(2)
        check_result = es.query_by_id(granule_id3, new_index_name2)
        self.assertTrue(check_result is not None, f'granule_id3 - new_index_name2 {check_result}')

        check_result = es.query_by_id(granule_id3, new_index_name1)
        self.assertTrue(check_result is None, f'granule_id3 - new_index_name1 is not None{check_result}')

        ####   index v3 ####
        granules_db_index.create_new_index(self.tenant, self.tenant_venue, self.custom_metadata_body3)
        sleep(2)
        self.assertTrue(es.has_index(new_index_name3), f'missing {new_index_name3}')

        with self.assertRaises(ValueError) as context:
            granules_db_index.update_entry(self.tenant, self.tenant_venue, {'archive_status': 'cnm_s_failed'}, granule_id4)
        sleep(2)
        self.assertTrue(str(context.exception).startswith('unable to update'))
        # TODO check error
        granules_db_index.update_entry(self.tenant, self.tenant_venue, {'archive_status': 'cnm_r_failed'}, granule_id2)
        sleep(2)
        check_result = es.query_by_id(granule_id2, new_index_name3)
        self.assertTrue(check_result is not None, f'granule_id2 - new_index_name3 {check_result}')

        check_result = es.query_by_id(granule_id2, new_index_name1)
        self.assertTrue(check_result is None, f'granule_id2 - new_index_name1 is not None{check_result}')

        check_result = es.query_by_id(granule_id2, new_index_name2)
        self.assertTrue(check_result is None, f'granule_id2 - new_index_name2 is not None{check_result}')

        granules_db_index.update_entry(self.tenant, self.tenant_venue, {'archive_status': 'cnm_s_failed'}, granule_id3)
        sleep(2)
        check_result = es.query_by_id(granule_id3, new_index_name3)
        self.assertTrue(check_result is not None, f'granule_id3 - new_index_name3 {check_result}')

        check_result = es.query_by_id(granule_id3, new_index_name1)
        self.assertTrue(check_result is None, f'granule_id3 - new_index_name1 is not None{check_result}')

        check_result = es.query_by_id(granule_id3, new_index_name2)
        self.assertTrue(check_result is None, f'granule_id3 - new_index_name2 is not None{check_result}')

        if es.has_index(new_index_name1):
            es.delete_index(new_index_name1)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v01'.lower().strip())
        if es.has_index(new_index_name2):
            es.delete_index(new_index_name2)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v02'.lower().strip())
        if es.has_index(new_index_name3):
            es.delete_index(new_index_name3)
            es.delete_index(f'{DBConstants.granules_index_prefix}_{self.tenant}_{self.tenant_venue}_perc__v03'.lower().strip())

        return
