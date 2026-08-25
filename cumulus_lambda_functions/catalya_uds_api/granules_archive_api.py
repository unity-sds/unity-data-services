import json
import os
import boto3
from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore


from cumulus_lambda_functions.daac_archiver.daac_archiver_catalia_2 import DaacArchiverCatalia
from cumulus_lambda_functions.daac_archiver.sql_mws.catalia_status_db import CataliaStatusDb
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_fast_api.internal_ddb_connector import InternalDDBConnector
from cumulus_lambda_functions.lib.uds_fast_api.web_service_constants import WebServiceConstants
from cumulus_lambda_functions.lib.uds_fast_api.fast_api_utils import FastApiUtils
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional
from mdps_ds_lib.lib.aws.aws_lambda import AwsLambda

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

router = APIRouter(
    prefix=f'/{WebServiceConstants.COLLECTIONS}',
    tags=["Granules Archive CRUD API"],
    responses={404: {"description": "Not found"}},
)


class VerboseArchiveRequestModel(BaseModel):
    username: str
    algorithm_name: str
    algorithm_version: str
    stac_item: dict

class VerboseArchiveActualRequestModel(BaseModel):
    username: str  # TODO this is not mandatory if it comes from the archive_single_granule
    algorithm_name: str  # TODO this is not mandatory if it comes from the archive_single_granule
    algorithm_version: str  # TODO this is not mandatory if it comes from the archive_single_granule
    stac_item: dict
    sending_uuids: dict


@router.put("/{collection_id}/archive/{granule_id}")
@router.put("/{collection_id}/archive/{granule_id}/")
async def archive_single_granule(request: Request, collection_id: str, granule_id: str, response: Response):
    LOGGER.debug(f'started FAUX archive_single_granule.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.archiving_granules_stac = dac.retrieve_archiving_granule(collection_id, granule_id)
    sending_ids = dac.generate_sending_ids_dict()

    if os.getenv('IS_API_IN_DOCKER', 'FALSE') == 'TRUE':
        LOGGER.debug(f'In docker. No time limit for archiving')
        dac.archive_granule_json()
        return {'message': 'archive initiated', 'operation_ids': sending_ids}

    # Async invocation for API Gateway to avoid timeout
    archive_lambda_name = os.environ.get('ARCHIVE_LAMBDA_NAME', '').strip()
    if not archive_lambda_name:
        raise HTTPException(status_code=500, detail='ARCHIVE_LAMBDA_NAME environment variable not set')

    # TODO need to replace with verbose
    actual_path = f'{request.url.path}/actual' if not request.url.path.endswith('/') else f'{request.url.path}actual'

    # Extract the original authorizer context to forward it
    lambda_event = request.scope.get('aws.event', {})
    authorizer_context = lambda_event.get('requestContext', {}).get('authorizer', {})

    updated_request_body = {}
    updated_request_body['sending_uuids'] = dac.sending_uuids
    updated_request_body['stac_item'] = dac.archiving_granules_stac
    actual_event = {
        'resource': actual_path,
        'path': actual_path,
        'httpMethod': 'PUT',
        'headers': {
            **FastApiUtils.get_authorization_token(request),  # Forward all auth headers
            'Accept': '*/*',
            'Host': request.url.hostname,
        },
        'pathParameters': {
            'collection_id': collection_id,
            'granule_id': granule_id,
        },
        'requestContext': {
            'resourcePath': actual_path,
            'httpMethod': 'PUT',
            'domainName': request.url.hostname,
            'authorizer': authorizer_context,  # Forward the authorizer context
        },
        'body': json.dumps(updated_request_body),
        'isBase64Encoded': False
    }

    LOGGER.info(f'Invoking async lambda for archive: {archive_lambda_name} with operation_ids: {sending_ids}')
    response_lambda = AwsLambda().invoke_function(
        function_name=archive_lambda_name,
        payload=actual_event,
    )
    LOGGER.debug(f'Async archive function started: {response_lambda}')
    response.status_code = 202
    return {'message': 'archive processing', 'operation_ids': sending_ids}
@router.put("/{collection_id}/verbose_archive/{granule_id}")
@router.put("/{collection_id}/verbose_archive/{granule_id}/")
async def verbose_archive_single_granule(request: Request, collection_id: str, granule_id: str, item_s3_url: str, request_body: VerboseArchiveRequestModel, response: Response):
    LOGGER.debug(f'started verbose_archive_single_granule with item_s3_url: {item_s3_url}')
    LOGGER.debug(f'username: {request_body.username}, algorithm: {request_body.algorithm_name} v{request_body.algorithm_version}')

    # Validate item_s3_url
    if not item_s3_url:
        raise HTTPException(status_code=400, detail='item_s3_url parameter is required')

    if not item_s3_url.startswith('s3://') or len(item_s3_url.split('/')) < 4:
        raise HTTPException(status_code=400, detail='item_s3_url must be in the format s3://<bucket>/<path>')

    # Extract STAC item from request body
    stac_item = request_body.stac_item
    LOGGER.debug(f'Received STAC item JSON: {json.dumps(stac_item)}')

    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator_manual_algorithm(request_body.username, request_body.algorithm_name, request_body.algorithm_version, request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.tracing_s3_url = item_s3_url
    dac.archiving_granules_stac = request_body.stac_item
    sending_ids = dac.generate_sending_ids_dict()

    if os.getenv('IS_API_IN_DOCKER', 'FALSE') == 'TRUE':
        LOGGER.debug(f'In docker. No time limit for archiving')
        dac.archive_granule_json()
        return {'message': 'archive initiated', 'operation_id': sending_ids}

    # Async invocation for API Gateway to avoid timeout
    archive_lambda_name = os.environ.get('ARCHIVE_LAMBDA_NAME', '').strip()
    if not archive_lambda_name:
        raise HTTPException(status_code=500, detail='ARCHIVE_LAMBDA_NAME environment variable not set')

    actual_path = f'{request.url.path}/actual' if not request.url.path.endswith('/') else f'{request.url.path}actual'

    # Extract the original authorizer context to forward it
    lambda_event = request.scope.get('aws.event', {})
    authorizer_context = lambda_event.get('requestContext', {}).get('authorizer', {})

    updated_request_body = request_body.model_dump()
    updated_request_body['sending_uuids'] = dac.sending_uuids
    actual_event = {
        'resource': actual_path,
        'path': actual_path,
        'httpMethod': 'PUT',
        'headers': {
            **FastApiUtils.get_authorization_token(request),  # Forward all auth headers
            'Accept': '*/*',
            'Host': request.url.hostname,
        },
        'pathParameters': {
            'collection_id': collection_id,
            'granule_id': granule_id,
        },
        'queryStringParameters': {
            'item_s3_url': item_s3_url
        },
        'requestContext': {
            'resourcePath': actual_path,
            'httpMethod': 'PUT',
            'domainName': request.url.hostname,
            'authorizer': authorizer_context,  # Forward the authorizer context
        },
        'body': json.dumps(updated_request_body),
        'isBase64Encoded': False
    }

    LOGGER.info(f'Invoking async lambda for verbose archive: {archive_lambda_name} with operation_ids: {sending_ids}')
    response_lambda = AwsLambda().invoke_function(
        function_name=archive_lambda_name,
        payload=actual_event,
    )
    LOGGER.debug(f'Async verbose archive function started: {response_lambda}')
    response.status_code = 202
    return {'message': 'verbose archive processing', 'operation_ids': sending_ids}

@router.put("/{collection_id}/verbose_archive/{granule_id}/actual")
@router.put("/{collection_id}/verbose_archive/{granule_id}/actual/")
async def verbose_archive_single_granule_actual(request: Request, collection_id: str, granule_id: str, item_s3_url: str, request_body: VerboseArchiveActualRequestModel, response: Response):
    LOGGER.debug(f'started verbose_archive_single_granule_actual with item_s3_url: {item_s3_url}')
    LOGGER.debug(f'username: {request_body.username}, algorithm: {request_body.algorithm_name} v{request_body.algorithm_version}')
    LOGGER.debug(f'verbose_archive_single_granule_actual: {request_body.sending_uuids}')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator_manual_algorithm(request_body.username, request_body.algorithm_name, request_body.algorithm_version, request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.tracing_s3_url = item_s3_url
    dac.archiving_granules_stac = request_body.stac_item
    dac.sending_uuids = request_body.sending_uuids
    dac.archive_granule_json()

    return {'message': 'archive initiated'}

@router.put("/{collection_id}/archive")
@router.put("/{collection_id}/archive/")
async def archive_entire_collection(request: Request, collection_id: str, response: Response):
    LOGGER.debug(f'started archive_entire_collection.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    if os.getenv('IS_API_IN_DOCKER', 'FALSE') == 'TRUE':
        LOGGER.debug(f'In docker. No time limit for archiving collection')
        dac = DaacArchiverCatalia()
        dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
        dac.daac_agreements = authorized_configured_daac_configs
        dac.archive_collection(collection_id)
        return {'message': 'archive completed'}

    # Read Fargate configuration from SSM Parameter Store
    prefix = os.getenv('PREFIX', '')
    if not prefix:
        raise HTTPException(status_code=500, detail='PREFIX environment variable not set')

    ssm_parameter_name = os.getenv('FARGATE_CONFIG', 'MISSING-FARGATE_CONFIG-Pls-Provide')
    try:
        fargate_config = AwsParamStore().get_param(ssm_parameter_name)
        fargate_config = json.loads(fargate_config)
        LOGGER.debug(f'Retrieved Fargate config from SSM: {ssm_parameter_name}')
    except Exception as e:
        LOGGER.exception(f'Failed to retrieve Fargate config from SSM: {ssm_parameter_name}')
        raise HTTPException(
            status_code=500,
            detail=f'Failed to retrieve Fargate configuration from SSM: {str(e)}'
        )

    # Extract configuration from SSM
    try:
        ecs_cluster = fargate_config['CLUSTER_NAME']
        task_definition = fargate_config['TASK_DEFINITION']
        subnet_ids = fargate_config['SUBNET_IDs']
        security_group_ids = fargate_config['SECURITY_GROUPS']
        container_name = fargate_config['CONTAINER_NAME']
    except KeyError as e:
        LOGGER.error(f'Missing required key in Fargate config: {e}')
        raise HTTPException(
            status_code=500,
            detail=f'Invalid Fargate configuration in SSM, missing key: {str(e)}'
        )

    # Prepare environment variables for the Fargate task
    # These match what docker_entrypoint/__main__.py expects for CATALYA_COLLECTION_ARCHIVE
    container_overrides = {
        'environment': [
            {'name': 'CATALYA_UDS_STAGING_BUCKET', 'value': os.getenv('CATALYA_UDS_STAGING_BUCKET', '')},
            {'name': 'CATALYA_DAAC_CONFIGS', 'value': json.dumps(authorized_configured_daac_configs)},
            {'name': 'CATALYA_COLLECTION_ID', 'value': collection_id},
            {'name': 'LOG_LEVEL', 'value': os.getenv('LOG_LEVEL', '20')},
        ],
        'command': ['CATALYA_COLLECTION_ARCHIVE']  # This is passed as argv[1] to docker_entrypoint/__main__.py
    }

    try:
        ecs_client = boto3.client('ecs', region_name=os.getenv('AWS_REGION', 'us-west-2'))

        response_ecs = ecs_client.run_task(
            cluster=ecs_cluster,
            taskDefinition=task_definition,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': security_group_ids,
                    'assignPublicIp': 'ENABLED'  # May need to adjust based on your VPC setup
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': container_name,
                        **container_overrides
                    }
                ]
            }
        )

        task_arn = response_ecs['tasks'][0]['taskArn'] if response_ecs.get('tasks') else 'unknown'
        LOGGER.info(f'Started Fargate task for collection archiving: {task_arn}')

        response.status_code = 202
        return {
            'message': 'collection archive processing started',
            'task_arn': task_arn,
            'collection_id': collection_id
        }
    except Exception as e:
        LOGGER.exception(f'Failed to start Fargate task for collection archiving')
        raise HTTPException(status_code=500, detail=f'Failed to start Fargate task: {str(e)}')

@router.put("/{collection_id}/archive/actual")
@router.put("/{collection_id}/archive/actual/")
async def archive_entire_collection_actual(request: Request, collection_id: str):
    LOGGER.debug(f'started archive_entire_collection.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]
    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.archive_collection(collection_id)  # TODO accept filtering mechanisms?
    return {'message': 'archive initiated'}


@router.get("/{operation_id}")
@router.get("/{operation_id}/")
async def get_archive_status(request: Request, operation_id: str):
    LOGGER.debug(f'started get_archive_status with operation_id: {operation_id}')
    uds_api_creds = json.loads(AwsParamStore().get_param(os.getenv('CATALYA_RDS_CREDS', 'NA')))
    status_db = CataliaStatusDb(os.getenv('CATALYA_STATUS_DB'), uds_api_creds)
    existing_statuses = status_db.get(operation_id)
    if len(existing_statuses) < 1:
        raise HTTPException(status_code=404, detail=f'STATUS DB does not have any entry for {operation_id}')
    return {'status_list': existing_statuses}
