import json
import os
import random

import requests
from cumulus_lambda_functions.lib.json_validator import JsonValidator

from cumulus_lambda_functions.lib.aws.aws_message_transformers import AwsMessageTransformers
from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from cumulus_lambda_functions.lib.time_utils import TimeUtils

from cumulus_lambda_functions.lib.aws.aws_sns import AwsSns
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DelegateS3Access",
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com",
                "AWS": "arn:aws:iam::429178552491:role/uds-sbx-cumulus-mock_daac_lambda_role"
            },
            "Action": [
                "s3:ListBucket",
                "s3:GetObject*",
                "s3:PutObject*"
            ],
            "Resource": [
                "arn:aws:s3:::uds-sbx-cumulus-staging/*",
                "arn:aws:s3:::uds-sbx-cumulus-staging"
            ]
        }
    ]
}

class MockDaacLogic:
    NO_RESPONSE_PERC = 'NO_RESPONSE_PERC'
    NO_RESPONSE_PERC_DEFAULT = .25
    FAIL_PERC = 'FAIL_PERC'
    FAIL_PERC_DEFAULT = .25
    UDS_ARCHIVE_SNS_TOPIC_ARN = 'UDS_ARCHIVE_SNS_TOPIC_ARN'

    def __init__(self):
        self.__no_response_percentage = float(os.environ.get(self.NO_RESPONSE_PERC, self.NO_RESPONSE_PERC_DEFAULT))
        self.__fail_percentage = float(os.environ.get(self.NO_RESPONSE_PERC, self.NO_RESPONSE_PERC_DEFAULT))
        self.__fail_percentage += self.__no_response_percentage
        self.__sns_topic_arn = os.environ.get(self.UDS_ARCHIVE_SNS_TOPIC_ARN)
        self.__sns = AwsSns().set_topic_arn(self.__sns_topic_arn)
        self.__response_message = {}
        self.__s3 = AwsS3()

    def __send_random_result(self, errored_list: list):
        if len(errored_list) > 0:
            LOGGER.debug(f'sending real failure message: {json.dumps(errored_list)}')
            self.__response_message['response'] = {
                'status': 'FAILURE',
                'errorCode': "VALIDATION_ERROR",
                'errorMessage': json.dumps(errored_list),
            }
            sns_response = self.__sns.publish_message(json.dumps(self.__response_message))
            LOGGER.debug(f'sns_response: {sns_response}')
            return

        # https://github.com/podaac/cloud-notification-message-schema?tab=readme-ov-file#response-message-fields
        random_success = random.uniform(0, 1)
        if random_success < self.__no_response_percentage:
            LOGGER.debug(f'intentionally not sending any message')
            return
        if random_success < self.__fail_percentage:
            LOGGER.debug(f'sending failure message')
            self.__response_message['response'] = {
                'status': 'FAILURE',
                'errorCode': ["VALIDATION_ERROR", "PROCESSING_ERROR", "TRANSFER_ERROR"][random.randint(0, 2)],
                'errorMessage': 'This is a sample failure message',
            }
            sns_response = self.__sns.publish_message(json.dumps(self.__response_message))
            LOGGER.debug(f'sns_response: {sns_response}')
            return
        self.__response_message['response'] = {
            'status': 'SUCCESS',
        }
        LOGGER.debug(f'sending success message')
        sns_response = self.__sns.publish_message(json.dumps(self.__response_message))
        LOGGER.debug(f'sns_response: {sns_response}')
        return

    def __check_s3_file(self, input_files: list):
        # {
        # "type": "data",
        # "name": "abcd.1234.efgh.test_file05.data.stac.json",
        # "uri": "https://uds-distribution-placeholder/uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2407291400/URN:NASA:UNITY:UDS_LOCAL_ARCHIVE_TEST:DEV:UDS_UNIT_COLLECTION___2407291400:abcd.1234.efgh.test_file05/abcd.1234.efgh.test_file05.data.stac.json",
        # "checksumType": "md5", "checksum": "unknown", "size": -1}
        errored_list = []
        for each_file in input_files:
            try:
                each_uri = each_file['uri']
                if each_uri.startswith('https'):
                    each_uri = each_uri.replace('https://', 's3://')
                    self.__s3.set_s3_url(each_uri)
                    self.__s3.set_s3_url(f's3://{self.__s3.target_key}')
                    LOGGER.debug(f'S3 URL with https: {self.__s3.target_key}')
                else:
                    self.__s3.set_s3_url(each_uri)
                    LOGGER.debug(f'S3 URL without https: {self.__s3.target_key}')
                LOGGER.debug(f'working on s3://{self.__s3.target_bucket}/{self.__s3.target_key}')
                s3_obj_size = self.__s3.get_s3_obj_size()
                if s3_obj_size != each_file['size']:
                    errored_list.append({
                        'uri': each_file['uri'],
                        'error': f'mismatched size: {s3_obj_size} v. {each_file["size"]}',
                    })
                # TODO validate md5?
            except Exception as e:
                errored_list.append({
                    'uri': each_file['uri'],
                    'error': f'unknown error: {str(e)}',
                })
        return errored_list


    def start(self, event):
        LOGGER.debug(f'event: {event}')
        """
        event: {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns:35fc364f-2c1a-4139-af3f-bbc2921ea50b', 'Sns': {'Type': 'Notification', 'MessageId': '2f324e04-4d7b-5f56-a46e-1110e4ac1f51', 'TopicArn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns', 'Subject': None, 'Message': 'asfdsadfsa', 'Timestamp': '2024-07-19T17:51:19.598Z', 'SignatureVersion': '1', 'Signature': 'Bh1CYWOwQrPcF7C7pOZ3h8khg9W2P01C8XhnIFQ0GE1H7vkXHm/vjLRFJbL0e2/6I0M2rlMJwSC/doS87PNCZ9NW+QPhyr/LmfSib1rfqbGMSIVBA3V1VbXokwvYqTwE05S8+UltEhezgexqDqxd/37WPB9iFOK0v3S5XTvNDRelQJUcTUpy8Ts/F2xFB0vgjKvdTQg+c3KDNIUzukcvNexDVfrp8QMEv/7/kO8A5JVYu0HagiBcIdVWPhgFjtTdcs0A3qSYx5C+sqoSX2Cb+opUZESQ9iNax5vZ1nZxokicSFqOts8uoSNDBE9x695BBET9IRD140bE3iF7xT5ZOQ==', 'SigningCertUrl': 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-60eadc530605d63b8e62a523676ef735.pem', 'UnsubscribeUrl': 'https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns:35fc364f-2c1a-4139-af3f-bbc2921ea50b', 'MessageAttributes': {}}}]}
        """
        input_event = AwsMessageTransformers().get_message_from_sns_event(event)
        LOGGER.debug(f'input_event: {input_event}')
        # TODO:  https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fuds-sbx-cumulus-mock_daac_lambda/log-events/2024$252F07$252F24$252F$255B$2524LATEST$255D3201091732ed43f99d4a61ea1b4eda59
        """
        [ERROR] ValueError: input json has SNS validation errors: data.Subject must be string
Traceback (most recent call last):
  File "/var/task/cumulus_lambda_functions/mock_daac/lambda_function.py", line 13, in lambda_handler
    MockDaacLogic().start(event)
  File "/var/task/cumulus_lambda_functions/mock_daac/mock_daac_logic.py", line 71, in start
    input_event = AwsMessageTransformers().get_message_from_sns_event(event)
  File "/var/task/cumulus_lambda_functions/lib/aws/aws_message_transformers.py", line 114, in get_message_from_sns_event
    raise ValueError(f'input json has SNS validation errors: {result}')
    
    
    2024-07-24 15:18:53,682 [DEBUG] [cumulus_lambda_functions.mock_daac.mock_daac_logic::67] event: 
{'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns:35fc364f-2c1a-4139-af3f-bbc2921ea50b', 'Sns': {'Type': 'Notification', 'MessageId': '15d4b41f-d5e1-572a-a292-eb04c8ae9aa5', 'TopicArn': 'arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns', 'Subject': None, 'Message': '{"collection": "DAAC:MOCK:UDS_UNIT_COLLECTION", "identifier": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_UNIT_COLLECTION___2407241000:abcd.1234.efgh.test_file05", "submissionTime": "2024-07-24T15:17:35.260565Z", "provider": "UDS_LOCAL_TEST", "version": "1.6.0", "product": {"name": "UDS_UNIT_COLLECTION___2407241000", "dataVersion": "9098", "files": []}}', 'Timestamp': '2024-07-24T15:17:35.824Z', 'SignatureVersion': '1', 'Signature': 'feJWQQtDZGrNPheO1XtZUTYscNfv0JvwfygB1Acuqsnj5mflOar8o7Y5rduGMe5eKtKrh6p9cRfOl621LBEToKcuBr6KhhXsJ2fdPQ15F2EcHKZXR5LczmYrM29xnSEXF1jZ0DYP5c4+rVvQX2re3/r1iULy9TyYxxROUPB4TcpnJS0Jy2idoaIa12dubrVPRuDsig9Otbf4b/br/QFS/TqL0Ig3HW84aYwuCBsV7sqy/e1z9yT+47z/gs8bNoalFvjaiWamZVhW50twjf5yd9wMTu4443fisfcTaYiTjpYukKr+dCM+DInaifmytccuFKiHFnZhwHFsPbFG1NMPNg==', 'SigningCertUrl': 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-60eadc530605d63b8e62a523676ef735.pem', 'UnsubscribeUrl': 'https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:429178552491:uds-sbx-cumulus-mock_daac_cnm_sns:35fc364f-2c1a-4139-af3f-bbc2921ea50b', 'MessageAttributes': {}}}]}
    
        """
        # Check input message is validated according to https://github.com/podaac/cloud-notification-message-schema?tab=readme-ov-file#notification-message-fields

        # validate using this: https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.6.1/cumulus_sns_schema.json
        cnm_msg_schema = requests.get('https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.6.1/cumulus_sns_schema.json')
        cnm_msg_schema.raise_for_status()
        cnm_msg_schema = json.loads(cnm_msg_schema.text)
        result = JsonValidator(cnm_msg_schema).validate(input_event)
        if result is not None:
            raise ValueError(f'input cnm event has cnm_msg_schema validation errors: {result}')

        # Check if S3 can be downloaded
        errored_list = self.__check_s3_file(input_event['product']['files'])
        # .25/.25/.50 P() on No send, send failure, send success
        # Return with this message: https://github.com/podaac/cloud-notification-message-schema?tab=readme-ov-file#response-message-fields
        self.__response_message = {
            'version': input_event['version'],
            'submissionTime': f'{TimeUtils.get_current_time()}Z',
            'receivedTime': input_event['submissionTime'],
            'processCompleteTime': f'{TimeUtils.get_current_time()}Z',
            'collection': input_event['collection'],
            'identifier': input_event['identifier'],
        }
        self.__send_random_result(errored_list)
        return
