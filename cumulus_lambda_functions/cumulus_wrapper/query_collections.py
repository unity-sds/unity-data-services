import json
import re

import requests
from mdps_ds_lib.lib.cumulus_stac.collection_transformer import CollectionTransformer

from cumulus_lambda_functions.cumulus_wrapper.cumulus_base import CumulusBase
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CollectionsQuery(CumulusBase):
    __collections_key = 'collections'
    __providers_key = 'providers'
    __rules_key = 'rules'
    __stats_key = 'stats'
    __collection_id_key = 'collectionId'
    __collection_name = 'name'
    __collection_version = 'version'

    def __init__(self, cumulus_base: str, cumulus_token: str):
        super().__init__(cumulus_base, cumulus_token)

    def with_collection_id(self, collection_id: str):
        # self._conditions.append(f'{self.__collection_id_key}={collection_id}')
        split_collection = collection_id.split('___')
        self._conditions.append(f'{self.__collection_name}={split_collection[0]}')
        self._conditions.append(f'{self.__collection_version}={split_collection[1]}')

        return self

    def with_collections(self, collection_ids: list):
        collection_names = [k.split('___')[0] for k in collection_ids]
        self._conditions.append(f'{self.__collection_name}__in={",".join(collection_names)}')
        return self

    def get_size(self, private_api_prefix: str):
        query_params = {'field': 'status', 'type': 'collections'}
        main_conditions = {k[0]: k[1] for k in [k1.split('=') for k1 in self._conditions]}
        if self.__collection_name in main_conditions:
            query_params[self.__collection_name] = main_conditions[self.__collection_name]
        if self.__collection_version in main_conditions:
            query_params[self.__collection_version] = main_conditions[self.__collection_version]
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/stats/aggregate',
            'queryStringParameters': query_params,
            'headers': {
                'Content-Type': 'application/json',
            },
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
        {'statusCode': 200, 'body': '{"meta":{"name":"cumulus-api","stack":"am-uds-dev-cumulus","table":"granule","limit":3,"page":1,"count":0},"results":[]}', 'headers': {'x-powered-by': 'Express', 'access-control-allow-origin': '*', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'application/json; charset=utf-8', 'content-length': '120', 'etag': 'W/"78-YdHqDNIH4LuOJMR39jGNA/23yOQ"', 'date': 'Tue, 07 Jun 2022 22:30:44 GMT', 'connection': 'close'}, 'isBase64Encoded': False}
            """
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        if query_result['statusCode'] >= 500:
            raise ValueError(f'server_error: {query_result.statusCode}. details: {query_result}')
        if query_result['statusCode'] >= 400:
            raise ValueError(f'client_error: {query_result.statusCode}. details: {query_result}')
        query_result = json.loads(query_result['body'])
        LOGGER.info(f'json query_result: {query_result}')
        if 'meta' not in query_result or 'count' not in query_result['meta']:
            raise ValueError(f'server_error: missing key: results. invalid response json: {query_result}')
        total_size = query_result['meta']['count']
        return {'total_size': total_size}

    def create_collection(self, new_collection: dict, private_api_prefix: str):
        payload = {
            'httpMethod': 'POST',
            'resource': '/{proxy+}',
            'path': f'/{self.__collections_key}',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(new_collection)
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}

    def delete_collection(self, private_api_prefix, collection_id, collection_version):
        payload = {
            'httpMethod': 'DELETE',
            'resource': '/{proxy+}',
            'path': f'/{self.__collections_key}/{collection_id}/{collection_version}',
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}

    def query_rules(self, private_api_prefix: str):
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/{self.__rules_key}',
            # 'queryStringParameters': {k[0]: k[1] for k in [k1.split('=') for k1 in self._conditions]},
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
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
            LOGGER.debug(f'json query_result: {query_result}')
            if 'results' not in query_result:
                LOGGER.error(f'missing key: results. invalid response json: {query_result}')
                return {'server_error': f'missing key: results. invalid response json: {query_result}'}
            query_result = query_result['results']
        except Exception as e:
            LOGGER.exception('error  while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'results': query_result}

    def delete_sqs_rules(self, new_collection: dict, private_api_prefix: str):
        # $ curl --request DELETE https://example.com/rules/repeat_test --header 'Authorization: Bearer ReplaceWithTheToken'
        underscore_collection_name = re.sub(r'[^a-zA-Z0-9_]', '___', new_collection["name"])  # replace any character that's not alphanumeric or underscore with 3 underscores
        rule_name = f'{underscore_collection_name}___{new_collection["version"]}___rules_sqs'
        payload = {
            'httpMethod': 'DELETE',
            'resource': '/{proxy+}',
            'path': f'/{self.__rules_key}/{rule_name}',
            'headers': {
                'Content-Type': 'application/json',
            },
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}

    def delete_executions(self, new_collection: dict, private_api_prefix: str):
        # $ curl --request DELETE https://example.com/rules/repeat_test --header 'Authorization: Bearer ReplaceWithTheToken'
        request_body = {
            "collectionId": new_collection["name"],
            "esBatchSize": 100000,
            "dbBatchSize": 50000
        }
        payload = {
            'httpMethod': 'POST',
            'resource': '/{proxy+}',
            'path': f'/executions/bulk-delete-by-collection',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(request_body)
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}

    def create_sqs_rules(self, new_collection: dict, private_api_prefix: str, sqs_url: str, provider_name: str = '', workflow_name: str = 'CatalogGranule', visibility_timeout: int = 1800):
        """
curl --request POST "$CUMULUS_BASEURL/rules" --header "Authorization: Bearer $cumulus_token"  --header 'Content-Type: application/json' --data '{
    "workflow": "DiscoverGranules",
    "collection": {
        "name": "ATMS_SCIENCE_Group",
        "version": "001"
    },
    "provider": "snpp_provider_03",
    "name": "ATMS_SCIENCE_Group_2016_002_v1",
    "rule": {
        "type": "onetime"
    },
    "meta": { "provider_path": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/002/", "publish": false, "distribution_endpoint": "s3://am-uds-dev-cumulus-internal/" },
    "state": "ENABLED"
}'
        :return:
        """
        underscore_collection_name = re.sub(r'[^a-zA-Z0-9_]', '___', new_collection["name"])  # replace any character that's not alphanumeric or underscore with 3 underscores
        LOGGER.debug(f'underscore_collection_name: {underscore_collection_name}')
        rule_body = {
            'workflow': workflow_name,
            'collection': {
                'name': new_collection['name'],
                'version': new_collection['version'],
            },
            # 'provider': provider_name,
            'name': f'{underscore_collection_name}___{new_collection["version"]}___rules_sqs',
            'rule': {
                # 'type': 'onetime',
                'type': 'sqs',
                'value': sqs_url,
            },
            'state': 'ENABLED',
            "meta": {
                'retries': 1,
                'visibilityTimeout': visibility_timeout,
                # "provider_path": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/002/",
                # "publish": False,
                # "distribution_endpoint": "s3://am-uds-dev-cumulus-internal/"
            },

        }
        if provider_name is not None and provider_name != '':
            rule_body['provider'] = provider_name
        LOGGER.info(f'rule_body: {rule_body}')
        payload = {
            'httpMethod': 'POST',
            'resource': '/{proxy+}',
            'path': f'/{self.__rules_key}',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(rule_body)
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}

    def __get_stats(self, collection_id, private_api_prefix: str):
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/{self.__collections_key}',
            'queryStringParameters': {k[0]: k[1] for k in [k1.split('=') for k1 in self._conditions]},
        }
        try:
            query_stats_result = self._invoke_api(payload, private_api_prefix)
        except:
            LOGGER.exception(f'error while trying to retrieve stats for collection: {collection_id}')
            return {}
        if query_stats_result['statusCode'] >= 400:
            return {}
        return query_stats_result['results']

    def get_stats(self, collection_id:str, private_api_prefix: str):
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/stats',
            'queryStringParameters': {'type': 'granules', 'collectionId': collection_id},
            'headers': {
                'Content-Type': 'application/json',
            },
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
        {'statusCode': 200, 'body': '{"meta":{"name":"cumulus-api","stack":"am-uds-dev-cumulus","table":"granule","limit":3,"page":1,"count":0},"results":[]}', 'headers': {'x-powered-by': 'Express', 'access-control-allow-origin': '*', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'application/json; charset=utf-8', 'content-length': '120', 'etag': 'W/"78-YdHqDNIH4LuOJMR39jGNA/23yOQ"', 'date': 'Tue, 07 Jun 2022 22:30:44 GMT', 'connection': 'close'}, 'isBase64Encoded': False}
            """
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        if query_result['statusCode'] >= 500:
            raise ValueError(f'server_error: {query_result.statusCode}. details: {query_result}')
        if query_result['statusCode'] >= 400:
            raise ValueError(f'client_error: {query_result.statusCode}. details: {query_result}')
        query_result = json.loads(query_result['body'])
        LOGGER.info(f'json query_result: {query_result}')
        if 'granules' not in query_result:
            raise ValueError(f'server_error: missing key: results. invalid response json: {query_result}')
        stats = query_result['granules']
        return stats

    def query_direct_to_private_api(self, private_api_prefix: str, output_base_url: str):
        payload = {
            'httpMethod': 'GET',
            'resource': '/{proxy+}',
            'path': f'/{self.__collections_key}',
            'queryStringParameters': {k[0]: k[1] for k in [k1.split('=') for k1 in self._conditions]},
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
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
            LOGGER.debug(f'json query_result: {query_result}')
            if 'results' not in query_result:
                LOGGER.error(f'missing key: results. invalid response json: {query_result}')
                return {'server_error': f'missing key: results. invalid response json: {query_result}'}
            query_result = query_result['results']
            for each_collection in query_result:
                stac_collection_id = f"{each_collection['name']}___{each_collection['version']}"
                stats = self.get_stats(stac_collection_id, private_api_prefix)
                each_collection['dateFrom'] = stats['dateFrom']
                each_collection['dateTo'] = stats['dateTo']
                each_collection['total_size'] = stats['value']
            stac_list = [CollectionTransformer(items_base_url=output_base_url).to_stac(k) for k in query_result]
            LOGGER.debug(f'stac_list: {stac_list}')
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'results': stac_list}

    def query(self):
        conditions_str = '&'.join(self._conditions)
        LOGGER.info(f'cumulus_base: {self.cumulus_base}')
        LOGGER.info(f'get_base_headers: {self.get_base_headers()}')
        try:
            query_result = requests.get(url=f'{self.cumulus_base}/{self.__collections_key}?{conditions_str}', headers=self.get_base_headers())
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
        return {'results': [CollectionTransformer().to_stac(k) for k in query_result]}

    def create_provider(self, provider_name: str, s3_bucket: str, private_api_prefix: str):
        #       INSERT INTO providers (name, protocol, host)       VALUES ('unity', 's3', 'https://dev.mdps.mcp.nasa.gov');
        # TODO : this fails
        payload = {
            'httpMethod': 'POST',
            'resource': '/{proxy+}',
            'path': f'/{self.__providers_key}',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                "id": provider_name,
                "host": s3_bucket,
                "protocol": "s3",
                # "port": 443,
                "globalConnectionLimit": 1000,
                # "maxDownloadTime": 300,
                # "username": "na",
                # "password": "na",
                # "privateKey": "na",
                # "cmKeyId": "na",
                # "allowedRedirects": "na",
            })
        }
        LOGGER.debug(f'payload: {payload}')
        try:
            query_result = self._invoke_api(payload, private_api_prefix)
            """
            {'statusCode': 500, 'body': '', 'headers': {}}
            """
            if query_result['statusCode'] >= 500:
                LOGGER.error(f'server error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'server_error': query_result}
            if query_result['statusCode'] >= 400:
                LOGGER.error(f'client error status code: {query_result["statusCode"]}. details: {query_result}')
                return {'client_error': query_result}
            query_result = json.loads(query_result['body'])
            LOGGER.debug(f'json query_result: {query_result}')
            if 'message' not in query_result:
                return {'server_error': f'invalid response: {query_result}'}
        except Exception as e:
            LOGGER.exception('error while invoking')
            return {'server_error': f'error while invoking:{str(e)}'}
        return {'status': query_result['message']}
