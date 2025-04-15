import json
import os
from glob import glob
from time import time
from typing import Union

from mdps_ds_lib.lib.utils.file_utils import FileUtils
from starlette.responses import Response, RedirectResponse
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from fastapi import APIRouter, HTTPException, Request
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants


LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.MISC}',
    tags=["Miscellaneous API"],
    responses={404: {"description": "Not found"}},
)


@router.get(f'/catalog_list')
@router.get(f'/catalog_list/')
async def catalog_list(request: Request, response: Response):
    """
    This is to list all catalogs for STAC Browser.
    This doesn't require any authorization token.
    :param request:
    :param response:
    :return:
    """
    base_url = os.environ.get(WebServiceConstants.BASE_URL, f'{request.url.scheme}://{request.url.netloc}')
    base_url = base_url[:-1] if base_url.endswith('/') else base_url
    base_url = base_url if base_url.startswith('http') else f'https://{base_url}'
    api_base_prefix = FastApiUtils.get_api_base_prefix()
    stac_browser_expecting_result = [{
        "id": 1,
        "url": f'{base_url}/{api_base_prefix}/catalog',
        "slug": "unity-ds",
        "title": "Unity DS (Venue: TODO)",
        "summary": "Unity DS collections & granules",
        "access": "public",
        "created": "2023-03-16T09:15:31.242Z",
        "updated": "2023-03-16T09:15:31.242Z",
        "isPrivate": False,
        "isApi": False,
        "accessInfo": None
    }]
    return stac_browser_expecting_result


@router.get(f'/stac_entry')
@router.get(f'/stac_entry/')
async def stac_entry(request: Request, response: Response):
    """
    This is an API to start STAC Browser.
    Optionally, it will add a required authorization cookie if available.
    However, this endpoint should be called from a separate URL due to the infrastructure.

    How to re-load UCS
    https://github.com/unity-sds/unity-data-services/issues/381#issuecomment-2201165672

    :param request:
    :param response:
    :return:
    """
    request_headers = dict(request.headers)
    LOGGER.debug(f'stac_entry - request_headers: {request_headers}')
    print(request_headers)
    base_url = os.environ.get(WebServiceConstants.BASE_URL, f'{request.url.scheme}://{request.url.netloc}')
    base_url = base_url[:-1] if base_url.endswith('/') else base_url
    base_url = base_url if base_url.startswith('http') else f'https://{base_url}'
    api_base_prefix = FastApiUtils.get_api_base_prefix()
    ending_url = f'{WebServiceConstants.STAC_BROWSER}/' if str(request.url).endswith('/') else WebServiceConstants.STAC_BROWSER
    redirect_response = RedirectResponse(f'/{api_base_prefix}/{ending_url}')
    if 'oidc_access_token' in request_headers:
        # TODO not sure cookie settings need to be stricter
        redirect_response.set_cookie(key="unity_token", value=request_headers['oidc_access_token'], httponly=False, secure=False, samesite='strict')  # missing , domain=base_url
        redirect_response.set_cookie(key="test1", value=f"{time()}", httponly=False, secure=False, samesite='strict')  # missing , domain=base_url
    return redirect_response


@router.get(f'/version')
@router.get(f'/version/')
async def ds_version(request: Request, response: Response):
    """
    This is to list all catalogs for STAC Browser.
    This doesn't require any authorization token.
    :param request:
    :param response:
    :return:
    """
    version_details_unknown = {
        'version': 'unknown',
        'built': 'unknown'
    }
    if not FileUtils.file_exist('/var/task/ds_version.json'):
        print(f'missing file : {[k for k in glob("/var/task/*.json")]}')
        return version_details_unknown
    version_details = FileUtils.read_json('/var/task/ds_version.json')

    version_details = {
        **version_details_unknown,
        **version_details,
    }
    return version_details
