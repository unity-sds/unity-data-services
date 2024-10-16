import json

from mdps_ds_lib.lib.utils.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CnmResultWriter:
    def __init__(self):
        self.__s3 = AwsS3()
        self.__cnm_response_schema = {
            'type': 'object',
            'required': ['collection', 'product', 'submissionTime'],
            'properties': {
                'submissionTime': {'type': 'string'},
                'collection': {'type': 'string'},
                'product': {
                    'type': 'object',
                    'required': ['name', 'files'],
                    'properties': {
                        'name': {'type': 'string'},
                        'files': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'required': ['name', 'uri'],
                                'properties': {
                                    'name': {'type': 'string'},
                                    'uri': {'type': 'string'},
                                }
                            },
                        }
                    }
                }
            }
        }
        self.__cnm_response = {}
        self.__s3_url = None

    @property
    def s3_url(self):
        return self.__s3_url

    @s3_url.setter
    def s3_url(self, val):
        """
        :param val:
        :return: None
        """
        self.__s3_url = val
        return

    @property
    def cnm_response(self):
        return self.__cnm_response

    @cnm_response.setter
    def cnm_response(self, val):
        """
        :param val:
        :return: None
        """
        self.__cnm_response = val
        return

    def extract_s3_location(self):
        result = JsonValidator(self.__cnm_response_schema).validate(self.cnm_response)
        if result is not None:
            LOGGER.error(f'invalid JSON: {result}. request_body: {self.cnm_response}')
            raise ValueError(f'invalid JSON: {result}. request_body: {self.cnm_response}')
        response_filename = f'{self.cnm_response["product"]["name"]}.{self.cnm_response["submissionTime"]}.cnm.json'
        parsed_url = self.cnm_response['product']['files'][0]['uri'].split('//')[1]
        s3_url = parsed_url.split('/')
        s3_url[-1] = response_filename
        self.__s3_url = 's3://' + '/'.join(s3_url[1:])
        LOGGER.debug(f'extracted s3_url: {self.__s3_url}')
        return self

    def start(self, event):
        LOGGER.debug(f'event: {event}')
        sns_msg = AwsMessageTransformers().sqs_sns(event)
        LOGGER.debug(f'sns_msg: {sns_msg}')
        self.cnm_response = sns_msg
        self.extract_s3_location()
        self.__s3.set_s3_url(self.s3_url).upload_bytes(json.dumps(self.cnm_response, indent=4).encode())
        return
