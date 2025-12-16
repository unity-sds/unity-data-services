import json
import os
from typing import Optional

from cumulus_lambda_functions.daac_archiver.catalia_auth_db import CataliaAuthDb
from cumulus_lambda_functions.daac_archiver.catalia_daac_handshakes_db import CataliaDaacHandshakesDb
from cumulus_lambda_functions.daac_archiver.daac_archiver_catalia import DaacArchiverCatalia
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

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
    daac_collection_id: str
    api_key: str
    daac_provider: Optional[str] = None
    daac_data_version: Optional[str] = None
    daac_sns_topic_arn: Optional[str] = None
    daac_role_arn: Optional[str] = None
    daac_role_session_name: Optional[str] = None
    archiving_types: Optional[list[ArchivingTypesModel]] = None

class InternalDDBConnector:
    def __init__(self):
        required_env = ['CATALYA_DAAC_AGREEMENT_DB_NAME', 'CATALYA_DB_NAME']
        if not all([k in os.environ for k in required_env]):
            raise EnvironmentError(f'one or more missing env: {required_env}')
        self.cad = CataliaAuthDb(os.getenv('CATALYA_DB_NAME'))
        self.cdhsd = CataliaDaacHandshakesDb(os.getenv('CATALYA_DAAC_AGREEMENT_DB_NAME'))
        self.auth_info = {}
        self.configured_daac_configs = []

    def archive_methods_initiator(self, request, collection_id, daac_collection_id):
        LOGGER.debug(f'started archive_methods_initiator.')
        self.auth_info = FastApiUtils.get_authorization_info(request)
        if daac_collection_id is None:
            self.configured_daac_configs = self.cdhsd.search(collection_id)
            configured_daac_ids = [k[self.cdhsd.target_project] for k in self.configured_daac_configs]
        else:
            configured_daac_ids = [daac_collection_id]
        authorized_daacs = self.cad.get_authorized_daac_full(self.auth_info.get('ldap_groups'), collection_id, configured_daac_ids)
        if len(authorized_daacs) < 1:
            LOGGER.debug(f'user: {self.auth_info["username"]} is not authorized for {collection_id}')
            raise HTTPException(status_code=403, detail=json.dumps({
                'message': 'not authorized to execute this action'
            }))
        return authorized_daacs

@router.post("/{collection_id}/{daac_collection_id}/archive")
@router.post("/{collection_id}/{daac_collection_id}/archive/")
async def add_daac_archive_config(request: Request, collection_id: str, daac_collection_id: str, new_body: DaacUpdateModel):
    LOGGER.debug(f'started add_daac_archive_config. {new_body.model_dump()}')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, daac_collection_id)
    authorized_ldaps = [k['userGroup'] for k in authorized_daacs]
    b1 = new_body.model_dump()
    try:
        # def add(self, catalia_collection, daac_collection, api_key, provider, data_version, sns_topic_arn, role_arn, role_session_name, archiving_types, user, user_group):
        i1.cdhsd.add(collection_id, daac_collection_id, b1['api_key'], b1['daac_provider'], b1['daac_data_version'],
                     b1['daac_sns_topic_arn'], b1['daac_role_arn'], b1['daac_role_session_name'], b1['archiving_types'], i1.auth_info['username'], authorized_ldaps)
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

@router.put("/{collection_id}/archive/{granule_id}")
@router.put("/{collection_id}/archive/{granule_id}/")
async def archive_single_granule(request: Request, collection_id: str, granule_id: str):
    LOGGER.debug(f'started archive_single_granule.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_ldaps]
    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.archive_granule(collection_id, granule_id)
    return {'message': 'archive initiated'}

@router.put("/{collection_id}/archive")
@router.put("/{collection_id}/archive/")
async def archive_entire_collection(request: Request, collection_id: str):
    LOGGER.debug(f'started archive_entire_collection.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_ldaps]
    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.archive_collection(collection_id)  # TODO accept filtering mechanisms?
    return {'message': 'archive initiated'}

