from typing import Union

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.dapa.auth_crud import AuthCrud, AuthDeleteModel, AuthListModel, AuthAddModel
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from fastapi import APIRouter, HTTPException, Request, Response

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

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

@router.put("")
@router.put("/")
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

@router.post("")
@router.post("/")
async def update_auth_mapping(request: Request, update_body: AuthAddModel):
    """
    Updating existing authorization mapping
    """
    LOGGER.debug(f'started update_auth_mapping')
    auth_info = FastApiUtils.get_authorization_info(request)
    auth_crud = AuthCrud(auth_info, update_body.model_dump())
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    update_result = auth_crud.update_record()
    if update_result['statusCode'] == 200:
        return update_result['body']
    raise HTTPException(status_code=update_result['statusCode'], detail=update_result['body'])

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
