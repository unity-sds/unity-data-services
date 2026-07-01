from typing import Optional

from pydantic import BaseModel

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_fast_api.internal_ddb_connector import InternalDDBConnector
from cumulus_lambda_functions.lib.uds_fast_api.web_service_constants import WebServiceConstants
from fastapi import APIRouter, HTTPException, Request, Response


LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Granules Archive CRUD API"],
    responses={404: {"description": "Not found"}},
)
class ArchivingTypesModel(BaseModel):
    data_type: str
    file_extension: Optional[list[str]] = []

class DaacUpdateModel(BaseModel):
    api_key: str
    daac_provider: str
    daac_data_version: str
    daac_sns_topic_arn: str
    daac_role_arn: str
    daac_role_session_name: str
    archiving_types: Optional[list[ArchivingTypesModel]] = None


@router.post("/{collection_id}/{daac_collection_id}/archive")
@router.post("/{collection_id}/{daac_collection_id}/archive/")
async def add_daac_archive_config(request: Request, collection_id: str, daac_collection_id: str, new_body: DaacUpdateModel):
    LOGGER.debug(f'started add_daac_archive_config. {new_body.model_dump()}')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, daac_collection_id)
    # authorized_ldaps = [k['userGroup'] for k in authorized_daacs]
    b1 = new_body.model_dump()
    try:
        # def add(self, catalia_collection, daac_collection, api_key, provider, data_version, sns_topic_arn, role_arn, role_session_name, archiving_types, user, user_group):
        i1.cdhsd.add(collection_id, daac_collection_id, b1['api_key'], b1['daac_provider'], b1['daac_data_version'],
                     b1['daac_sns_topic_arn'], b1['daac_role_arn'], b1['daac_role_session_name'], b1['archiving_types'], i1.auth_info['username'], i1.auth_info.get('ldap_groups'))
    except Exception as e:
        LOGGER.exception(f'error while add_daac_archive_config: {b1}')
        raise HTTPException(status_code=500, detail=e)
    return {'message': 'archive config added'}

@router.delete("/{collection_id}/{daac_collection_id}/archive")
@router.delete("/{collection_id}/{daac_collection_id}/archive/")
async def delete_daac_archive_config(request: Request, collection_id: str, daac_collection_id: str):
    LOGGER.debug(f'started delete_daac_archive_config.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, daac_collection_id)
    try:
        i1.cdhsd.delete(collection_id, daac_collection_id)
    except Exception as e:
        LOGGER.exception(f'error while delete_daac_archive_config: {collection_id}, {daac_collection_id}')
        raise HTTPException(status_code=500, detail=e)
    return {'message': 'archive config deleted'}

@router.get("/{collection_id}/{daac_collection_id}/archive")
@router.get("/{collection_id}/{daac_collection_id}/archive/")
async def get_daac_archive_config(request: Request, collection_id: str, daac_collection_id: str):
    LOGGER.debug(f'started get_daac_archive_config.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, daac_collection_id)
    try:
        result = i1.cdhsd.get_single(collection_id, daac_collection_id)
    except Exception as e:
        LOGGER.exception(f'error while get_daac_archive_config: {collection_id}, {daac_collection_id}')
        raise HTTPException(status_code=500, detail=e)
    return {'result': result}
