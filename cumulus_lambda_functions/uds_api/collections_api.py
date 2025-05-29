import json
import os
from datetime import datetime
from typing import Union

from pystac import Catalog, Link, Collection, Extent, SpatialExtent, TemporalExtent, Summaries, Provider

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from fastapi import APIRouter, HTTPException, Request, Response

from cumulus_lambda_functions.uds_api.dapa.collections_dapa_cnm import CnmRequestBody, CollectionsDapaCnm
from cumulus_lambda_functions.uds_api.dapa.collections_dapa_creation import CollectionDapaCreation, \
    CumulusCollectionModel
from cumulus_lambda_functions.uds_api.dapa.collections_dapa_query import CollectionDapaQuery
from cumulus_lambda_functions.uds_api.dapa.pagination_links_generator import PaginationLinksGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from fastapi.responses import PlainTextResponse, JSONResponse

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Collection CRUD API"],
    responses={404: {"description": "Not found"}},
)

@router.put("")
@router.put("/")
async def ingest_cnm_dapa(request: Request, new_cnm_body: CnmRequestBody, response: Response, response_class=JSONResponse):
    """
    Ingestion of Granules for a given collection via CNM

    This is a facade endpoint which will trigger another endpoint which takes some time to execute ingestion
    """
    LOGGER.debug(f'starting ingest_cnm_dapa')
    collection_id = new_cnm_body.model_dump()
    if 'features' not in collection_id or len(collection_id['features']) < 1 or 'collection' not in collection_id['features'][0]:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': 'missing collection_id in request_body["features"][0]["collection"]'
        }))
    collection_id = collection_id['features'][0]['collection']
    collection_id = collection_id.split('___')[0]  # split id, version and only keeping id. TODO need this?
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.create, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    try:
        cnm_prep_result = CollectionsDapaCnm(new_cnm_body.model_dump()).start_facade(request.url)
    except Exception as e:
        LOGGER.exception('failed during ingest_cnm_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if cnm_prep_result['statusCode'] < 300:
        response.status_code = cnm_prep_result['statusCode']
        return cnm_prep_result['body']
    raise HTTPException(status_code=cnm_prep_result['statusCode'], detail=cnm_prep_result['body'])


@router.put("/actual")
@router.put("/actual/")
async def ingest_cnm_dapa_actual(request: Request, new_cnm_body: CnmRequestBody, response_class=JSONResponse):
    """
    Real ingestion of Granules for a given collection via CNM

    This will take some time to repeatedly create SNS messages for CNM

    """
    LOGGER.debug(f'starting ingest_cnm_dapa_actual')
    try:
        collections_dapa_cnm = CollectionsDapaCnm(new_cnm_body.model_dump())
        cnm_result = collections_dapa_cnm.start()
    except Exception as e:
        LOGGER.exception('failed during ingest_cnm_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if cnm_result['statusCode'] == 200:
        return cnm_result['body']
    raise HTTPException(status_code=cnm_result['statusCode'], detail=cnm_result['body'])


@router.post("")
@router.post("/")
async def create_new_collection(request: Request, new_collection: CumulusCollectionModel, response: Response):
    """
    Creating a new Cumulus Collection

    This is a facade endpoint which will trigger another endpoint which takes some time to hit Cumulus collection creation endpoint.
    """
    LOGGER.debug(f'starting create_new_collection')
    new_collection = new_collection.model_dump()
    collection_id = new_collection
    if 'id' not in collection_id:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': 'missing collection_id in request_body["id"]'
        }))
    collection_id = new_collection['id']
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.create, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))
    try:
        # new_collection = request.body()
        bearer_token = request.headers.get('Authorization', '')
        LOGGER.debug(f'create_new_collection--bearer_token: {bearer_token}')
        creation_result = CollectionDapaCreation(new_collection).start(request.url, bearer_token)
    except Exception as e:
        LOGGER.exception('failed during ingest_cnm_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if creation_result['statusCode'] < 300:
        response.status_code = creation_result['statusCode']
        return creation_result['body']
    raise HTTPException(status_code=creation_result['statusCode'], detail=creation_result['body'])


@router.post("/actual")
@router.post("/actual/")
async def create_new_collection_real(request: Request, new_collection: CumulusCollectionModel):
    """
    Actual endpoint to create a new Cumulus Collection
    """
    LOGGER.debug(f'starting create_new_collection_real')
    new_collection = new_collection.model_dump()
    collection_id = new_collection
    if 'id' not in collection_id:
        raise HTTPException(status_code=500, detail=json.dumps({
            'message': 'missing collection_id in request_body["id"]'
        }))
    collection_id = new_collection['id']
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    collection_identifier = UdsCollections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.create, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))

    try:
        creation_result = CollectionDapaCreation(new_collection).create()
    except Exception as e:
        LOGGER.exception('failed during ingest_cnm_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if creation_result['statusCode'] < 300:
        return creation_result['body'], creation_result['statusCode']
    raise HTTPException(status_code=creation_result['statusCode'], detail=creation_result['body'])

@router.get("/{collection_id}")
@router.get("/{collection_id}/")
async def get_single_collection(request: Request, collection_id: str, limit: Union[int, None] = 10, offset: Union[int, None] = 0, ):
    LOGGER.debug(f'starting get_single_collection: {collection_id}')
    LOGGER.debug(f'starting get_single_collection request: {request}')

    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    uds_collections = UdsCollections(es_url=os.getenv('ES_URL'),
                                     es_port=int(os.getenv('ES_PORT', '443')), es_type=os.getenv('ES_TYPE', 'AWS'))
    if collection_id is None or collection_id == '':
        raise HTTPException(status_code=500, detail=f'missing or invalid collection_id: {collection_id}')
    collection_identifier = uds_collections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))

    try:
        custom_params = {}
        if limit > CollectionDapaQuery.max_limit:
            LOGGER.debug(f'incoming limit > {CollectionDapaQuery.max_limit}. resetting to max. incoming limit: {limit}')
            limit = CollectionDapaQuery.max_limit
            custom_params['limit'] = limit
        LOGGER.debug(f'new limit: {limit}')
        pg_link_generator = PaginationLinksGenerator(request, custom_params)
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        collections_dapa_query = CollectionDapaQuery(collection_id, limit, offset, None,
                                                     f'{pg_link_generator.base_url}/{api_base_prefix}')
        collections_result = collections_dapa_query.get_collection()
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if collections_result['statusCode'] == 200:
        return collections_result['body']
    raise HTTPException(status_code=collections_result['statusCode'], detail=collections_result['body'])

@router.get("")
@router.get("/")
async def query_collections(request: Request, collection_id: Union[str, None] = None, limit: Union[int, None] = 10, offset: Union[int, None] = 0, ):
    LOGGER.debug(f'starting query_collections: {collection_id}')
    LOGGER.debug(f'starting query_collections request: {request}')

    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    uds_collections = UdsCollections(es_url=os.getenv('ES_URL'),
                                     es_port=int(os.getenv('ES_PORT', '443')), es_type=os.getenv('ES_TYPE', 'AWS'))
    if collection_id is not None:
        collection_identifier = uds_collections.decode_identifier(collection_id)
        if not authorizer.is_authorized_for_collection(DBConstants.read, collection_id,
                                                       auth_info['ldap_groups'],
                                                       collection_identifier.tenant,
                                                       collection_identifier.venue):
            LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
            raise HTTPException(status_code=403, detail=json.dumps({
                'message': 'not authorized to execute this action'
            }))
    else:
        collection_regexes = authorizer.get_authorized_collections(DBConstants.read, auth_info['ldap_groups'])
        LOGGER.info(f'collection_regexes: {collection_regexes}')
        authorized_collections = uds_collections.get_collections(collection_regexes)
        LOGGER.info(f'authorized_collections: {authorized_collections}')
        collection_id = [k[DBConstants.collection_id] for k in authorized_collections]
        LOGGER.info(f'authorized_collection_ids: {collection_id}')
        # NOTE: 2022-11-21: only pass collections. not versions

    try:
        custom_params = {}
        if limit > CollectionDapaQuery.max_limit:
            LOGGER.debug(f'incoming limit > {CollectionDapaQuery.max_limit}. resetting to max. incoming limit: {limit}')
            limit = CollectionDapaQuery.max_limit
            custom_params['limit'] = limit
        LOGGER.debug(f'new limit: {limit}')
        pg_link_generator = PaginationLinksGenerator(request, custom_params)
        pagination_links = pg_link_generator.generate_pagination_links()
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        collections_dapa_query = CollectionDapaQuery(collection_id, limit, offset, pagination_links, f'{pg_link_generator.base_url}/{api_base_prefix}')
        collections_result = collections_dapa_query.start()
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if collections_result['statusCode'] == 200:
        return collections_result['body']
    raise HTTPException(status_code=collections_result['statusCode'], detail=collections_result['body'])

@router.delete("/{collection_id}")
@router.delete("/{collection_id}/")
async def delete_single_collection(request: Request, collection_id: str):
    LOGGER.debug(f'starting delete_single_collection: {collection_id}')
    LOGGER.debug(f'starting delete_single_collection request: {request}')

    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    uds_collections = UdsCollections(es_url=os.getenv('ES_URL'),
                                     es_port=int(os.getenv('ES_PORT', '443')), es_type=os.getenv('ES_TYPE', 'AWS'))
    if collection_id is None or collection_id == '':
        raise HTTPException(status_code=500, detail=f'missing or invalid collection_id: {collection_id}')
    collection_identifier = uds_collections.decode_identifier(collection_id)
    if not authorizer.is_authorized_for_collection(DBConstants.delete, collection_id,
                                                   auth_info['ldap_groups'],
                                                   collection_identifier.tenant,
                                                   collection_identifier.venue):
        LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
        raise HTTPException(status_code=403, detail=json.dumps({
            'message': 'not authorized to execute this action'
        }))

    granules_count = GranulesDbIndex().get_size(collection_identifier.tenant, collection_identifier.venue,
                                                collection_id)
    LOGGER.debug(f'granules_count: {granules_count} for {collection_id}')
    if granules_count > 0:
        LOGGER.debug(f'NOT deleting {collection_id} as it is not empty')
        raise HTTPException(status_code=409, detail=f'NOT deleting {collection_id} as it is not empty')

    try:
        new_collection = Collection(
            id=collection_id,
            description='TODO',
            extent = Extent(
                SpatialExtent([[0.0, 0.0, 0.0, 0.0]]),
                TemporalExtent([[datetime.utcnow(), datetime.utcnow()]])
            ),
            license = "proprietary",
            providers = [],
                # title=input_collection['LongName'],
                # keywords=[input_collection['SpatialKeywords']['Keyword']],
            summaries = Summaries({
                "totalGranules": [-1],
            }),
            )
        creation_result = CollectionDapaCreation(new_collection).delete()
    except Exception as e:
        LOGGER.exception('failed during ingest_cnm_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    if creation_result['statusCode'] < 300:
        return creation_result['body'], creation_result['statusCode']
    raise HTTPException(status_code=creation_result['statusCode'], detail=creation_result['body'])
