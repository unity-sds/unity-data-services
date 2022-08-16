import unittest
import os
import tempfile

from cumulus_lambda_functions.cumulus_upload_granules.upload_granules import UploadGranules


class TestLUploadGranules(unittest.TestCase):
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
                ff.write('''<?xml version="1.0" encoding="UTF-8" ?>
<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">
    <keyval type="scalar">
        <key>AggregateDir</key>
        <val>snppatmsl1a</val>
    </keyval>
    <keyval type="vector">
        <key>AutomaticQualityFlag</key>
        <val>Passed</val>
    </keyval>
    <keyval type="vector">
        <key>BuildId</key>
        <val>v01.43.00</val>
    </keyval>
    <keyval type="vector">
        <key>CollectionLabel</key>
        <val>L1AMw_nominal2</val>
    </keyval>
    <keyval type="scalar">
        <key>DataGroup</key>
        <val>sndr</val>
    </keyval>
    <keyval type="scalar">
        <key>EndDateTime</key>
        <val>2016-01-14T10:06:00.000Z</val>
    </keyval>
    <keyval type="scalar">
        <key>EndTAI93</key>
        <val>726919569.000</val>
    </keyval>
    <keyval type="scalar">
        <key>FileFormat</key>
        <val>nc4</val>
    </keyval>
    <keyval type="scalar">
        <key>FileLocation</key>
        <val>/pge/out</val>
    </keyval>
    <keyval type="scalar">
        <key>Filename</key>
        <val>SNDR.SNPP.ATMS.L1A.nominal2.02.nc</val>
    </keyval>
    <keyval type="vector">
        <key>GranuleNumber</key>
        <val>101</val>
    </keyval>
    <keyval type="scalar">
        <key>JobId</key>
        <val>f163835c-9945-472f-bee2-2bc12673569f</val>
    </keyval>
    <keyval type="scalar">
        <key>ModelId</key>
        <val>urn:npp:SnppAtmsL1a</val>
    </keyval>
    <keyval type="scalar">
        <key>NominalDate</key>
        <val>2016-01-14</val>
    </keyval>
    <keyval type="vector">
        <key>ProductName</key>
        <val>SNDR.SNPP.ATMS.20160114T1000.m06.g101.L1A.L1AMw_nominal2.v03_15_00.D.201214135000.nc</val>
    </keyval>
    <keyval type="scalar">
        <key>ProductType</key>
        <val>SNDR_SNPP_ATMS_L1A</val>
    </keyval>
    <keyval type="scalar">
        <key>ProductionDateTime</key>
        <val>2020-12-14T13:50:00.000Z</val>
    </keyval>
    <keyval type="vector">
        <key>ProductionLocation</key>
        <val>Sounder SIPS: JPL/Caltech (Dev)</val>
    </keyval>
    <keyval type="vector">
        <key>ProductionLocationCode</key>
        <val>D</val>
    </keyval>
    <keyval type="scalar">
        <key>RequestId</key>
        <val>1215</val>
    </keyval>
    <keyval type="scalar">
        <key>StartDateTime</key>
        <val>2016-01-14T10:00:00.000Z</val>
    </keyval>
    <keyval type="scalar">
        <key>StartTAI93</key>
        <val>726919209.000</val>
    </keyval>
    <keyval type="scalar">
        <key>TaskId</key>
        <val>8c3ae101-8f7c-46c8-b5c6-63e7b6d3c8cd</val>
    </keyval>
</cas:metadata>''')
            self.assertEqual('Registered', UploadGranules().start(), 'wrong registration result')
        return
