import json
import os
from typing import Optional
import boto3
from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore

from cumulus_lambda_functions.daac_archiver.catalia_auth_db import CataliaAuthDb
from cumulus_lambda_functions.daac_archiver.catalia_daac_handshakes_db import CataliaDaacHandshakesDb
from cumulus_lambda_functions.daac_archiver.daac_archiver_catalia import DaacArchiverCatalia
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.uds_api.web_service_constants import WebServiceConstants
from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from mdps_ds_lib.lib.aws.aws_lambda import AwsLambda

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

@router.put("/{collection_id}/archive/{granule_id}")
@router.put("/{collection_id}/archive/{granule_id}/")
async def archive_single_granule(request: Request, collection_id: str, granule_id: str, response: Response):
    LOGGER.debug(f'started FAUX archive_single_granule.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    if os.getenv('IS_API_IN_DOCKER', 'FALSE') == 'TRUE':
        LOGGER.debug(f'In docker. No time limit for archiving')
        dac = DaacArchiverCatalia()
        dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
        dac.daac_agreements = authorized_configured_daac_configs
        dac.archive_granule(collection_id, granule_id)
        return {'message': 'archive initiated'}

    # Async invocation for API Gateway to avoid timeout
    archive_lambda_name = os.environ.get('ARCHIVE_LAMBDA_NAME', '').strip()
    if not archive_lambda_name:
        raise HTTPException(status_code=500, detail='ARCHIVE_LAMBDA_NAME environment variable not set')

    bearer_token = request.headers.get('authorization', '')
    actual_path = f'{request.url.path}/actual' if not request.url.path.endswith('/') else f'{request.url.path}actual'

    actual_event = {
        'resource': actual_path,
        'path': actual_path,
        'httpMethod': 'PUT',
        'headers': {
            'Authorization': bearer_token,
            'Accept': '*/*',
            'Host': request.url.hostname,
        },
        'pathParameters': {
            'collection_id': collection_id,
            'granule_id': granule_id
        },
        'requestContext': {
            'resourcePath': actual_path,
            'httpMethod': 'PUT',
            'domainName': request.url.hostname,
        },
        'body': json.dumps({
            'authorized_configured_daac_configs': authorized_configured_daac_configs
        }),
        'isBase64Encoded': False
    }

    LOGGER.info(f'Invoking async lambda for archive: {archive_lambda_name}')
    response_lambda = AwsLambda().invoke_function(
        function_name=archive_lambda_name,
        payload=actual_event,
    )
    LOGGER.debug(f'Async archive function started: {response_lambda}')
    response.status_code = 202
    return {'message': 'archive processing'}

@router.put("/{collection_id}/verbose_archive/{granule_id}")
@router.put("/{collection_id}/verbose_archive/{granule_id}/")
async def verbose_archive_single_granule(request: Request, collection_id: str, granule_id: str, item_s3_url: str, stac_item: dict, response: Response):
    LOGGER.debug(f'started verbose_archive_single_granule with item_s3_url: {item_s3_url}')

    # Convert STAC item to JSON
    item_json = stac_item
    LOGGER.debug(f'Received STAC item JSON: {json.dumps(item_json)}')

    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]

    if os.getenv('IS_API_IN_DOCKER', 'FALSE') == 'TRUE':
        LOGGER.debug(f'In docker. No time limit for archiving')
        dac = DaacArchiverCatalia()
        dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
        dac.daac_agreements = authorized_configured_daac_configs
        dac.archive_granule(collection_id, granule_id)
        return {'message': 'archive initiated'}

    # Async invocation for API Gateway to avoid timeout
    archive_lambda_name = os.environ.get('ARCHIVE_LAMBDA_NAME', '').strip()
    if not archive_lambda_name:
        raise HTTPException(status_code=500, detail='ARCHIVE_LAMBDA_NAME environment variable not set')

    bearer_token = request.headers.get('authorization', '')
    actual_path = f'{request.url.path}/actual' if not request.url.path.endswith('/') else f'{request.url.path}actual'

    actual_event = {
        'resource': actual_path,
        'path': actual_path,
        'httpMethod': 'PUT',
        'headers': {
            'Authorization': bearer_token,
            'Accept': '*/*',
            'Host': request.url.hostname,
        },
        'pathParameters': {
            'collection_id': collection_id,
            'granule_id': granule_id
        },
        'requestContext': {
            'resourcePath': actual_path,
            'httpMethod': 'PUT',
            'domainName': request.url.hostname,
        },
        'body': json.dumps({
            'authorized_configured_daac_configs': authorized_configured_daac_configs
        }),
        'isBase64Encoded': False
    }

    LOGGER.info(f'Invoking async lambda for archive: {archive_lambda_name}')
    response_lambda = AwsLambda().invoke_function(
        function_name=archive_lambda_name,
        payload=actual_event,
    )
    LOGGER.debug(f'Async archive function started: {response_lambda}')
    response.status_code = 202
    return {'message': 'archive processing'}

@router.put("/{collection_id}/verbose_archive/{granule_id}/actual")
@router.put("/{collection_id}/verbose_archive/{granule_id}/actual/")
async def verbose_archive_single_granule_actual(request: Request, collection_id: str, granule_id: str, item_s3_url: str, stac_item: dict, response: Response):
    LOGGER.debug(f'started verbose_archive_single_granule_actual with item_s3_url: {item_s3_url}')
    # TODO stac_item is already a dict?
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]
    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.verbose_archive_granule(collection_id, granule_id, stac_item)
    return {'message': 'archive initiated'}

@router.put("/{collection_id}/archive/{granule_id}/actual")
@router.put("/{collection_id}/archive/{granule_id}/actual/")
async def archive_single_granule_actual(request: Request, collection_id: str, granule_id: str):
    LOGGER.debug(f'started archive_single_granule.')
    i1 = InternalDDBConnector()
    authorized_daacs = i1.archive_methods_initiator(request, collection_id, None)
    # authorized_ldaps = set([k['userGroup'] for k in authorized_daacs])
    authorized_configured_daac_configs = [k for k in i1.configured_daac_configs if k[i1.cdhsd.target_project] in authorized_daacs]
    dac = DaacArchiverCatalia()
    dac.staged_s3_bucket = os.getenv('CATALYA_UDS_STAGING_BUCKET')
    dac.daac_agreements = authorized_configured_daac_configs
    dac.archive_granule(collection_id, granule_id)
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
async def archive_entire_collection(request: Request, collection_id: str):
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
