from cumulus_lambda_functions.daac_archiver.daac_archiver_logic import DaacArchiverLogic
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator


def lambda_handler_request(event, context):
    """
    :param event:
    :param context:
    :return:
    {'Records': [{'messageId': '6ff7c6fd-4053-4ab4-bc12-c042be1ed275', 'receiptHandle': 'AQEBYASiFPjQT5JBI2KKCTF/uQhHfJt/tHhgucslQQdvkNVxcXCNi2E5Ux4U9N0eu7RfvlnvtycjUh0gdL7jIeoyH+VRKSF61uAJuT4p31BsNe0GYu49N9A6+kxjP/RrykR7ZofmQRdHToX1ugRc76SMRic4H/ZZ89YAHA2QeomJFMrYywIxlk8OAzYaBf2dQI7WexjY5u1CW00XNMbTGyTo4foVPxcSn6bdFpfgxW/L7yJMX/0YQvrA9ruiuQ+lrui+6fWYh5zEk3f5v1bYtUQ6DtyyfbtMHZQJTJpUlWAFRzzN+3melilH7FySyOGDXhPb0BOSzmdKq9wBbfLW/YPb7l99ejq4GfRfj8LyI4EtB96vTeUw4LCgUqbZcBrxbGBLUXMacweh+gCjHav9ylqr2SeOiqG3vWPq9pwFYQIDqNE=', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "33e1075a-435c-5217-a33d-59fae85e19b2",\n  "TopicArn" : "arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester",\n  "Subject" : "Amazon S3 Notification",\n  "Message" : "{\\"Service\\":\\"Amazon S3\\",\\"Event\\":\\"s3:TestEvent\\",\\"Time\\":\\"2024-04-22T18:13:22.416Z\\",\\"Bucket\\":\\"uds-sbx-cumulus-staging\\",\\"RequestId\\":\\"DQ4T0GRVFPSX45C9\\",\\"HostId\\":\\"gHBFnYNmfnGDZBmqoQwA3RScjtjBk5lr426moGxu8IDpe5UhWAqNTxHqilWBoPN1njzIrzNrf8c=\\"}",\n  "Timestamp" : "2024-04-22T18:13:22.434Z",\n  "SignatureVersion" : "1",\n  "Signature" : "RvSxqpU7J7CCJXbin9cXqTxzjMjgAUFtk/n454mTMcOe5x3Ay1w4AHfzyeYQCFBdLHNBa8n3OdMDoDlJqyVQMb8k+nERaiZWN2oqFVDRqT9pqSr89b+4FwlhPv6TYy2pBa/bgjZ4cOSYsey1uSQ3hjl0idfssvuV5cCRxQScbA+yu8Gcv9K7Oqgy01mC0sDHiuPIifhFXxupG5ygbjqoHIB+1gdMEbBwyixoY5GOpHM/O2uHNF+dJDjax1WMxQ2FzVjiFeCa+tNcjovF059+tx2v1YmDq/kEAFrN6DAtP6R4zKag62P9jkvjU/wHYJ2jjXmZAqoG+nuzAo24HiZPSw==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-60eadc530605d63b8e62a523676ef735.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester:76cbefa1-addf-45c2-97e1-ae16986b195b"\n}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1713809602474', 'SenderId': 'AIDAIYLAVTDLUXBIEIX46', 'ApproximateFirstReceiveTimestamp': '1713809602483'}, 'messageAttributes': {}, 'md5OfBody': 'c6d06d1b742ad5bd2cfe5f542640aad2', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester', 'awsRegion': 'us-west-2'}]}
    """
    LambdaLoggerGenerator.remove_default_handlers()
    DaacArchiverLogic().send_to_daac(event)
    return


def lambda_handler_response(event, context):
    """
    :param event:
    :param context:
    :return:
    {'Records': [{'messageId': '6ff7c6fd-4053-4ab4-bc12-c042be1ed275', 'receiptHandle': 'AQEBYASiFPjQT5JBI2KKCTF/uQhHfJt/tHhgucslQQdvkNVxcXCNi2E5Ux4U9N0eu7RfvlnvtycjUh0gdL7jIeoyH+VRKSF61uAJuT4p31BsNe0GYu49N9A6+kxjP/RrykR7ZofmQRdHToX1ugRc76SMRic4H/ZZ89YAHA2QeomJFMrYywIxlk8OAzYaBf2dQI7WexjY5u1CW00XNMbTGyTo4foVPxcSn6bdFpfgxW/L7yJMX/0YQvrA9ruiuQ+lrui+6fWYh5zEk3f5v1bYtUQ6DtyyfbtMHZQJTJpUlWAFRzzN+3melilH7FySyOGDXhPb0BOSzmdKq9wBbfLW/YPb7l99ejq4GfRfj8LyI4EtB96vTeUw4LCgUqbZcBrxbGBLUXMacweh+gCjHav9ylqr2SeOiqG3vWPq9pwFYQIDqNE=', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "33e1075a-435c-5217-a33d-59fae85e19b2",\n  "TopicArn" : "arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester",\n  "Subject" : "Amazon S3 Notification",\n  "Message" : "{\\"Service\\":\\"Amazon S3\\",\\"Event\\":\\"s3:TestEvent\\",\\"Time\\":\\"2024-04-22T18:13:22.416Z\\",\\"Bucket\\":\\"uds-sbx-cumulus-staging\\",\\"RequestId\\":\\"DQ4T0GRVFPSX45C9\\",\\"HostId\\":\\"gHBFnYNmfnGDZBmqoQwA3RScjtjBk5lr426moGxu8IDpe5UhWAqNTxHqilWBoPN1njzIrzNrf8c=\\"}",\n  "Timestamp" : "2024-04-22T18:13:22.434Z",\n  "SignatureVersion" : "1",\n  "Signature" : "RvSxqpU7J7CCJXbin9cXqTxzjMjgAUFtk/n454mTMcOe5x3Ay1w4AHfzyeYQCFBdLHNBa8n3OdMDoDlJqyVQMb8k+nERaiZWN2oqFVDRqT9pqSr89b+4FwlhPv6TYy2pBa/bgjZ4cOSYsey1uSQ3hjl0idfssvuV5cCRxQScbA+yu8Gcv9K7Oqgy01mC0sDHiuPIifhFXxupG5ygbjqoHIB+1gdMEbBwyixoY5GOpHM/O2uHNF+dJDjax1WMxQ2FzVjiFeCa+tNcjovF059+tx2v1YmDq/kEAFrN6DAtP6R4zKag62P9jkvjU/wHYJ2jjXmZAqoG+nuzAo24HiZPSw==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-60eadc530605d63b8e62a523676ef735.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester:76cbefa1-addf-45c2-97e1-ae16986b195b"\n}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1713809602474', 'SenderId': 'AIDAIYLAVTDLUXBIEIX46', 'ApproximateFirstReceiveTimestamp': '1713809602483'}, 'messageAttributes': {}, 'md5OfBody': 'c6d06d1b742ad5bd2cfe5f542640aad2', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-west-2:237868187491:uds-sbx-cumulus-granules_cnm_ingester', 'awsRegion': 'us-west-2'}]}
    """
    LambdaLoggerGenerator.remove_default_handlers()
    DaacArchiverLogic().receive_from_daac(event)
    return
