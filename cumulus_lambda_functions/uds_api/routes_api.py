from fastapi import APIRouter

from cumulus_lambda_functions.uds_api import collections_api, granules_api, auth_admin_api, system_admin_api, \
    custom_meta_admin_api, catalog_api, misc_api, granules_archive_api

# from ideas_api.src.endpoints import job_endpoints
# from ideas_api.src.endpoints import process_endpoints
# from ideas_api.src.endpoints import setup_es


main_router = APIRouter(redirect_slashes=False)
# main_router.include_router(setup_es.router)
main_router.include_router(auth_admin_api.router)
main_router.include_router(system_admin_api.router)
main_router.include_router(collections_api.router)
main_router.include_router(catalog_api.router)
main_router.include_router(granules_api.router)
main_router.include_router(granules_archive_api.router)
main_router.include_router(custom_meta_admin_api.router)
main_router.include_router(misc_api.router)

