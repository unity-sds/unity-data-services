import os
from typing import Union

from pystac import Catalog, Link

from cumulus_lambda_functions.lib.uds_db.db_constants import DBConstants

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.authorization.uds_authorizer_factory import UDSAuthorizerFactory

from cumulus_lambda_functions.lib.authorization.uds_authorizer_abstract import UDSAuthorizorAbstract

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from fastapi import APIRouter, HTTPException, Request, Response
from cumulus_lambda_functions.uds_api.dapa.collections_dapa_query import CollectionDapaQuery
from cumulus_lambda_functions.uds_api.dapa.pagination_links_generator import PaginationLinksGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.CATALOG}',
    tags=["Collection CRUD API"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
@router.get("/")
async def get_catalog(request: Request, limit: Union[int, None] = 10, offset: Union[int, None] = 0, ):
    LOGGER.debug(f'starting get_catalog request: {request}')

    authorizer: UDSAuthorizorAbstract = UDSAuthorizerFactory() \
        .get_instance(UDSAuthorizerFactory.cognito,
                      es_url=os.getenv('ES_URL'),
                      es_port=int(os.getenv('ES_PORT', '443'))
                      )
    auth_info = FastApiUtils.get_authorization_info(request)
    uds_collections = UdsCollections(es_url=os.getenv('ES_URL'),
                                     es_port=int(os.getenv('ES_PORT', '443')), es_type=os.getenv('ES_TYPE', 'AWS'))
    collection_regexes = authorizer.get_authorized_collections(DBConstants.read, auth_info['ldap_groups'])
    LOGGER.info(f'collection_regexes: {collection_regexes}')
    authorized_collections = uds_collections.get_collections(collection_regexes)
    LOGGER.info(f'authorized_collections: {authorized_collections}')
    # Example: [{'collection_id': 'URN:NASA:UNITY:MAIN_PROJECT:DEV:CUMULUS_DAPA_UNIT_TEST___1697606545', 'granule_count': 0, 'start_time': 1697581345446, 'end_time': 1697581345446}]
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

        catalog = Catalog(
            id='unity_ds',
            description='Unity DS Catalog',
            title='Unity DS Catalog',
            href=pg_link_generator.base_url
        )
        api_base_prefix = FastApiUtils.get_api_base_prefix()
        authorized_collections_links = [Link(
            rel='child',
            target=f'{pg_link_generator.base_url}/{api_base_prefix}/collections/{k["collection_id"]}',
            media_type='application/json',
            title=k["collection_id"],
        ) for k in authorized_collections]
        catalog.add_links(authorized_collections_links)
        return catalog.to_dict(True, False)
    except Exception as e:
        LOGGER.exception('failed during get_granules_dapa')
        raise HTTPException(status_code=500, detail=str(e))
