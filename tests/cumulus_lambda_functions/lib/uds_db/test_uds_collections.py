import uuid
from unittest import TestCase

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections


class TestUdsCollections(TestCase):
    def test_01(self):
        uds_collection = UdsCollections('https://search-uds-local-sample-iuthdh4e3yqre3mcfjtlfmxbua.us-west-2.es.amazonaws.com', 443, 'AWS')
        collection_prefix = f'urn:nasa:unity:unitty_project_1:DEV_001:ecm_{uuid.uuid4()}'
        collection_id = f'{collection_prefix}_test_1___1'
        uds_collection.add_collection(collection_id, 0, 10, [0.1, 1.2, 2.3, 3.4], 12)
        collections = uds_collection.get_collections([f'{collection_prefix}.*'])
        self.assertEqual(1, len(collections))
        uds_collection.delete_collection(collection_id)
        collections = uds_collection.get_collections([f'{collection_prefix}.*'])
        self.assertEqual(0, len(collections))
        return

    def test_02(self):
        temp_collection_id = f'URN:NASA:UNITY:UDS_LOCAL:DEV:COLLECTION1___V1.1'
        aa = UdsCollections.decode_identifier(temp_collection_id)
        print(aa)
        granule_id = f"{temp_collection_id}:abcd.1234.efgh.test_file05"
        aa = UdsCollections.decode_identifier(granule_id)
        self.assertEqual(aa.venue, 'DEV', f'wrong venue')
        self.assertEqual(aa.tenant, 'UDS_LOCAL', f'wrong tenant')
        print(aa)
        return

