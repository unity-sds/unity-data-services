import json
import os
from typing import Union

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from pystac import Item

from cumulus_lambda_functions.cumulus_wrapper.query_granules import GranulesQuery

from cumulus_lambda_functions.daac_archiver.daac_archiver_logic import DaacArchiverLogic
from cumulus_lambda_functions.uds_api.dapa.daac_archive_crud import DaacArchiveCrud, DaacDeleteModel, DaacAddModel, \
    DaacUpdateModel
from cumulus_lambda_functions.uds_api.dapa.granules_dapa_query_es import GranulesDapaQueryEs
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract

from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from fastapi import APIRouter, HTTPException, Request

from cumulus_lambda_functions.uds_api.dapa.granules_dapa_query import GranulesDapaQuery
from cumulus_lambda_functions.uds_api.dapa.pagination_links_generator import PaginationLinksGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Granules CRUD API"],
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


# https://docs.ogc.org/per/20-025r1.html#_get_collectionscollectionidvariables
@router.get("/{collection_id}/variables")
@router.get("/{collection_id}/variables/")
async def get_granules_dapa(request: Request, collection_id: str):
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

    try:
        granules_db_index = GranulesDbIndex()
        granule_index_mapping = granules_db_index.get_latest_index(collection_identifier.tenant, collection_identifier.venue)
        # This is the response from the method
        # {"unity_granule_main_project1694791693139_dev__v02":{"mappings":{"dynamic":"strict","properties":{"collection_id":{"type":"keyword"},"event_time":{"type":"long"},"granule_id":{"type":"keyword"},"last_updated":{"type":"long"},"tag":{"type":"keyword"}}}}}
        # needs to drill down to properties
        custom_metadata = granules_db_index.get_custom_metadata_fields(granule_index_mapping)
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    return custom_metadata


@router.get("/{collection_id}/items")
@router.get("/{collection_id}/items/")
async def get_granules_dapa(request: Request, collection_id: str, limit: Union[int, None] = 10, offset: Union[str, None] = None, datetime: Union[str, None] = None, filter: Union[str, None] = None):
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

    try:
        pagination_links = PaginationLinksGenerator(request)
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        granules_dapa_query = GranulesDapaQueryEs(collection_id, limit, offset, datetime, filter, pagination_links, f'{pagination_links.base_url}/{api_base_prefix}')
        granules_result = granules_dapa_query.start()
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if granules_result['statusCode'] == 200:
        return granules_result['body']
    raise HTTPException(status_code=granules_result['statusCode'], detail=granules_result['body'])


@router.get("/{collection_id}/items/{granule_id}")
@router.get("/{collection_id}/items/{granule_id}/")
async def get_single_granule_dapa(request: Request, collection_id: str, granule_id: str):
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
    try:
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        pg_link_generator = PaginationLinksGenerator(request)
        granules_dapa_query = GranulesDapaQueryEs(collection_id, 1, None, None, filter, None, f'{pg_link_generator.base_url}/{api_base_prefix}')
        granules_result = granules_dapa_query.get_single_granule(granule_id)
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    return granules_result

@router.delete("/{collection_id}/items/{granule_id}")
@router.delete("/{collection_id}/items/{granule_id}/")
async def delete_single_granule_dapa(request: Request, collection_id: str, granule_id: str, delete_files: bool=True):
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.delete, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    try:
        LOGGER.debug(f'deleting granule: {granule_id}')
        cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
        cumulus = GranulesQuery('https://na/dev', 'NA')
        cumulus.with_collection_id(collection_id)
        cumulus_delete_result = cumulus.delete_entry(cumulus_lambda_prefix, granule_id)  # TODO not sure it is correct granule ID
        LOGGER.debug(f'cumulus_delete_result: {cumulus_delete_result}')
        es_delete_result = GranulesDbIndex().delete_entry(collection_identifier.tenant,
                                                          collection_identifier.venue,
                                                          granule_id
                                                          )
        LOGGER.debug(f'es_delete_result: {es_delete_result}')
        es_delete_result = [Item.from_dict(k['_source']) for k in es_delete_result['hits']['hits']]
        if delete_files is False:
            LOGGER.debug(f'Not deleting files as it is set to false in the request')
            return {}
        s3 = AwsS3()
        for each_granule in es_delete_result:
            s3_urls = [v.href for k, v in each_granule.assets.items()]
            LOGGER.debug(f'deleting S3 for {each_granule.id} - s3_urls: {s3_urls}')
            delete_result = s3.delete_multiple(s3_urls=s3_urls)
            LOGGER.debug(f'delete_result for {each_granule.id} - delete_result: {delete_result}')
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    return {}


@router.put("/{collection_id}/archive/{granule_id}")
@router.put("/{collection_id}/archive/{granule_id}/")
async def archive_single_granule_dapa(request: Request, collection_id: str, granule_id: str):
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
    try:
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        pg_link_generator = PaginationLinksGenerator(request)
        granules_dapa_query = GranulesDapaQueryEs(collection_id, 1, None, None, filter, None, f'{pg_link_generator.base_url}/{api_base_prefix}')
        granules_result = granules_dapa_query.archive_single_granule(granule_id)
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'archive initiated'}
