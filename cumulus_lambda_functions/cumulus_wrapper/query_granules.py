import json

import boto3
import requests
from cumulus_lambda_functions.cumulus_stac.item_transformer import ItemTransformer

from cumulus_lambda_functions.cumulus_wrapper.cumulus_base import CumulusBase
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class GranulesQuery(CumulusBase):
    __granules_key = 'granules'
    __ending_time_key = 'endingDateTime'
    __beginning_time_key = 'beginningDateTime'

    def __init__(self, cumulus_base: str, cumulus_token: str):
        super().__init__(cumulus_base, cumulus_token)

    def with_bbox(self):
        return self

    def with_time_from(self, from_time):
        self._conditions.append(f'{self.__ending_time_key}__from={from_time}')
        return self

    def with_time_to(self, to_time):
        self._conditions.append(f'{self.__beginning_time_key}__from={to_time}')
        return self

    def with_time(self, input_time):
        self._conditions.append(f'{self.__beginning_time_key}__from={input_time}')
        self._conditions.append(f'{self.__ending_time_key}__to={input_time}')
        return self

    def with_time_range(self, from_time, to_time):
        """

        curl -k "$CUMULUS_BASEURL/granules?limit=1&beginningDateTime__from=2016-01-18T22:00:00&endingDateTime__to=2016-01-20T22:00:00" --header "Authorization: Bearer $cumulus_token"|jq
        :param beginning_dt:
        :param ending_dt:
        :return:
        """
        self._conditions.append(f'{self.__ending_time_key}__from={from_time}')
        self._conditions.append(f'{self.__beginning_time_key}__to={to_time}')
        return self

    def __invoke_api(self, payload, private_api_prefix: str):
        """Function to invoke cumulus api via aws lambda"""

        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName=f'{private_api_prefix}-PrivateApiLambda',
            Payload=json.dumps(payload),
        )
        json_response_payload = response.get('Payload').read().decode('utf-8')
        response_data = json.loads(json_response_payload)

        return response_data

    def query_direct_to_private_api(self, private_api_prefix: str):
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/{self.__granules_key}',
            'queryStringParameters': {k[0]: k[1] for k in [k1.split('=') for k1 in self._conditions]},
            # 'queryStringParameters': {'limit': '30'},
            'headers': {
                'Content-Type': 'application/json',
            },
            # 'body': json.dumps({"action": "removeFromCmr"})
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self.__invoke_api(payload, private_api_prefix)
            """
        {'statusCode': 200, 'body': '{"meta":{"name":"cumulus-api","stack":"am-uds-dev-cumulus","table":"granule","limit":3,"page":1,"count":0},"results":[]}', 'headers': {'x-powered-by': 'Express', 'access-control-allow-origin': '*', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'application/json; charset=utf-8', 'content-length': '120', 'etag': 'W/"78-YdHqDNIH4LuOJMR39jGNA/23yOQ"', 'date': 'Tue, 07 Jun 2022 22:30:44 GMT', 'connection': 'close'}, 'isBase64Encoded': False}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result.statusCode}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result.statusCode}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.info(f'json query_result: {query_result}')
            if 'results' not in query_result:
                LOGGER.error(f'missing key: results. invalid response json: {query_result}')
                return {'server_error': f'missing key: results. invalid response json: {query_result}'}
            query_result = query_result['results']
            stac_list = [ItemTransformer().to_stac(k) for k in query_result]
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'results': stac_list}

    def query(self):
        conditions_str = '&'.join(self._conditions)
        LOGGER.info(f'cumulus_base: {self.cumulus_base}')
        LOGGER.info(f'get_base_headers: {self.get_base_headers()}')
        try:
            query_result = requests.get(url=f'{self.cumulus_base}/{self.__granules_key}?{conditions_str}', headers=self.get_base_headers())
            LOGGER.info(f'query_result: {query_result}')
            if query_result.status_code >= 500:
                return {'server_error': query_result.text}
            if query_result.status_code >= 400:
                return {'client_error': query_result.text}
            query_result = json.loads(query_result.content.decode())
            LOGGER.info(f'query_result: {query_result}')
            if 'results' not in query_result:
                return {'server_error': f'missing key: results. invalid response json: {query_result}'}
            query_result = query_result['results']
        except Exception as e:
            LOGGER.exception('error during cumulus query')
            return {'server_error': str(e)}
        return {'results': [ItemTransformer().to_stac(k) for k in query_result]}
