import os
import time
from unittest import TestCase

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.aws.es_abstract import ESAbstract

from cumulus_lambda_functions.lib.aws.es_factory import ESFactory


class TestESMiddleware(TestCase):
    def test_migrate_index_data_01(self):
        os.environ['ES_URL'] = 'https://vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        # os.environ['ES_URL'] = 'localhost'
        os.environ['ES_PORT'] = '9200'
        es: ESAbstract = ESFactory().get_instance('NO_AUTH',
                                                 index=DBConstants.collections_index,
                                                 base_url=os.getenv('ES_URL'),
                                                 port=int(os.getenv('ES_PORT', '443'))
                                                 )
        test_index_name = 'TestESMiddleware'.lower()
        es.delete_index(f'{test_index_name}_01')
        es.delete_index(f'{test_index_name}_02')
        es.create_index(f'{test_index_name}_01', {
          "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
          },
          "mappings": {
                        "dynamic": "strict",
                        "properties": {
                          "collection": {"type": "keyword"},
                        }
                    }
        })

        es.create_index(f'{test_index_name}_02', {
          "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
          },
          "mappings": {
                        "dynamic": "strict",
                        "properties": {
                          "collection": {"type": "keyword"},
                            "grr": {"type": "keyword"}
                        }
                    }
        })
        self.assertEqual(True, es.has_index(f'{test_index_name}_01'), f'{test_index_name}_01 does exist')
        self.assertEqual(True, es.has_index(f'{test_index_name}_02'), f'{test_index_name}_02 does exist')
        self.assertEqual(False, es.has_index(f'{test_index_name}_03'), f'{test_index_name}_03 does NOT exist')

        for j in range(15):
            j *= 10000
            documents = {
                f'collection_{j+i}': {'collection': f'collection_{j+i}'} for i in range(1000)
            }
            result = es.index_many(doc_dict=documents, index=f'{test_index_name}_01')
            print(result)
        result = es.migrate_index_data(f'{test_index_name}_01', f'{test_index_name}_02')
        print(result)
        time.sleep(5)
        result = es.query({'track_total_hits': True, 'size': 0, 'query': {'match_all': {}}}, f'{test_index_name}_01')
        self.assertEqual(0, es.get_result_size(result), 'old index is empty')
        result = es.query({'track_total_hits': True, 'size': 0, 'query': {'match_all': {}}}, f'{test_index_name}_02')
        self.assertEqual(15000, es.get_result_size(result), 'new index is not empty')
        with self.assertRaises(ValueError) as context:
            result = es.migrate_index_data(f'{test_index_name}_03', f'{test_index_name}_02')
        self.assertTrue(str(context.exception).startswith('at least one of the indices do not exist'))
        query_by_id = es.query_by_id('collection_10000', f'{test_index_name}_02')
        self.assertTrue(query_by_id is not None, f'query_by_id is None')
        print(f'query_by_id: {query_by_id}')
        query_by_id = es.query_by_id('collection_40000', f'{test_index_name}_02')
        self.assertTrue(query_by_id is None, f'query_by_id is not None: {query_by_id}')

        return

