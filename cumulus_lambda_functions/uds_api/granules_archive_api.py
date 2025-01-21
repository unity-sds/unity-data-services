import json
import os

from cumulus_lambda_functions.uds_api.dapa.daac_archive_crud import DaacArchiveCrud, DaacDeleteModel, DaacAddModel, \
    DaacUpdateModel

from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract

from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from fastapi import APIRouter, HTTPException, Request

from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Granules Archive CRUD API"],
    responses={404: {"description": "Not found"}},
)

@router.put("/{collection_id}/archive")
@router.put("/{collection_id}/archive/")
async def dapa_archive_add_config(request: Request, collection_id: str, new_body: DaacAddModel):
    LOGGER.debug(f'started dapa_archive_add_config. {new_body.model_dump()}')
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    if '___' not in collection_identifier.id:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': f'missing version in collection ID. collection_id: {collection_id}'
        }))
    daac_crud = DaacArchiveCrud(auth_info, collection_id, new_body.model_dump())
    add_result = daac_crud.add_new_config()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])

@router.post("/{collection_id}/archive")
@router.post("/{collection_id}/archive/")
async def dapa_archive_update_config(request: Request, collection_id: str, new_body: DaacUpdateModel):
    LOGGER.debug(f'started dapa_archive_add_config. {new_body.model_dump()}')
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    if '___' not in collection_identifier.id:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': f'missing version in collection ID. collection_id: {collection_id}'
        }))
    daac_crud = DaacArchiveCrud(auth_info, collection_id, new_body.model_dump())
    add_result = daac_crud.update_config()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])

@router.delete("/{collection_id}/archive")
@router.delete("/{collection_id}/archive/")
async def dapa_archive_delete_config(request: Request, collection_id: str, new_body: DaacDeleteModel):
    LOGGER.debug(f'started dapa_archive_add_config. {new_body.model_dump()}')
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    if '___' not in collection_identifier.id:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': f'missing version in collection ID. collection_id: {collection_id}'
        }))
    daac_crud = DaacArchiveCrud(auth_info, collection_id, new_body.model_dump())
    add_result = daac_crud.delete_config()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])

@router.get("/{collection_id}/archive")
@router.get("/{collection_id}/archive/")
async def dapa_archive_get_config(request: Request, collection_id: str):
    # TODO return UDS SNS to accept DAAC messages here
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    daac_crud = DaacArchiveCrud(auth_info, collection_id, {})
    add_result = daac_crud.get_config()
    if add_result['statusCode'] == 200:
        return add_result['body']
    raise HTTPException(status_code=add_result['statusCode'], detail=add_result['body'])
