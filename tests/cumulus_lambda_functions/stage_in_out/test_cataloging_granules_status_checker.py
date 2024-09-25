import os
from unittest import TestCase

from mdps_ds_lib.lib.constants import Constants
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stage_in_out.cataloging_granules_status_checker import CatalogingGranulesStatusChecker


class TestCatalogingGranulesStatusChecker(TestCase):
    def test_01(self):
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'

        cgsc = CatalogingGranulesStatusChecker('NEW_COLLECTION_EXAMPLE_L1B___9',
                                               ['NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
                                                'NEW_COLLECTION_EXAMPLE_L1B___9:test_file02'],
                                               TimeUtils().get_datetime_obj().timestamp(),
                                               30,
                                               5,
                                               False)
        status = cgsc.verify_one_time()
        self.assertTrue('missing_granules' in status, f'missing missing_granules')
        self.assertTrue('registered_granules' in status, f'missing registered_granules')
        self.assertEqual(len(status['missing_granules']), 2, f'mismatched registered_granules')
        self.assertEqual(len(status['registered_granules']), 0, f'mismatched registered_granules')
        return

    def test_02(self):
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'

        cgsc = CatalogingGranulesStatusChecker('NEW_COLLECTION_EXAMPLE_L1B___9',
                                               ['NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
                                                'NEW_COLLECTION_EXAMPLE_L1B___9:test_file02'],
                                               TimeUtils().parse_from_str('1980-01-01T00:00:00+00:00').get_datetime_obj().timestamp(),
                                               30,
                                               5,
                                               False)
        status = cgsc.verify_one_time()
        self.assertTrue('missing_granules' in status, f'missing missing_granules')
        self.assertTrue('registered_granules' in status, f'missing registered_granules')
        self.assertEqual(len(status['missing_granules']), 0, f'mismatched missing_granules')
        self.assertEqual(len(status['registered_granules']), 2, f'mismatched registered_granules')
        return

    def test_03(self):
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '6ir9qveln397i0inh9pmsabq1'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['GRANULES_CATALOG_TYPE'] = 'UNITY'

        cgsc = CatalogingGranulesStatusChecker('NEW_COLLECTION_EXAMPLE_L1B___9',
                                               ['NEW_COLLECTION_EXAMPLE_L1B___9:test_file01',
                                                'NEW_COLLECTION_EXAMPLE_L1B___9:test_file02'],
                                               TimeUtils().get_datetime_obj().timestamp(),
                                               5,
                                               3,
                                               False)
        status = cgsc.verify_n_times()
        self.assertTrue('missing_granules' in status, f'missing missing_granules')
        self.assertTrue('registered_granules' in status, f'missing registered_granules')
        self.assertEqual(len(status['missing_granules']), 2, f'mismatched registered_granules')
        self.assertEqual(len(status['registered_granules']), 0, f'mismatched registered_granules')
        return
