import logging
from typing import Union

from botocore.exceptions import ClientError

from cumulus_lambda_functions.lib.aws.aws_cred import AwsCred

LOGGER = logging.getLogger()


class AwsParamStore(AwsCred):
    def __init__(self):
        super().__init__()
        self.__ssm_client = self.get_client('ssm')
        self.__ssm = None

    def set_param(self, key: str, val: str, encrypted: bool = True):
        self.__ssm_client.put_parameter(Name=key, Value=val,
                                        Type='SecureString' if encrypted else 'String',
                                        Overwrite=True)

    def get_param(self, param_name: str) -> Union[str, None]:
        """
        Ref: https://stackoverflow.com/questions/46063138/how-can-i-import-the-boto3-ssm-parameternotfound-exception
            on how to catch ParameterNotFound exception

        :param param_name: named of parameter in Parameter store
        :return: plain value of the parameter or None if some exception.
        """
        try:
            param_response = self.__ssm_client.get_parameter(Name=param_name, WithDecryption=True)
            if 'ResponseMetadata' not in param_response or \
                    'HTTPStatusCode' not in param_response['ResponseMetadata'] or \
                    param_response['ResponseMetadata']['HTTPStatusCode'] != 200 or \
                    'Parameter' not in param_response or \
                    'Value' not in param_response['Parameter']:
                return None
        except ClientError:
            LOGGER.exception('cannot get parameter store value for %s', param_name)
            return None
        return param_response['Parameter']['Value']
