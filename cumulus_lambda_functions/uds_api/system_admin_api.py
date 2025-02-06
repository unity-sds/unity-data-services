from typing import Union

from cumulus_lambda_functions.cumulus_es_setup.es_setup import SetupESIndexAlias
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.dapa.auth_crud import AuthCrud, AuthDeleteModel, AuthListModel, AuthAddModel
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from fastapi import APIRouter, HTTPException, Request, Response

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.ADMIN}/system',
    tags=["System Admin Records CRUD (Admins-Only)"],
    responses={404: {"description": "Not found"}},
)


@router.put("/es_setup")
@router.put("/es_setup/")
async def es_setup(request: Request, tenant: Union[str, None]=None, venue: Union[str, None]=None, group_names: Union[str, None]=None):
    LOGGER.debug(f'started es_setup')
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
    try:
        SetupESIndexAlias().start()
    except Exception as e:
        LOGGER.exception(f'')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'successful'}
