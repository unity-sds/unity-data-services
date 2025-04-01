import json
import os
from time import sleep
from unittest import TestCase

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from pystac import Item, Asset

from cumulus_lambda_functions.granules_to_es.granules_indexer import GranulesIndexer
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex


class TestGranulesIndexer(TestCase):
    def test_01(self):
        os.environ['ES_URL'] = 'vpc-uds-sbx-cumulus-es-qk73x5h47jwmela5nbwjte4yzq.us-west-2.es.amazonaws.com'
        os.environ['ES_PORT'] = '9200'

        s3 = AwsS3()
        mock_stac_item = Item(id='URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01',
                         geometry={
                             "type": "Point",
                             "coordinates": [0.0, 0.0]
                         },
                         bbox=[0.0, -10.0, 10.0, 0.0],
                         datetime=TimeUtils().parse_from_unix(9876543210, True).get_datetime_obj(),
                         properties={
                             "start_datetime": "2016-01-31T18:00:00.009057Z",
                             "end_datetime": "2016-01-31T19:59:59.991043Z",
                             "created": "2016-02-01T02:45:59.639000Z",
                             "updated": "2022-03-23T15:48:21.578000Z",
                             "datetime": "2022-03-23T15:48:19.079000Z",
                         },
                         collection='URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417',
                         assets={
                             'data': Asset('test_file01.nc', title='main data'),
                             'metadata': Asset('test_file01.cmr.xml', title='metadata cas'),
                             'metadata__cas': Asset('test_file01.nc.cas', title='metadata cas'),
                             'metadata__stac': Asset('test_file01.nc.stac.json', title='metadata stac'),
                         })
        s3.set_s3_url('s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.stac.json')\
          .upload_bytes(json.dumps(mock_stac_item.to_dict(False, False)).encode())
        cumulus_msg = {
            "event": "Update",
            "record": {
                "collectionId": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417",
                "createdAt": 1699568555580,
                "duration": 36.81,
                "error": {
                    "Cause": "None",
                    "Error": "Unknown Error"
                },
                "execution": "https://console.aws.amazon.com/states/home?region=us-west-2#/executions/details/arn:aws:states:us-west-2:237868187491:execution:uds-sbx-cumulus-CatalogGranule:3ae4c03e-dcd1-4d25-8b8a-b8c2a3c126ae",
                "granuleId": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01",
                "processingEndDateTime": "2023-11-09T22:22:45.944Z",
                "processingStartDateTime": "2023-11-09T22:22:10.949Z",
                "productVolume": "1765",
                "provider": "unity",
                "published": False,
                "status": "completed",
                "timestamp": 1699568567282,
                "timeToArchive": 0,
                "timeToPreprocess": 20.302,
                "updatedAt": 1699568567282,
                "files": [
                    {
                        "bucket": "uds-sbx-cumulus-staging",
                        "checksum": "9817be382b87c48ebe482b9c47d1525a",
                        "checksumType": "md5",
                        "fileName": "test_file01.cmr.xml",
                        "key": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.cmr.xml",
                        "size": 1768,
                        "source": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.cmr.xml",
                        "type": "metadata"
                    },
                    {
                        "bucket": "uds-sbx-cumulus-staging",
                        "checksum": "unknown",
                        "checksumType": "md5",
                        "fileName": "test_file01.nc.stac.json",
                        "key": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.stac.json",
                        "size": -1,
                        "source": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.stac.json",
                        "type": "metadata__stac"
                    },
                    {
                        "bucket": "uds-sbx-cumulus-staging",
                        "checksum": "unknown",
                        "checksumType": "md5",
                        "fileName": "test_file01.nc.cas",
                        "key": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.cas",
                        "size": -1,
                        "source": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.cas",
                        "type": "metadata__cas"
                    },
                    {
                        "bucket": "uds-sbx-cumulus-staging",
                        "checksum": "unknown",
                        "checksumType": "md5",
                        "fileName": "test_file01.nc",
                        "key": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc",
                        "size": -1,
                        "source": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc",
                        "type": "data"
                    }
                ],
                "beginningDateTime": "2016-01-31T18:00:00.009Z",
                "endingDateTime": "2016-01-31T19:59:59.991Z",
                "lastUpdateDateTime": "2018-04-25T21:45:45.524Z",
                "productionDateTime": "1970-01-01T00:00:00.000Z",
                "queryFields": {
                    "cnm": {
                        "product": {
                            "name": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01",
                            "files": [
                                {
                                    "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc",
                                    "name": "test_file01.nc",
                                    "size": -1,
                                    "type": "data",
                                    "checksum": "unknown",
                                    "checksumType": "md5"
                                },
                                {
                                    "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.cas",
                                    "name": "test_file01.nc.cas",
                                    "size": -1,
                                    "type": "metadata__cas",
                                    "checksum": "unknown",
                                    "checksumType": "md5"
                                },
                                {
                                    "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.nc.stac.json",
                                    "name": "test_file01.nc.stac.json",
                                    "size": -1,
                                    "type": "metadata__stac",
                                    "checksum": "unknown",
                                    "checksumType": "md5"
                                },
                                {
                                    "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.cmr.xml",
                                    "name": "test_file01.cmr.xml",
                                    "size": 1768,
                                    "type": "metadata",
                                    "checksum": "9817be382b87c48ebe482b9c47d1525a",
                                    "checksumType": "md5"
                                }
                            ],
                            "dataVersion": "2311091417"
                        },
                        "version": "1.6.0",
                        "provider": "unity",
                        "response": {
                            "status": "SUCCESS"
                        },
                        "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION",
                        "identifier": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01",
                        "receivedTime": "2023-11-09T22:22:23.399Z",
                        "submissionTime": "2023-11-09T22:21:21.989722",
                        "processCompleteTime": "2023-11-09T22:22:41.220Z"
                    }
                }
            }
        }
        sns_msg = {
            "Type": "Notification",
            "MessageId": "f6441383-4a99-5f27-8a66-4e44177ea7f4",
            "TopicArn": "arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-report-granules-topic",
            "Message": json.dumps(cumulus_msg),
            "Timestamp": "2023-11-09T22:22:31.148Z",
            "SignatureVersion": "1",
            "Signature": "Skm4aumaUGxZA76/Jdya+6a42805KvAn6PrZIwXdKHE+ng37e+aN75SuCTDrv5hzeRFxA8YSoEYMG+00CvnoVN3gtsVt/o78Nkj5lr2oMCwNj2k5kwyEve4BetRelyXF1BTc7ptD7MYsSVGrIWZQwqNqUviDfBdI1nxujDiZvWnjAPWjJA8+cjx2acFAbaTzIhN90V3Fn0yOtveVXblAUZQ3EwF8Cv0CsTJFVPYliguw72s2r+9xPbc5Yj8dBL4B38HI7JC+u6qL8vgzIh+/wVlpqOef5P23qFeYDE533318EUEDfrkRs//LCbe+lcoTzka5qwOWaveMbIM9tstmeg==",
            "SigningCertURL": "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem",
            "UnsubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-report-granules-topic:c003b5ee-09a7-4129-9873-a1629868e8bd"
        }
        sample_event = {
            "Records": [
                {
                    "messageId": "6210f778-d081-4ae9-a861-8534d612dfae",
                    "receiptHandle": "AQEBk55DchogyQzpVsH1A4YEj4K/PcVuIG9Em/a6/4AHIA4G5vLPiHVElNiuMfYc1ussk2U//JwZbD788Fv8u6W22L3AJ1U8EIcGJ57aibpmd6tSCWLS5q5FA4u2X2Jq5z+lCX5NZXzNDYMqMJaCGtBkcYi4a9LDXtD+U7HWX0V8OPhFFF2a1qUu+E05c16f5OmE7wRJ3SFrRmtJOhp2DigKKsw6VJtZklTm6uILMOL1ETOTlbA02dhF16fjcXlAACirDp0Yo9pi91FrpEljOYkqAO9AX4WMbEjAPZrnaATfYmRqCTOlnrIK8xvgEPgIu/OOub7KBYh6AQn7U8QBNoASkXkn31dqyM2I+KosKy2VeJO9cjPTahhXtkW7zUFA6863Czt2oHqL6Rvwsjr+7TikfQ==",
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
                    "eventSourceARN": "arn:aws-us-gov:sqs:us-gov-west-1:440216117821:send_records_to_es",
                    "awsRegion": "us-gov-west-1"
                }
            ]
        }
        granules_indexer = GranulesIndexer(sample_event)
        granules_indexer.start()
        granules_index = GranulesDbIndex()
        sleep(3)
        result = granules_index.get_entry('UDS_LOCAL_TEST', 'DEV', mock_stac_item.id)
        print(result)
        self.assertEqual(result['bbox'], {'type': 'envelope', 'coordinates': [[0.0, 0.0], [10.0, -10.0]]}, f'wrong bbox')
        return

    def test_wkt_to_es(self):
        result = GranulesDbIndex.wkt_to_es('POINT (30 10)')
        print(result)
        self.assertEqual(result['type'], 'Point', 'wrong type')
        self.assertEqual(result['coordinates'], [30, 10], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('LINESTRING (30 10, 10 30, 40 40)')
        print(result)
        self.assertEqual(result['type'], 'LineString', 'wrong type')
        self.assertEqual(result['coordinates'], [[30, 10], [10, 30], [40, 40]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))')
        print(result)
        self.assertEqual(result['type'], 'Polygon', 'wrong type')
        self.assertEqual(result['coordinates'], [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10),(20 30, 35 35, 30 20, 20 30))')
        print(result)
        self.assertEqual(result['type'], 'Polygon', 'wrong type')
        self.assertEqual(result['coordinates'], [[[35.0, 10.0], [45.0, 45.0], [15.0, 40.0], [10.0, 20.0], [35.0, 10.0]], [[20.0, 30.0], [35.0, 35.0], [30.0, 20.0], [20.0, 30.0]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10),(20 30, 35 35, 30 20, 20 30),(20 35, 35 38, 30 25, 20 35))')
        print(result)
        self.assertEqual(result['type'], 'Polygon', 'wrong type')
        self.assertEqual(result['coordinates'], [[[35.0, 10.0], [45.0, 45.0], [15.0, 40.0], [10.0, 20.0], [35.0, 10.0]], [[20.0, 30.0], [35.0, 35.0], [30.0, 20.0], [20.0, 30.0]], [[20.0, 35.0], [35.0, 38.0], [30.0, 25.0], [20.0, 35.0]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('MULTIPOINT ((10 40), (40 30), (20 20), (30 10))')
        print(result)
        self.assertEqual(result['type'], 'MultiPoint', 'wrong type')
        self.assertEqual(result['coordinates'], [[10.0, 40.0], [40.0, 30.0], [20.0, 20.0], [30.0, 10.0]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('MULTIPOINT (10 40, 40 30, 20 20, 30 10)')
        print(result)
        self.assertEqual(result['type'], 'MultiPoint', 'wrong type')
        self.assertEqual(result['coordinates'], [[10.0, 40.0], [40.0, 30.0], [20.0, 20.0], [30.0, 10.0]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10))')
        print(result)
        self.assertEqual(result['type'], 'MultiLineString', 'wrong type')
        self.assertEqual(result['coordinates'], [[[10.0, 10.0], [20.0, 20.0], [10.0, 40.0]], [[40.0, 40.0], [30.0, 30.0], [40.0, 20.0], [30.0, 10.0]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)),((15 5, 40 10, 10 20, 5 10, 15 5)))')
        print(result)
        self.assertEqual(result['type'], 'MultiPolygon', 'wrong type')
        self.assertEqual(result['coordinates'], [[[[30.0, 20.0], [45.0, 40.0], [10.0, 40.0], [30.0, 20.0]]], [[[15.0, 5.0], [40.0, 10.0], [10.0, 20.0], [5.0, 10.0], [15.0, 5.0]]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),(30 20, 20 15, 20 25, 30 20)))')
        print(result)
        self.assertEqual(result['type'], 'MultiPolygon', 'wrong type')
        self.assertEqual(result['coordinates'], [[[[40.0, 40.0], [20.0, 45.0], [45.0, 30.0], [40.0, 40.0]]], [[[20.0, 35.0], [10.0, 30.0], [10.0, 10.0], [30.0, 5.0], [45.0, 20.0], [20.0, 35.0]], [[30.0, 20.0], [20.0, 15.0], [20.0, 25.0], [30.0, 20.0]]]], 'wrong type')
        result = GranulesDbIndex.wkt_to_es('GEOMETRYCOLLECTION (POINT (40 10),LINESTRING (10 10, 20 20, 10 40),POLYGON ((40 40, 20 45, 45 30, 40 40)))')
        print(result)
        return
