from unittest import TestCase

from cumulus_lambda_functions.daac_archiver.catalia_auth_db import CataliaAuthDb


class TestCataliaAuthDb(TestCase):
    def test_01(self):
        cad = CataliaAuthDb('h5s_on_disk_william_local')
        cad.add('A', 'X:Y:.*', '.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0_V1', 'M:N:L0.*', False)
        cad.add('A', 'X:Y:L0.*', 'M:N:L0.*', True)
        cad.add('A', 'X:Y:L1_V1', 'M:N:L1.*', True)

        self.assertFalse(cad.authorize('B', 'X', 'X'))
        self.assertFalse(cad.authorize('A', 'X:Y:L0_V1', 'M:N:L0_V1'))
        self.assertFalse(cad.authorize('A', 'X:Y:L1_V1', 'M:N:L0_V1'))
        self.assertTrue(cad.authorize('A', 'X:Y:L1_V1', 'M:N:L1_V1'))
        self.assertTrue(cad.authorize('A', 'X:Y:L0_V2', 'M:N:L0_V1'))
        self.assertFalse(cad.authorize('A', 'X:Y:L0_V2', 'M:N:L1_V1'))
        return
