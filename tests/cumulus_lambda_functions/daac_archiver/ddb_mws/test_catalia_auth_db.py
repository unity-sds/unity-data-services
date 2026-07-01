from unittest import TestCase

from cumulus_lambda_functions.daac_archiver.ddb_mws.catalia_auth_db import CataliaAuthDb


class TestCataliaAuthDb(TestCase):
    catalia_db_name = 'h5s_on_disk_william_local'
    def test_01(self):
        cad = CataliaAuthDb(self.catalia_db_name)
        cad.add('A', 'X:Y:.*', '.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0_V1', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', True)
        cad.add('A', 'X:Y:L1_V1', 'M:N:L1.*', True)

        self.assertFalse(cad.authorize('B', 'X', 'X'))
        self.assertFalse(cad.authorize('A', 'X:Y:L0_V1', 'M:N:L0_V1'))
        self.assertFalse(cad.authorize('A', 'X:Y:L1_V1', 'M:N:L0_V1'))
        self.assertTrue(cad.authorize('A', 'X:Y:L1_V1', 'M:N:L1_V1'))
        self.assertTrue(cad.authorize('A', 'x:y:L0_V2', 'M:N:L0_V1'))
        self.assertFalse(cad.authorize('A', 'x:y:L0_V2', 'M:N:L1_V1'))
        return

    def test_01(self):
        cad = CataliaAuthDb(self.catalia_db_name)
        cad.add('A', 'X:Y:.*', '.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0_V1', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', True)
        cad.add('A', 'X:Y:L1_V1', 'M:N:L1.*', True)

        user_groups = cad.get_authorized_catalia(['A', 'B', 'C'], 'X:Y:L1_V1')
        self.assertEqual(2, len(user_groups), f'wrong user groups: {user_groups}')

        daacs = cad.get_authorized_daac(user_groups, 'X:Y:L1_V1', ['M:N:L1_V1', 'M:N:L1_V2', 'M:N:L0_V1'])
        self.assertEqual(2, len(daacs), f'wrong user groups: {user_groups}')
        daacs = cad.get_authorized_daac(user_groups, 'X:Y:L0_V1', ['M:N:L1_V1', 'M:N:L0_V2', 'M:N:L0_V1'])
        self.assertEqual(1, len(daacs), f'wrong user groups: {user_groups}')
        daacs = cad.get_authorized_daac(user_groups, 'X:Y:L0_V1', ['M:N:L0_V2', 'M:N:L0_V1'])
        self.assertEqual(0, len(daacs), f'wrong user groups: {user_groups}')
        user_groups = cad.get_authorized_catalia(['B', 'C'], 'X:Y:L1_V1')
        self.assertEqual(0, len(user_groups), f'wrong user groups: {user_groups}')
        user_groups = cad.get_authorized_catalia(['A', 'B', 'C'], 'X:Y1:L2_V1')
        self.assertEqual(0, len(user_groups), f'wrong user groups: {user_groups}')
        debug = 1
        return
