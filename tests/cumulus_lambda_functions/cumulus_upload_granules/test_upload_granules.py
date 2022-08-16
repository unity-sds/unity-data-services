import os
import tempfile
from unittest import TestCase


from cumulus_lambda_functions.cumulus_upload_granules.upload_granules import UploadGranules
from cumulus_lambda_functions.lib.utils.file_utils import FileUtils

print(UploadGranules().start())


class TestL1aInputMetadata(TestCase):
    def test_01(self):
        os.environ['DAPA_API'] = 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev'
        os.environ['USERNAME'] = '/unity/uds/user/wphyo/username'
        os.environ['PASSWORD'] = '/unity/uds/user/wphyo/dwssap'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '7a1fglm2d54eoggj13lccivp25'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'

        os.environ['COLLECTION_ID'] = 'SNDR_SNPP_ATMS_L1A_NGA___1'
        os.environ['PROVIDER_ID'] = 'SNPP'
        os.environ['UPLOAD_DIR'] = '/tmp/snpp_upload_test_1'
        os.environ['STAGING_BUCKET'] = 'am-uds-dev-cumulus-staging'
        os.environ['VERIFY_SSL'] = 'false'
        os.environ['DELETE_FILES'] = 'false'

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            with open(os.path.join(tmp_dir_name, 'Downloads/SNDR.SNPP.ATMS.L1A.nominal2.02.nc')) as ff:
                ff.write('sample_file')
            with open(os.path.join(tmp_dir_name, 'Downloads/SNDR.SNPP.ATMS.L1A.nominal2.02.nc.cas')) as ff:
        return
