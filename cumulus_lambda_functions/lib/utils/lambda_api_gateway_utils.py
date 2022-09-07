from copy import deepcopy

from cumulus_lambda_functions.lib.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

API_GATEWAY_EVENT_SCHEMA = {
    'type': 'object',
    'required': [
        'requestContext',
        'headers',
    ],
    'properties': {
        'requestContext': {
            'type': 'object',
            'required': [
                'path',
            ],
            'properties': {
                'path': {
                    'type': 'string'
                }
            }
        },
        'headers': {
            'type': 'object',
            'required': [
                'Host',
            ],
            'properties': {
                'Host': {
                    'type': 'string'
                }
            }
        }
    }
}
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class LambdaApiGatewayUtils:
    def __init__(self, event: dict, default_limit: int = 10):
        self.__event = event
        self.__default_limit = default_limit
        api_gateway_event_validator_result = JsonValidator(API_GATEWAY_EVENT_SCHEMA).validate(event)
        if api_gateway_event_validator_result is not None:
            raise ValueError(f'invalid event: {api_gateway_event_validator_result}. event: {event}')

    def __get_current_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting current page URL')
            return f'unable to get current page URL, {str(e)}'
        return requesting_url

    def __get_next_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            if limit == 0:
                return ''
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            offset += limit
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting next page URL')
            return f'unable to get next page URL, {str(e)}'
        return requesting_url

    def __get_prev_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            if limit == 0:
                return ''
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            offset -= limit
            if offset < 0:
                offset = 0
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting previous page URL')
            return f'unable to get previous page URL, {str(e)}'
        return requesting_url

    def generate_pagination_links(self):
        return [
            {'rel': 'self', 'href': self.__get_current_page()},
            {'rel': 'root', 'href': f"https://{self.__event['headers']['Host']}"},
            {'rel': 'next', 'href': self.__get_next_page()},
            {'rel': 'prev', 'href': self.__get_prev_page()},
        ]
