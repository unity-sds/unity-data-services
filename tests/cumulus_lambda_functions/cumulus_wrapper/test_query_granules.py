from unittest import TestCase

from cumulus_lambda_functions.cumulus_wrapper.query_granules import GranulesQuery


class TestGranulesQuery(TestCase):
    def test_01(self):
        lambda_prefix = 'uds-dev-cumulus'

        query_granules = GranulesQuery('NA', 'NA')
        query_granules.with_collection_id('SNDR_SNPP_ATMS_L1B_OUTPUT___1')
        query_granules.with_limit(7)
        granules = query_granules.query_direct_to_private_api(lambda_prefix)
        self.assertTrue('results' in granules, f'results not in collections: {granules}')
        # self.assertEqual(7, len(granules['results']), f'wrong length: {granules}')
        return

    def test_02(self):
        lambda_prefix = 'uds-dev-cumulus'

        query_granules = GranulesQuery('NA', 'NA')
        query_granules.with_collection_id('NEW_COLLECTION_EXAMPLE_L1B___9')
        query_granules.with_limit(2)
        query_granules.with_filter('id', ['NEW_COLLECTION_EXAMPLE_L1B___9:test_file01', 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file02'])
        granules = query_granules.query_direct_to_private_api(lambda_prefix)
        self.assertTrue('results' in granules, f'results not in collections: {granules}')
        # self.assertEqual(2, len(granules['results']), f'wrong length: {granules}')
        # self.assertEqual(granules['results'][0]['id'], 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file01')
        # self.assertEqual(granules['results'][1]['id'], 'NEW_COLLECTION_EXAMPLE_L1B___9:test_file02')
        return
