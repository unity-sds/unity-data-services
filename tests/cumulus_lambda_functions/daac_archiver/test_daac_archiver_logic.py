import json
import os
from time import sleep
from unittest import TestCase

from cumulus_lambda_functions.daac_archiver.daac_archiver_logic import DaacArchiverLogic
from cumulus_lambda_functions.lib.uds_db.archive_index import UdsArchiveConfigIndex


class TestDaacArchiverLogic(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tenant = 'UDS_LOCAL_TEST'  # 'uds_local_test'  # 'uds_sandbox'
        self.tenant_venue = 'DEV'  # 'DEV1'  # 'dev'
        self.collection_name = 'UDS_COLLECTION'  # 'uds_collection'  # 'sbx_collection'
        self.collection_version = '24.07.23.17.00'.replace('.', '')  # '2402011200'

    def test_01_send_to_daac(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        archive_index = UdsArchiveConfigIndex(os.environ['ES_URL'], int(os.environ['ES_PORT']), os.getenv('ES_TYPE', 'AWS'), os.getenv('ES_USE_SSL', 'TRUE').strip() is True)
        archive_index.set_tenant_venue(self.tenant, self.tenant_venue)
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        temp_collection_id_no_version = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}'
        ingesting_dict = {
            'daac_collection_id': f'MOCK:DAAC-1:{self.collection_name}',
            'daac_sns_topic_arn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns',
            'daac_data_version': '123',
            'collection': temp_collection_id_no_version,
            'ss_username': 'unit_test',
            # 'archiving_types': [],
            'archiving_types': [  # TODO this is not working correctly.
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},
            ],
        }
        archive_index.add_new_config(ingesting_dict)
        sleep(3)
        sample_msg = {"collection": temp_collection_id_no_version,
                      "identifier": f"{temp_collection_id}:abcd.1234.efgh.test_file05",
                      "submissionTime": "2024-07-23T21:45:12.217650", "provider": "unity", "version": "1.6.0",
                      "product": {"dataVersion": "2407231700", "files": [
                          {"type": "data", "name": "abcd.1234.efgh.test_file05.data.stac.json",
                           "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.data.stac.json",
                           "checksumType": "md5", "checksum": "unknown", "size": -1},
                          {"type": "metadata", "name": "abcd.1234.efgh.test_file05.nc.cas",
                           "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.nc.cas",
                           "checksumType": "md5", "checksum": "unknown", "size": -1},
                          {"type": "metadata", "name": "abcd.1234.efgh.test_file05.nc.stac.json",
                           "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.nc.stac.json",
                           "checksumType": "md5", "checksum": "unknown", "size": -1},
                          {"type": "metadata", "name": "abcd.1234.efgh.test_file05.cmr.xml",
                           "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.cmr.xml",
                           "checksumType": "md5", "checksum": "5168713c028cd169c59b10b8c3e1ead1", "size": 1783}],
                                  "name": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2407231700:abcd.1234.efgh.test_file05"},
                      "receivedTime": "2024-07-23T21:46:42.015Z", "response": {"status": "SUCCESS"},
                      "processCompleteTime": "2024-07-23T21:47:14.530Z"}
        sns_msg = {
            "Type": "Notification",
            "MessageId": "f6441383-4a99-5f27-8a66-4e44177ea7f4",
            "TopicArn": "arn:aws:sns:us-west-2:xxx:uds-sbx-cumulus-report-granules-topic",
            "Message": json.dumps(sample_msg),
            "Timestamp": "2023-11-09T22:22:31.148Z",
            "SignatureVersion": "1",
            "Signature": "xxx/Jdya+6a42805KvAn6PrZIwXdKHE+ng37e+aN75SuCTDrv5hzeRFxA8YSoEYMG+00CvnoVN3gtsVt/o78Nkj5lr2oMCwNj2k5kwyEve4BetRelyXF1BTc7ptD7MYsSVGrIWZQwqNqUviDfBdI1nxujDiZvWnjAPWjJA8+cjx2acFAbaTzIhN90V3Fn0yOtveVXblAUZQ3EwF8Cv0CsTJFVPYliguw72s2r+9xPbc5Yj8dBL4B38HI7JC+u6qL8vgzIh+/wVlpqOef5P23qFeYDE533318EUEDfrkRs//LCbe+lcoTzka5qwOWaveMbIM9tstmeg==",
            "SigningCertURL": "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem",
            "UnsubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-report-granules-topic:c003b5ee-09a7-4129-9873-a1629868e8bd"
        }
        sqs_event = {
            "Records": [
                {
                    "messageId": "6210f778-d081-4ae9-a861-8534d612dfae",
                    "receiptHandle": "xxx/PcVuIG9Em/a6/4AHIA4G5vLPiHVElNiuMfYc1ussk2U//JwZbD788Fv8u6W22L3AJ1U8EIcGJ57aibpmd6tSCWLS5q5FA4u2X2Jq5z+lCX5NZXzNDYMqMJaCGtBkcYi4a9LDXtD+U7HWX0V8OPhFFF2a1qUu+E05c16f5OmE7wRJ3SFrRmtJOhp2DigKKsw6VJtZklTm6uILMOL1ETOTlbA02dhF16fjcXlAACirDp0Yo9pi91FrpEljOYkqAO9AX4WMbEjAPZrnaATfYmRqCTOlnrIK8xvgEPgIu/OOub7KBYh6AQn7U8QBNoASkXkn31dqyM2I+KosKy2VeJO9cjPTahhXtkW7zUFA6863Czt2oHqL6Rvwsjr+7TikfQ==",
                    "body": json.dumps(sns_msg),
                    "attributes": {
                        "ApproximateReceiveCount": "6",
                        "SentTimestamp": "1644255065441",
                        "SenderId": "AIDALVP5ID7KAVBU2CQ3O",
                        "ApproximateFirstReceiveTimestamp": "1644255065441"
                    },
                    "messageAttributes": {},
                    "md5OfBody": "00cb0a5ed122862537ab6115dae36f69",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws-us-gov:sqs:us-gov-west-1:xxx:send_records_to_es",
                    "awsRegion": "us-gov-west-1"
                }
            ]
        }
        # print(json.dumps(sqs_event))
        daac_archiver = DaacArchiverLogic()
        daac_archiver.send_to_daac(sqs_event)
        return

    def test_02_receive_from_daac(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'
        archive_index = UdsArchiveConfigIndex(os.environ['ES_URL'], int(os.environ['ES_PORT']), os.getenv('ES_TYPE', 'AWS'), os.getenv('ES_USE_SSL', 'TRUE').strip() is True)
        archive_index.set_tenant_venue(self.tenant, self.tenant_venue)
        temp_collection_id = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}___{self.collection_version}'
        temp_collection_id_no_version = f'URN:NASA:UNITY:{self.tenant}:{self.tenant_venue}:{self.collection_name}'

        sleep(3)
        sample_msg = {'version': '1.6.1', 'submissionTime': '2024-07-30T17:29:01.925477Z', 'receivedTime': '2024-07-30T17:28:55.085776Z', 'processCompleteTime': '2024-07-30T17:29:01.925508Z', 'collection': 'DAAC:MOCK:UDS_UNIT_COLLECTION', 'identifier': 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_UNIT_COLLECTION___2407291400:abcd.1234.efgh.test_file05', 'response': {'status': 'SUCCESS'}}
        sns_msg = {
            "Type": "Notification",
            "MessageId": "f6441383-4a99-5f27-8a66-4e44177ea7f4",
            "TopicArn": "arn:aws:sns:us-west-2:xxx:uds-sbx-cumulus-report-granules-topic",
            "Message": json.dumps(sample_msg),
            "Timestamp": "2023-11-09T22:22:31.148Z",
            "SignatureVersion": "1",
            "Signature": "xxx/Jdya+6a42805KvAn6PrZIwXdKHE+ng37e+aN75SuCTDrv5hzeRFxA8YSoEYMG+00CvnoVN3gtsVt/o78Nkj5lr2oMCwNj2k5kwyEve4BetRelyXF1BTc7ptD7MYsSVGrIWZQwqNqUviDfBdI1nxujDiZvWnjAPWjJA8+cjx2acFAbaTzIhN90V3Fn0yOtveVXblAUZQ3EwF8Cv0CsTJFVPYliguw72s2r+9xPbc5Yj8dBL4B38HI7JC+u6qL8vgzIh+/wVlpqOef5P23qFeYDE533318EUEDfrkRs//LCbe+lcoTzka5qwOWaveMbIM9tstmeg==",
            "SigningCertURL": "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem",
            "UnsubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-report-granules-topic:c003b5ee-09a7-4129-9873-a1629868e8bd"
        }
        sqs_event = {
            "Records": [
                {
                    "messageId": "6210f778-d081-4ae9-a861-8534d612dfae",
                    "receiptHandle": "xxx/PcVuIG9Em/a6/4AHIA4G5vLPiHVElNiuMfYc1ussk2U//JwZbD788Fv8u6W22L3AJ1U8EIcGJ57aibpmd6tSCWLS5q5FA4u2X2Jq5z+lCX5NZXzNDYMqMJaCGtBkcYi4a9LDXtD+U7HWX0V8OPhFFF2a1qUu+E05c16f5OmE7wRJ3SFrRmtJOhp2DigKKsw6VJtZklTm6uILMOL1ETOTlbA02dhF16fjcXlAACirDp0Yo9pi91FrpEljOYkqAO9AX4WMbEjAPZrnaATfYmRqCTOlnrIK8xvgEPgIu/OOub7KBYh6AQn7U8QBNoASkXkn31dqyM2I+KosKy2VeJO9cjPTahhXtkW7zUFA6863Czt2oHqL6Rvwsjr+7TikfQ==",
                    "body": json.dumps(sns_msg),
                    "attributes": {
                        "ApproximateReceiveCount": "6",
                        "SentTimestamp": "1644255065441",
                        "SenderId": "AIDALVP5ID7KAVBU2CQ3O",
                        "ApproximateFirstReceiveTimestamp": "1644255065441"
                    },
                    "messageAttributes": {},
                    "md5OfBody": "00cb0a5ed122862537ab6115dae36f69",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws-us-gov:sqs:us-gov-west-1:xxx:send_records_to_es",
                    "awsRegion": "us-gov-west-1"
                }
            ]
        }
        # print(json.dumps(sqs_event))
        daac_archiver = DaacArchiverLogic()
        daac_archiver.receive_from_daac(sqs_event)
        return
