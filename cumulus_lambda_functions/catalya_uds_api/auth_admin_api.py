from typing import Union

from cumulus_lambda_functions.daac_archiver.ddb_mws.catalia_auth_db import CataliaAuthDb
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from fastapi import APIRouter, HTTPException, Request

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

import os

from pydantic import BaseModel

from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class AuthDeleteModel(BaseModel):
    source: str
    target: str
    group_name: str


class AuthDeleteModelAlgorithm(BaseModel):
    source: str
    target: str
    algorithm_name: str
    algorithm_version: str


delete_schema = {
    'type': 'object',
    'required': ['source', 'target', 'group_name'],
    'properties': {
        'source': {'type': 'string'},
        'target': {'type': 'string'},
        'group_name': {'type': 'string'},
    }
}


class AuthListModel(BaseModel):
    group_name: list[str]


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


class AuthAddModel(BaseModel):
    source: str
    target: str
    group_name: str
    access: bool

class AuthAddModelAlgorithm(BaseModel):
    source: str
    target: str
    algorithm_name: str
    algorithm_version: str
    access: bool

add_schema = {
    'type': 'object',
    'required': ['source', 'target', 'group_name', 'access'],
    'properties': {
        'source': {'type': 'string'},
        'target': {'type': 'string'},
        'group_name': {'type': 'string'},
        'access': {'type': 'boolean'},
    }
}


class AuthCrud:
    def __init__(self, authorization_info, request_body):
        required_env = ['ADMIN_COMMA_SEP_GROUPS', 'CATALYA_DB_NAME']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.__request_body = request_body
        self.__authorization_info = authorization_info
        self.__admin_groups = [k.strip() for k in os.getenv('ADMIN_COMMA_SEP_GROUPS').split(',')]
        self.__cad = CataliaAuthDb(os.getenv('CATALYA_DB_NAME'))

    def is_admin(self):
        belonged_admin_groups = list(set(self.__admin_groups) & set(self.__authorization_info['ldap_groups']))
        if len(belonged_admin_groups) < 1:
            LOGGER.warn(f'unauthorized attempt to admin function: {self.__authorization_info}')
            return {
                'statusCode': 403,
                'body': {'message': f'user is not in admin groups: {self.__admin_groups}'}
            }
        return {
                'statusCode': 200,
                'body': {}
            }

    def list_all_record(self):
        return {
                'statusCode': 501,
                'body': {'message': 'Not Implemented Yet'}
            }
        # return {
        #         'statusCode': 200,
        #         'body': all_records
        #     }

    def convert_algorithm_to_group_name(self):
        self.__request_body['group_name'] = f"{self.__request_body['algorithm_name']}___{self.__request_body['algorithm_version']}"
        return self

    def add_new_record(self):
        body_validator_result = JsonValidator(add_schema).validate(self.__request_body)
        if body_validator_result is not None:
            LOGGER.error(f'invalid add body: {body_validator_result}. request_body: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': f'invalid add body: {body_validator_result}. request_body: {self.__request_body}'
            }
        self.__cad.add(self.__request_body['group_name'], self.__request_body['source'], self.__request_body['target'], self.__request_body['access'])
        return {
            'statusCode': 200,
            'body': {'message': 'inserted'}
        }

    def delete_record(self):
        body_validator_result = JsonValidator(delete_schema).validate(self.__request_body)
        if body_validator_result is not None:
            LOGGER.error(f'invalid delete body: {body_validator_result}. request_body: {self.__request_body}')
            return {
                'statusCode': 500,
                'body': f'invalid delete body: {body_validator_result}. request_body: {self.__request_body}'
            }
        self.__cad.delete(self.__request_body['group_name'], self.__request_body['source'], self.__request_body['target'])
        return {
            'statusCode': 200,
            'body': {'message': 'deleted'}
        }


router = APIRouter(
    prefix=f'/{WebServiceConstants.ADMIN}/auth',
    tags=["Admin Records CRUD (Admins-Only)"],
    responses={404: {"description": "Not found"}},
)

@router.delete("")
@router.delete("/")
async def delete_auth_mapping(request: Request, delete_body: AuthDeleteModel):
    """
    Deleting one authorization mapping
    """
    LOGGER.debug(f'started delete_auth_mapping')
    auth_info = FastApiUtils.get_authorization_info(request)
    auth_crud = AuthCrud(auth_info, delete_body.model_dump())
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    delete_result = auth_crud.delete_record()
    if delete_result['statusCode'] == 200:
        return delete_result['body']
    raise HTTPException(status_code=delete_result['statusCode'], detail=delete_result['body'])

@router.post("")
@router.post("/")
async def add_auth_mapping(request: Request, new_body: AuthAddModel):
    """
    Adding a new Authorization mapping
    """
    LOGGER.debug(f'started add_auth_mapping. sss {new_body.model_dump()}')
    auth_info = FastApiUtils.get_authorization_info(request)
    auth_crud = AuthCrud(auth_info, new_body.model_dump())
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    add_result = auth_crud.add_new_record()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])

@router.delete("/algorithm")
@router.delete("/algorithm/")
async def delete_auth_mapping(request: Request, delete_body: AuthDeleteModelAlgorithm):
    """
    Deleting one authorization mapping
    """
    LOGGER.debug(f'started delete_auth_mapping')
    auth_info = FastApiUtils.get_authorization_info(request)
    auth_crud = AuthCrud(auth_info, delete_body.model_dump())
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    delete_result = auth_crud.convert_algorithm_to_group_name().delete_record()
    if delete_result['statusCode'] == 200:
        return delete_result['body']
    raise HTTPException(status_code=delete_result['statusCode'], detail=delete_result['body'])

@router.post("/algorithm")
@router.post("/algorithm/")
async def add_auth_mapping_for_algorithms(request: Request, new_body: AuthAddModelAlgorithm):
    """
    Adding a new Authorization mapping
    """
    LOGGER.debug(f'started add_auth_mapping. sss {new_body.model_dump()}')
    auth_info = FastApiUtils.get_authorization_info(request)
    auth_crud = AuthCrud(auth_info, new_body.model_dump())
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    add_result = auth_crud.convert_algorithm_to_group_name().add_new_record()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])

@router.get("")
@router.get("/")
async def list_auth_mappings(request: Request, tenant: Union[str, None]=None, venue: Union[str, None]=None, group_names: Union[str, None]=None):
    """
    Listing all exsiting Authorization Mapping.

    """
    LOGGER.debug(f'started list_auth_mappings')
    auth_info = FastApiUtils.get_authorization_info(request)
    query_body = {
        'tenant': tenant,
        'venue': venue,
        'ldap_group_names': group_names if group_names is None else [k.strip() for k in group_names.split(',')],
    }
    auth_crud = AuthCrud(auth_info, query_body)
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    query_result = auth_crud.list_all_record()
    if query_result['statusCode'] == 200:
        return query_result['body']
    raise HTTPException(status_code=query_result['statusCode'], detail=query_result['body'])
