import json
import os

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract
from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory
from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
from mdps_ds_lib.lib.utils.lambda_api_gateway_utils import LambdaApiGatewayUtils

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


delete_schema = {
    'type': 'object',
    'required': ['tenant', 'venue', 'group_name'],
    'properties': {
        'tenant': {'type': 'string'},
        'venue': {'type': 'string'},
        'group_name': {'type': 'string'},
    }
}

list_schema = {
    'type': 'object',
    'properties': {
        'tenant': {'type': 'string'},
        'venue': {'type': 'string'},
        'group_names': {
            'type': 'array',
            'items': {'type': 'string'},
            'minItems': 1,
        },
    }
}

add_schema = {
    'type': 'object',
    'required': ['tenant', 'venue', 'group_name', 'actions', 'resources'],
    'properties': {
        'tenant': {'type': 'string'},
        'venue': {'type': 'string'},
        'group_name': {'type': 'string'},
        'actions': {
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': [DBConstants.create, DBConstants.delete, DBConstants.update, DBConstants.read]
            },
            'minItems': 1,
        },
        'resources': {
            'type': 'array',
            'items': {'type': 'string'},
            'minItems': 1,
        },
    }

}


class AuthCrud:
    def __init__(self, event):
        required_env = ['ES_URL', 'ADMIN_COMMA_SEP_GROUPS']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__admin_groups = [k.strip() for k in os.getenv('ADMIN_COMMA_SEP_GROUPS').split(',')]
        self.__event = event
        self.__request_body = {}
        self.__es_url = os.getenv('ES_URL')
        self.__es_port = int(os.getenv('ES_PORT', '443'))
        self.__authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
            .get_instance(UDSAuthorizerFactory.cognito,
                          es_url=self.__es_url,
                          es_port=self.__es_port
                          )
        self.__lambda_utils = LambdaApiGatewayUtils(self.__event, 10)

    def __is_admin(self):
        auth_info = self.__lambda_utils.get_authorization_info()
        belonged_admin_groups = list(set(self.__admin_groups) & set(auth_info['ldap_groups']))
        return len(belonged_admin_groups) > 0

    def __load_request_body(self):
        if 'body' in self.__event and self.__event['body'] is not None:
            self.__request_body = json.loads(self.__event['body'])
        return

    def list_all_record(self):
        if not self.__is_admin():
            return {
                'statusCode': 403,
                'body': f'user is not in admin groups: {self.__admin_groups}'
            }
        self.__load_request_body()
        all_records = self.__authorizer.list_groups(
            tenant=self.__request_body['tenant'] if 'tenant' in self.__request_body else None,
            venue=self.__request_body['venue'] if 'venue' in self.__request_body else None,
            ldap_group_names=self.__request_body['group_names'] if 'group_names' in self.__request_body else None,
        )
        return {
                'statusCode': 200,
                'body': json.dumps(all_records)
            }

    def add_new_record(self):
        if not self.__is_admin():
            return {
                'statusCode': 403,
                'body': f'user is not in admin groups: {self.__admin_groups}'
            }
        self.__load_request_body()
        body_validator_result = JsonValidator(add_schema).validate(self.__request_body)
        if body_validator_result is not None:
            LOGGER.error(f'invalid add body: {body_validator_result}. request_body: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': f'invalid add body: {body_validator_result}. request_body: {self.__request_body}'
            }
        self.__authorizer.add_authorized_group(
            action=self.__request_body['actions'],
            resource=self.__request_body['resources'],
            tenant=self.__request_body['tenant'],
            venue=self.__request_body['venue'],
            ldap_group_name=self.__request_body['group_name'],
        )
        return {
            'statusCode': 200,
            'body': 'inserted'
        }

    def update_record(self):
        if not self.__is_admin():
            return {
                'statusCode': 403,
                'body': f'user is not in admin groups: {self.__admin_groups}'
            }
        self.__load_request_body()
        body_validator_result = JsonValidator(add_schema).validate(self.__request_body)
        if body_validator_result is not None:
            LOGGER.error(f'invalid update body: {body_validator_result}. request_body: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': f'invalid update body: {body_validator_result}. request_body: {self.__request_body}'
            }
        self.__authorizer.update_authorized_group(
            action=self.__request_body['actions'],
            resource=self.__request_body['resources'],
            tenant=self.__request_body['tenant'],
            venue=self.__request_body['venue'],
            ldap_group_name=self.__request_body['group_name'],
        )
        return {
            'statusCode': 200,
            'body': 'updated'
        }

    def delete_record(self):
        if not self.__is_admin():
            return {
                'statusCode': 403,
                'body': f'user is not in admin groups: {self.__admin_groups}'
            }
        self.__load_request_body()
        body_validator_result = JsonValidator(delete_schema).validate(self.__request_body)
        if body_validator_result is not None:
            LOGGER.error(f'invalid delete body: {body_validator_result}. request_body: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': f'invalid delete body: {body_validator_result}. request_body: {self.__request_body}'
            }
        self.__authorizer.delete_authorized_group(
            tenant=self.__request_body.get('tenant'),
            venue=self.__request_body.get('venue'),
            ldap_group_name=self.__request_body.get('group_name'),
        )
        return {
            'statusCode': 200,
            'body': 'deleted'
        }
