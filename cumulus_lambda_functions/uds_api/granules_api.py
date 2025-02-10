import json
import os
from time import sleep
from typing import Union, Optional

from pydantic import BaseModel
from starlette.responses import Response, JSONResponse

from cumulus_lambda_functions.cumulus_wrapper.query_granules import GranulesQuery

from cumulus_lambda_functions.uds_api.dapa.granules_dapa_query_es import GranulesDapaQueryEs
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract

from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from fastapi import APIRouter, HTTPException, Request, Query, Path

from cumulus_lambda_functions.uds_api.dapa.pagination_links_generator import PaginationLinksGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Granules CRUD API"],
    responses={404: {"description": "Not found"}},
)

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
async def get_granules_dapa(request: Request, collection_id: str=Path(description="Collection ID. To query across different collections, use '*'. Example: 'URN:NASA:UNITY:MY_TENANT:DEV:\\*'"),
                            limit: Union[int, None] = Query(10, description='Number of items in each page.'),
                            offset: Union[str, None] = Query(None, description='Pagination Item from current page to get the next page'),
                            datetime: Union[str, None] = Query(None, description='Example: 2018-02-12T23:20:50Z'),
                            filter: Union[str, None] = Query(None, description="OGC CQL filters: https://portal.ogc.org/files/96288#rc_cql-text -- Example: id in (g1,g2,g3) and tags::core = 'level-3' and (time1 < 34 or time1 > 14)"),
                            bbox: Union[str, None]=Query(None, description='Bounding box in minx,miny,maxx,maxy -- Example: bbox=12.3,0.3,14.4,2.3'),
                            sortby: Union[str, None]=Query(None, description='Sort the results based on the comma separated parameters, each sorting key can be started with + / - for ascending / descending order. missing operator is assumed "+". Example: sortby=+id,-properties.created'),
                            ):
    # https://docs.ogc.org/DRAFTS/24-030.html#sortby-parameter
    # https://docs.ogc.org/DRAFTS/24-030.html#_declaring_default_sort_order
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
        bbox_array = [float(k) for k in bbox.split(',')] if bbox is not None else None
        granules_dapa_query = GranulesDapaQueryEs(collection_id, limit, offset, datetime, filter, pagination_links, f'{pagination_links.base_url}/{api_base_prefix}', bbox_array, sortby)
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
async def delete_single_granule_dapa_actual(request: Request, collection_id: str, granule_id: str):
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
        include_cumulus = os.getenv('CUMULUS_INCLUSION', 'TRUE').upper().strip() == 'TRUE'
        if include_cumulus:
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
        # es_delete_result = [Item.from_dict(k['_source']) for k in es_delete_result['hits']['hits']]
        # if delete_files is False:
        #     LOGGER.debug(f'Not deleting files as it is set to false in the request')
        #     return {}
        # s3 = AwsS3()
        # for each_granule in es_delete_result:
        #     s3_urls = [v.href for k, v in each_granule.assets.items()]
        #     LOGGER.debug(f'deleting S3 for {each_granule.id} - s3_urls: {s3_urls}')
        #     delete_result = s3.delete_multiple(s3_urls=s3_urls)
        #     LOGGER.debug(f'delete_result for {each_granule.id} - delete_result: {delete_result}')
    except Exception as e:
        LOGGER.exception('failed during delete_single_granule_dapa_actual')
        raise HTTPException(status_code=500, detail=str(e))
    return {}


class StacGranuleModel(BaseModel):
    """
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "URN:NASA:AVIRIS:f240424t01:p00_r10",
        "properties": {
            "start_datetime": "24-04-24T20:37:00.000000",
            "end_datetime": "24-04-24T20:50:00.000000",
            "site_name": "x001(orthocorrected)",
            "nasa_log": 232016.0,
            "investigator": "Raymond Kokaly",
            "comments": "x001 s-)n; LN2 refill 2042",
            "site_info": "GEMx - RFLY02",
            "datetime": "1970-01-01T00:00:00Z"
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                0.0,
                0.0
            ]
        },
        "links": [],
        "assets": {
            "l1b": {
                "href": "https://popo.jpl.nasa.gov/gemx/data_products/l1b/f240424t01p00r10rdn_g.tar.gz",
                "title": "f240424t01p00r10rdn_g.tar.gz",
                "description": "2024-10-08 15:16",
                "file:size": 2362232012.8
            },
            "l2": {
                "href": "https://popo.jpl.nasa.gov/gemx/data_products/l2/f240424t01p00r10rfl.tar.gz",
                "title": "f240424t01p00r10rfl.tar.gz",
                "description": "2024-10-18 08:22",
                "file:size": 4187593113.6
            },
            "quicklook": {
                "href": "http://aviris.jpl.nasa.gov/ql/24qlook/f240424t01p00r10_geo.jpeg",
                "title": "f240424t01p00r10_geo.jpeg",
                "description": "Quicklook Link"
            }
        },
        "bbox": [
            32.5,
            -114.314407,
            33.5,
            -114.314407
        ],
        "stac_extensions": [
            "https://stac-extensions.github.io/file/v2.1.0/schema.json"
        ],
        "collection": "URN:NASA:AVIRIS:f240424t01"
    """
    stac_extensions: list[str]
    collection: str
    bbox: list[float]
    assets: dict
    links: list
    geometry: dict
    properties: dict
    id: str
    stac_version: str
    type: str

@router.put("/{collection_id}/items/{granule_id}")
@router.put("/{collection_id}/items/{granule_id}/")
async def add_single_granule_dapa(request: Request, collection_id: str, granule_id: str, new_granule: StacGranuleModel, response: Response):
    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443')),
                      use_ssl=os.getenv('ES_USE_SSL', 'TRUE').strip() is True,
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
        LOGGER.debug(f'adding granule: {granule_id}')
        new_granule = new_granule.model_dump()
        include_cumulus = os.getenv('CUMULUS_INCLUSION', 'TRUE').upper().strip() == 'TRUE'
        if include_cumulus:
            cumulus_lambda_prefix = os.getenv('CUMULUS_LAMBDA_PREFIX')
            cumulus = GranulesQuery('https://na/dev', 'NA')
            cumulus.with_collection_id(collection_id)
            raise NotImplementedError(f'Please implement to convert stac into cumulus granule')
            cumulus_add_result = cumulus.add_entry(cumulus_lambda_prefix, {})  # TODO not sure it is correct granule ID
            LOGGER.debug(f'cumulus_add_result: {cumulus_add_result}')
        if 'bbox' in new_granule:
            new_granule['bbox'] = GranulesDbIndex.to_es_bbox(new_granule['bbox'])
        collection_identifier = UdsCollections.decode_identifier(collection_id)
        LOGGER.debug(f'new_granule: {new_granule}')
        es_add_result = GranulesDbIndex().add_entry(collection_identifier.tenant,
                                                    collection_identifier.venue,
                                                    new_granule,
                                                    granule_id
                                                    )
        LOGGER.debug(f'es_add_result: {es_add_result}')
    except Exception as e:
        LOGGER.exception('failed during add_single_granule_dapa')
        raise HTTPException(status_code=500, detail=str(e))
    return {}

# @router.delete("/{collection_id}/items/{granule_id}")
# @router.delete("/{collection_id}/items/{granule_id}/")
# async def delete_single_granule_dapa_facade(request: Request, collection_id: str, granule_id: str, response: Response, response_class=JSONResponse):
#     authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
#         .get_instance(UDSAuthorizerFactory.cognito,
#                       es_url=os.getenv('ES_URL'),
#                       es_port=int(os.getenv('ES_PORT', '443'))
#                       )
#     auth_info = FastApiUtils.get_authorization_info(request)
#     collection_identifier = UdsCollections.decode_identifier(collection_id)
#     if not authorizer.is_authorized_for_collection(DBConstants.delete, collection_id,
#                                                    auth_info['ldap_groups'],
#                                                    collection_identifier.tenant,
#                                                    collection_identifier.venue):
#         LOGGER.debug(f'user: {auth_info["username"]} is not authorized for {collection_id}')
#         raise HTTPException(status_code=403, detail=json.dumps({
#             'message': 'not authorized to execute this action'
#         }))
#     try:
#         LOGGER.debug(f'deleting granule: {granule_id}')
#         granules_dapa_query = GranulesDapaQueryEs(collection_id, -1, -1, None, None, None, '')
#         delete_prep_result = granules_dapa_query.delete_facade(request.url, request.headers.get('Authorization', ''))
#     except Exception as e:
#         LOGGER.exception('failed during delete_single_granule_dapa')
#         raise HTTPException(status_code=500, detail=str(e))
#     if delete_prep_result['statusCode'] < 300:
#         response.status_code = delete_prep_result['statusCode']
#         return delete_prep_result['body']
#     raise HTTPException(status_code=delete_prep_result['statusCode'], detail=delete_prep_result['body'])
