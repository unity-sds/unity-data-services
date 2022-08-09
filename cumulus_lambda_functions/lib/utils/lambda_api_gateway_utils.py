from copy import deepcopy

from cumulus_lambda_functions.lib.json_validator import JsonValidator


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


class LambdaApiGatewayUtils:
    @staticmethod
    def generate_requesting_url(event: dict):
        api_gateway_event_validator_result = JsonValidator(API_GATEWAY_EVENT_SCHEMA).validate(event)
        if api_gateway_event_validator_result is not None:
            raise ValueError(f'invalid event: {api_gateway_event_validator_result}. event: {event}')
        requesting_url = f"https://{event['headers']['Host']}{event['requestContext']['path']}"
        return requesting_url

    @staticmethod
    def generate_next_url(event: dict, default_limit: int = 10):
        requesting_base_url = LambdaApiGatewayUtils.generate_requesting_url(event)
        new_queries = deepcopy(event['queryStringParameters']) if 'queryStringParameters' in event and event['queryStringParameters'] is not None else {}
        limit = int(new_queries['limit'] if 'limit' in new_queries else default_limit)
        if limit == 0:
            return ''
        offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
        offset += limit
        new_queries['limit'] = limit
        new_queries['offset'] = offset
        requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        return requesting_url

    @staticmethod
    def generate_prev_url(event: dict, default_limit: int = 10):
        requesting_base_url = LambdaApiGatewayUtils.generate_requesting_url(event)
        new_queries = deepcopy(event['queryStringParameters']) if 'queryStringParameters' in event and event['queryStringParameters'] is not None else {}
        limit = int(new_queries['limit'] if 'limit' in new_queries else default_limit)
        if limit == 0:
            return ''
        offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
        offset -= limit
        if offset < 0:
            offset = 0
        new_queries['limit'] = limit
        new_queries['offset'] = offset
        requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        return requesting_url
