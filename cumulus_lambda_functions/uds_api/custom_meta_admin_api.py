from typing import Union

from cumulus_lambda_functions.cumulus_es_setup.es_setup import SetupESIndexAlias
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.dapa.auth_crud import AuthCrud, AuthDeleteModel, AuthListModel, AuthAddModel
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from fastapi import APIRouter, HTTPException, Request, Response

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.ADMIN}',
    tags=["Custom Metadata Index CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.put("/custom_metadata/{tenant}")
@router.put("/custom_metadata/{tenant}/")
async def custom_metadata_add(request: Request, tenant: str, venue: Union[str, None] = None, request_body: dict = {}):
    LOGGER.debug(f'started es_granules_index_setup')
    auth_info = FastApiUtils.get_authorization_info(request)
    query_body = {
        'tenant': tenant,
        'venue': venue,
    }
    auth_crud = AuthCrud(auth_info, query_body)
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    try:
        GranulesDbIndex().create_new_index(tenant, venue, request_body)
    except Exception as e:
        LOGGER.exception(f'')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'successful'}


@router.get("/custom_metadata/{tenant}")
@router.get("/custom_metadata/{tenant}/")
async def custom_metadata_get(request: Request, tenant: str, venue: Union[str, None] = None):
    LOGGER.debug(f'started es_granules_index_setup')
    auth_info = FastApiUtils.get_authorization_info(request)
    query_body = {
        'tenant': tenant,
        'venue': venue,
    }
    auth_crud = AuthCrud(auth_info, query_body)
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    try:
        granules_index_mapping = GranulesDbIndex().get_latest_index(tenant, venue)
    except Exception as e:
        LOGGER.exception(f'failed to retrieve granules mapping')
        raise HTTPException(status_code=500, detail=str(e))
    return granules_index_mapping


@router.delete("/custom_metadata/{tenant}/destroy")
@router.delete("/custom_metadata/{tenant}/destroy/")
async def custom_metadata_destroy(request: Request, tenant: str, venue: Union[str, None] = None):
    LOGGER.debug(f'started es_granules_index_setup')
    auth_info = FastApiUtils.get_authorization_info(request)
    query_body = {
        'tenant': tenant,
        'venue': venue,
    }
    auth_crud = AuthCrud(auth_info, query_body)
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    try:
        GranulesDbIndex().destroy_indices(tenant, venue)
    except Exception as e:
        LOGGER.exception(f'')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'successful'}


@router.delete("/custom_metadata/{tenant}")
@router.delete("/custom_metadata/{tenant}/")
async def custom_metadata_delete(request: Request, tenant: str, venue: Union[str, None] = None):
    LOGGER.debug(f'started es_granules_index_delete_setup')
    auth_info = FastApiUtils.get_authorization_info(request)
    query_body = {
        'tenant': tenant,
        'venue': venue,
    }
    auth_crud = AuthCrud(auth_info, query_body)
    is_admin_result = auth_crud.is_admin()
    if is_admin_result['statusCode'] != 200:
        raise HTTPException(status_code=is_admin_result['statusCode'], detail=is_admin_result['body'])
    try:
        GranulesDbIndex().delete_index(tenant, venue)
    except Exception as e:
        LOGGER.exception(f'')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'successful'}
