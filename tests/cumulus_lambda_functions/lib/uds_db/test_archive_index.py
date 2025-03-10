from time import sleep
from unittest import TestCase

from cumulus_lambda_functions.lib.uds_db.archive_index import UdsArchiveConfigIndex


class TestUdsArchiveConfigIndex(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'

    def test_01(self):
        collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:unit_test_1'
        archive_index = UdsArchiveConfigIndex('vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com', 9200, 'AWS', True)
        archive_index.set_tenant_venue(self.tenant, self.tenant_venue)
        ingesting_dict = {
            'daac_collection_id': 'daac_unit_test_collection',
            'daac_sns_topic_arn': 'daac_unit_test_sns',
            'daac_data_version': 'unit_test',
            'collection': collection_id,
            'ss_username': 'unit_test',
            'archiving_types': [
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},
            ],
        }
        archive_index.add_new_config(ingesting_dict)
        sleep(3)
        result = archive_index.get_config(collection_id)
        result_len = len(result)
        self.assertTrue(result_len > 0, f'has no result: {result}')
        print(result)
        archive_index.delete_config(collection_id, 'daac_unit_test_collection')
        sleep(3)
        result1 = archive_index.get_config(collection_id)
        self.assertEqual(result_len -1, len(result1), f'has no result: {result}')
        return
