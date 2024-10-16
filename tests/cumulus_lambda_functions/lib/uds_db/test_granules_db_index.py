import json
import os
from unittest import TestCase

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
        self.tenant = 'UDS_MY_LOCAL_ARCHIVE_TEST'  # 'uds_local_test'  # 'uds_sandbox'
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
                    'must': {'term': {'collection': {'value': f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:UDS_UNIT_COLLECTION___2408290522'}}}
                }
            },
        }
        granules_index = GranulesDbIndex()
        query_result = granules_index.dsl_search(self.tenant, self.tenant_venue, search_dsl)
        print(json.dumps(query_result, indent=4))
        # self.assertEqual(custom_metadata, expected)
        return