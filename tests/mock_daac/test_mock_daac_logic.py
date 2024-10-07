import json
from unittest import TestCase

from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from cumulus_lambda_functions.mock_daac.mock_daac_logic import MockDaacLogic


class TestMockDaacLogic(TestCase):
    def test_01(self):
        sample_cnm_message = {
            "collection": "MY_DAAC",
            "identifier": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100:abcd.1234.efgh.test_file05",
            "submissionTime": f'{TimeUtils.get_current_time()}Z',
            "provider": "DEV",  # TODO need to pull this from granule ID
            "version": "1.6.0",
            "product": {
                "name": "UDS_COLLECTION___2404251100:abcd.1234.efgh.test_file05",  # TODO extract granule ID Everything after tenant/venue."
                "dataVersion": "123",  # TODO ask user to provide it in config,
                "files": [
                    {
                        "name": "abcd.1234.efgh.test_file05.data.stac.json",
                        "type": "data",
                        "uri": "s3://unity-dev-cumulus-unity-william-test-1/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.data.stac.json",
                        "checksumType": "md5",
                        "checksum": "unknown",
                        "size": -1
                    },
                    {
                        "name": "abcd.1234.efgh.test_file05.nc.cas",
                        "type": "metadata",
                        "uri": "s3://unity-dev-cumulus-unity-william-test-1/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.nc.cas",
                        "checksumType": "md5",
                        "checksum": "unknown",
                        "size": -1
                    },
                    {
                        "name": "abcd.1234.efgh.test_file05.nc.stac.json",
                        "type": "metadata",
                        "uri": "s3://unity-dev-cumulus-unity-william-test-1/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2404251100:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.nc.stac.json",
                        "checksumType": "md5",
                        "checksum": "unknown",
                        "size": -1
                    }
                ]
            }
        }
        input_event = {'Records': [{
            'EventSource': 'aws:sns',
            'EventVersion': '1.0',
            'EventSubscriptionArn': 'arn:aws:sns:us-west-2:xxx:uds-sbx-cumulus-mock_daac_cnm_sns:xxx-2c1a-4139-af3f-bbc2921ea50b',
            'Sns': {'Type': 'Notification', 'MessageId': 'xxx-4d7b-5f56-a46e-1110e4ac1f51',
                    'TopicArn': 'arn:aws:sns:us-west-2:xxx:uds-sbx-cumulus-mock_daac_cnm_sns',
                    'Subject': '',  # TODO will this always be present?
                    'Message': json.dumps(sample_cnm_message),
                    'Timestamp': '2024-07-19T17:51:19.598Z', 'SignatureVersion': '1',
                    'Signature': 'xxx/vjLRFJbL0e2/6I0M2rlMJwSC/doS87PNCZ9NW+QPhyr/LmfSib1rfqbGMSIVBA3V1VbXokwvYqTwE05S8+UltEhezgexqDqxd/xxx/F2xFB0vgjKvdTQg+c3KDNIUzukcvNexDVfrp8QMEv/7/kO8A5JVYu0HagiBcIdVWPhgFjtTdcs0A3qSYx5C+sqoSX2Cb+opUZESQ9iNax5vZ1nZxokicSFqOts8uoSNDBE9x695BBET9IRD140bE3iF7xT5ZOQ==', 'SigningCertUrl': 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-60eadc530605d63b8e62a523676ef735.pem',
                    'UnsubscribeUrl': 'https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:xx:uds-sbx-cumulus-mock_daac_cnm_sns:xxx-2c1a-4139-af3f-bbc2921ea50b',
                    'MessageAttributes': {}}
        }]}
        MockDaacLogic().start(input_event)
        return
