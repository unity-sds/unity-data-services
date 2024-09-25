import json
import os
from typing import Union

from mdps_ds_lib.lib.aws.aws_lambda import AwsLambda
from starlette.datastructures import URL

from mdps_ds_lib.lib.aws.aws_sns import AwsSns

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from pydantic import BaseModel
from mdps_ds_lib.lib.utils.time_utils import TimeUtils

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class SingleFeatureRequestBody(BaseModel):
    id: str
    collection: str
    assets: dict


class CnmRequestBody(BaseModel):
    provider_id: str
    features: list[SingleFeatureRequestBody]


class CollectionsDapaCnm:
    def __init__(self, request_body):
        required_env = ['SNS_TOPIC_ARN', 'COLLECTION_CREATION_LAMBDA_NAME']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
        self.__request_body = request_body
        self.__collection_cnm_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME', '').strip()


    def start_facade(self, current_url: URL):
        LOGGER.debug(f'request body: {self.__request_body}')

        actual_path = current_url.path
        actual_path = actual_path if actual_path.endswith('/') else f'{actual_path}/'
        actual_path = f'{actual_path}actual'
        LOGGER.info(f'sanity_check')

        actual_event = {
            'resource': actual_path,
            'path': actual_path,
            'httpMethod': 'PUT',
            'headers': {
                'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Authorization': 'Bearer xxx',
                'Host': current_url.hostname, 'User-Agent': 'python-requests/2.28.2',
                'X-Amzn-Trace-Id': 'Root=1-64a66e90-6fa8b7a64449014639d4f5b4', 'X-Forwarded-For': '44.236.15.58',
                'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'},
            'multiValueHeaders': {
                'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate'], 'Authorization': ['Bearer xxx'],
                'Host': [current_url.hostname], 'User-Agent': ['python-requests/2.28.2'],
                'X-Amzn-Trace-Id': ['Root=1-64a66e90-6fa8b7a64449014639d4f5b4'],
                'X-Forwarded-For': ['127.0.0.1'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']
            },
            'queryStringParameters': {},
            'multiValueQueryStringParameters': {},
            'pathParameters': {},
            'stageVariables': None,
            'requestContext': {
                'resourceId': '',
                'authorizer': {'principalId': '', 'integrationLatency': 0},
                'resourcePath': actual_path, 'httpMethod': 'PUT',
                'extendedRequestId': '', 'requestTime': '',
                'path': actual_path, 'accountId': '',
                'protocol': 'HTTP/1.1', 'stage': '', 'domainPrefix': '', 'requestTimeEpoch': 0,
                'requestId': '',
                'identity': {
                    'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None,
                    'sourceIp': '127.0.0.1', 'principalOrgId': None, 'accessKey': None,
                    'cognitoAuthenticationType': None,
                    'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'python-requests/2.28.2',
                    'user': None
                },
                'domainName': current_url.hostname, 'apiId': ''
            },
            'body': json.dumps(self.__request_body),
            'isBase64Encoded': False
        }
        LOGGER.info(f'actual_event: {actual_event}')
        response = AwsLambda().invoke_function(
            function_name=self.__collection_cnm_lambda_name,
            payload=actual_event,
        )
        LOGGER.debug(f'async function started: {response}')
        return {
            'statusCode': 202,
            'body': {
                'message': 'processing'
            }
        }

    def __generate_cumulus_asset(self, v):
        cumulus_asset = {
                            'name': os.path.basename(v['href']),
                            'type': v['roles'][0] if 'roles' in v and len(v['roles']) > 0 else 'unknown',
                            'uri': v['href'],
                            'checksumType': 'md5',  # TODO Is this the only type?
                            'checksum': v['file:checksum'] if 'file:checksum' in v else 'unknown',
                            'size': v['file:size'] if 'file:size' in v else -1,
                        }
        return cumulus_asset

    def start(self):
        """
        Publish granule messages to CNM SNS Topic.
        This is the workflow: cnm (Rest endpoint) -> sns -> sqs -> event bridge rule (every 1 minute) -> uds-dev-cumulus-sqsMessageConsumer lambda -> sqs -> uds-dev-cumulus-sqs2sf lambda -> step function
Sample Output:
{
    "collection": "SNDR_SNPP_ATMS_L1A",
    "identifier": "SNDR.SNPP.ATMS.L1A.nominal2.01",
    "product": {
      "dataVersion": "1",
      "files": [
        {
          "name": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
          "size": 9194361,
          "type": "data",
          "uri": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
          "checksumType": "md5",
          "checksum": "2eafd390e5e7ac4b4d7d86d361fed50b"
        },
        {
          "name": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
          "size": 2673,
          "type": "metadata",
          "uri": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
          "checksumType": "md5",
          "checksum": "60e834d887ac6fb81ef63c4056c5b673"
        }
      ],
      "name": "SNDR.SNPP.ATMS.L1A.nominal2.01"
    },
    "provider": "SNPP",
    "submissionTime": "2022-07-06T00:00:00Z",
    "version": "1.6.0"
  }


Input to trigger CNM
Message:
{
 "collection": "SNDR_SNPP_ATMS_L1A",
 "identifier": "SNDR.SNPP.ATMS.L1A.nominal2.01",
 "product": {
  "dataVersion": "1",
  "files": [
   {
    "name": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
    "size": 9194361,
    "type": "data",
    "uri": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
    "checksumType": "md5",
    "checksum": "2eafd390e5e7ac4b4d7d86d361fed50b"
   },
   {
    "name": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
    "size": 2673,
    "type": "metadata",
    "uri": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
    "checksumType": "md5",
    "checksum": "60e834d887ac6fb81ef63c4056c5b673"
   }
  ],
  "name": "SNDR.SNPP.ATMS.L1A.nominal2.01"
 },
 "provider": "SNPP",
 "submissionTime": "2022-07-06T00:00:00Z",
 "version": "1.6.0"
}
aws sns publish --topic-arn arn:aws:sns:us-west-2:884500545225:am-uds-dev-cumulus-cnm-submission-sns --message file:///tmp/SNDR.SNPP.ATMS.L1A.nominal2.01.json



Test Input message
{
    "requestContext": {
        "provider_id": "SNPP",
        "features": [
            {
                "id": "SNDR.SNPP.ATMS.L1A.nominal2.01",
                "collection": "SNDR_SNPP_ATMS_L1A___1",
                "assets": {
                    "data": {
                        "href": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc"
                    },
                    "metadata": {
                        "href": "s3://am-uds-dev-cumulus-staging/SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas"
                    }
                }
            }
        ]
    }
}
        :return:
        """
        error_list = []
        for each_granule in self.__request_body['features']:
            LOGGER.debug(f'executing: {each_granule}')
            try:
                collection_id_version = each_granule['collection'].split('___')
                sns_msg = {
                    'collection': collection_id_version[0],
                    'identifier': each_granule['id'],
                    'submissionTime': TimeUtils.get_current_time(),
                    "provider": self.__request_body['provider_id'],
                    "version": '1.6.0',  # TODO
                    'product': {
                        'name': each_granule['id'],
                        'dataVersion': collection_id_version[1],
                        'files': [self.__generate_cumulus_asset(v) for k, v in each_granule['assets'].items()],
                    }
                }
                LOGGER.debug(f'sending sns message: {sns_msg}')
                sns_response = AwsSns().set_topic_arn(self.__sns_topic_arn).publish_message(json.dumps(sns_msg))
                LOGGER.debug(f'published message result: {sns_response}')
            except Exception as e:
                LOGGER.exception(f'error while sending SNS msg for granule: {each_granule}')
                error_list.append({'message': str(e), 'feature': each_granule})
        if len(error_list) < 1:
            return {
                'statusCode': 200,
                'body': 'registered'
            }
        return {
            'statusCode': 500,
            'body': {'message': f'failed {len(error_list)}/{len(self.__request_body["features"])}',
                                'details': error_list}
        }
