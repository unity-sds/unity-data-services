import json
import os
from uuid import uuid4

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.aws.aws_sns import AwsSns
from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from cumulus_lambda_functions.daac_archiver.ddb_mws.catalia_archiving_traces import CataliaArchivingTraces
from cumulus_lambda_functions.daac_archiver.services.sfa_client_mw import SfaClientMw
from cumulus_lambda_functions.daac_archiver.services.staging_svc import StagingSvc
from cumulus_lambda_functions.daac_archiver.services.status_update_svc import StatusUpdateSvc
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_utils import backoff_wrapper

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class DaacArchiverCatalia:
    def __init__(self):
        self.__staging_service = StagingSvc()
        self.__sns = AwsSns()
        self.__s3 = AwsS3()
        self.__staged_s3_bucket = 'SET_ME_UP'  # DONE. There is validation to see if it's original value, it will throw an error.
        self.__uds_ctla_archiving_traces = CataliaArchivingTraces(os.getenv('CATALYA_TRACING_DB', None))
        self.__daac_agreements = []
        self.__update_status_to_sfa = os.getenv('UPDATE_STATUS_TO_SFA', 'FALSE').strip().upper() == 'TRUE'
        self.__archiving_granules_stac = None
        self.__archiving_status_extension_url = "https://stac-extensions.github.io/archival_statuses/v1.0.0/schema.json"
        self.__cnm_msg_version = "1.6.0"
        self.__tracing_s3_url = None

    @property
    def archiving_granules_stac(self):
        return self.__archiving_granules_stac

    @archiving_granules_stac.setter
    def archiving_granules_stac(self, val):
        """
        :param val:
        :return: None
        """
        self.__archiving_granules_stac = val
        return

    @property
    def staged_s3_bucket(self):
        return self.__staged_s3_bucket

    @staged_s3_bucket.setter
    def staged_s3_bucket(self, val):
        """
        :param val:
        :return: None
        """
        self.__staged_s3_bucket = val
        return

    @property
    def daac_agreements(self):
        return self.__daac_agreements

    @daac_agreements.setter
    def daac_agreements(self, val):
        """
        :param val:
        :return: None
        """
        self.__daac_agreements = val
        return

    def archive_collection(self, collection_id):
        """
        Archive all granules in a collection by querying the STAC Fast API
        and processing them in parallel.

        NOTE: TODO This will not work if there are too many granules..
        :param collection_id: The collection ID to archive all granules from
        :return: self
        """
        LOGGER.info(f'Starting collection archival for collection: {collection_id}')

        try:
            # Query all granules in the collection with pagination
            all_granule_jsons = []
            page = 1
            limit = 100  # Reasonable batch size
            sfa_client_mw = SfaClientMw()
            while True:
                LOGGER.debug(f'Fetching granules page {page} for collection {collection_id}')

                # Use backoff wrapper for STAC API call
                granules_response = backoff_wrapper(
                    sfa_client_mw.sfa_client.get_items,
                    collection_id=collection_id,
                    limit=limit,
                    offset=(page - 1) * limit
                )

                if not granules_response or 'features' not in granules_response:
                    LOGGER.warning(f'No granules found in response for collection {collection_id}, page {page}')
                    break

                granules = granules_response['features']
                if not granules:
                    LOGGER.info(f'No more granules found for collection {collection_id}, stopping pagination')
                    break

                all_granule_jsons.extend(granules)
                LOGGER.info(f'Fetched {len(granules)} granules from page {page}, total so far: {len(all_granule_jsons)}')

                # If we got fewer than the limit, we're done
                if len(granules) < limit:
                    break

                page += 1

            LOGGER.info(f'Found {len(all_granule_jsons)} total granules in collection {collection_id}')

            if not all_granule_jsons:
                LOGGER.warning(f'No granules found in collection {collection_id}')
                return self

            # Process all granules in parallel
            return self.archive_granules(all_granule_jsons)

        except Exception as e:
            LOGGER.error(f'Failed to archive collection {collection_id}: {e}')
            raise RuntimeError(f'Collection archival failed: {e}') from e

    def archive_granules(self, granule_jsons: list, max_workers=10):
        """
        Process multiple granules in parallel for archival.

        :param granule_jsons: List of granule JSON objects from STAC Fast API
        :param max_workers: Maximum number of parallel workers (default: 10)
        :return: self
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if not granule_jsons:
            LOGGER.warning('No granules provided for archival')
            return self

        LOGGER.info(f'Starting parallel archival of {len(granule_jsons)} granules with {max_workers} workers')

        # Track results
        successful_granules = []
        failed_granules = []

        def archive_single_granule(granule_json):
            """
            Archive a single granule - wrapper function for parallel execution.

            :param granule_json: Individual granule JSON object
            :return: tuple (granule_id, success, error_message)
            """
            granule_id = granule_json.get('id', 'unknown')
            collection_id = granule_json.get('collection', 'unknown')

            try:
                LOGGER.debug(f'Processing granule {granule_id} from collection {collection_id}')

                # Create a new instance for thread safety
                # Each worker gets its own archiver instance with same configuration
                worker_archiver = DaacArchiverCatalia()
                worker_archiver.staged_s3_bucket = self.__staged_s3_bucket
                worker_archiver.daac_agreements = self.__daac_agreements

                # Set the granule data directly instead of fetching again
                worker_archiver.archiving_granules_stac = granule_json

                # Process the granule
                worker_archiver.archive_granule_json()

                LOGGER.info(f'Successfully archived granule {granule_id}')
                return granule_id, True, None

            except Exception as e:
                error_msg = f'Failed to archive granule {granule_id}: {str(e)}'
                LOGGER.error(error_msg)
                return granule_id, False, error_msg

        # Execute parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_granule = {
                executor.submit(archive_single_granule, granule_json): granule_json.get('id', 'unknown')
                for granule_json in granule_jsons
            }

            # Process completed tasks
            for future in as_completed(future_to_granule):
                granule_id = future_to_granule[future]
                try:
                    result_granule_id, success, error_msg = future.result()

                    if success:
                        successful_granules.append(result_granule_id)
                    else:
                        failed_granules.append({'granule_id': result_granule_id, 'error': error_msg})

                except Exception as e:
                    error_msg = f'Unexpected error processing granule {granule_id}: {str(e)}'
                    LOGGER.error(error_msg)
                    failed_granules.append({'granule_id': granule_id, 'error': error_msg})

        # Log final results
        total_granules = len(granule_jsons)
        success_count = len(successful_granules)
        failed_count = len(failed_granules)

        LOGGER.info(f'Parallel archival completed: {success_count}/{total_granules} successful, {failed_count} failed')

        if failed_granules:
            LOGGER.warning(f'Failed granules: {[f["granule_id"] for f in failed_granules]}')
            for failure in failed_granules[:5]:  # Log first 5 failures in detail
                LOGGER.error(f'Failure details - {failure["granule_id"]}: {failure["error"]}')

        if successful_granules:
            LOGGER.debug(f'Successfully archived granules: {successful_granules[:10]}...')  # Log first 10

        return self

    def archive_granule(self, collection_id, granule_id):
        # TODO look up granule details
        sfa_client_mw = SfaClientMw()
        self.__archiving_granules_stac = backoff_wrapper(sfa_client_mw.sfa_client.get_item, collection_id, item_id=granule_id)
        LOGGER.debug(f'retrieved stac_item from STAC Fast API: {self.__archiving_granules_stac}')
        self.archive_granule_json()
        return self

    def verbose_archive_granule(self, collection_id, granule_id, tracing_s3_url, item_json: dict):
        # TODO validate item.json is valid or just ask for STAC Item object
        # TODO update collection and granule id in item.json if different. Needed ??
        LOGGER.debug(f'verbose_archive_granule input item_json: {item_json}')
        self.__tracing_s3_url = tracing_s3_url
        self.__archiving_granules_stac = item_json
        self.archive_granule_json()
        return self

    def archive_granule_json(self):
        """
        1. Check UDS API if this granule is being pushed to archive(s)
        2. Copy Data and Metadata to staging bucket
        3. Update STAC Metadata to staging bucket. + Re-upload.
        4. Send message to DAAC SNS

        :param stac_granule_json:
        :return:
        """
        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Pls retrieve it first.')
        self.archiving_granules_stac = SfaClientMw.add_archival_extension(self.archiving_granules_stac)
        if len(self.__daac_agreements) < 1:
            LOGGER.debug(f'this collection does not have any daac. {self.__archiving_granules_stac}')
            return
        self.__staging_service.staged_s3_bucket = self.staged_s3_bucket
        self.__staging_service.stage_files(self.archiving_granules_stac)
        for each_agreement in self.__daac_agreements:
            LOGGER.debug(f'working on {each_agreement}')
            self.send_daac_sns(each_agreement)
        return

    def extract_files(self, daac_config: dict):
        """
        Extract files from STAC assets and convert to CNM file format.

        This method has been updated to work with STAC assets instead of CNM JSON.
        It extracts files from self.__archiving_granules_stac.assets and converts them
        to the CNM file format expected by DAAC.

        Old CNM JSON structure:
        {
            "product: {
                "files": [
                    {
                        "type": "data",
                        "name": "cc_file.pdf",
                        "uri": "s3://bucket/path/cc_file.pdf",
                        "checksumType": "md5",
                        "checksum": "deb1087d3e614f31b7c9eb461edea93a",
                        "size": 1579135
                    },
                ]
            }
        }

        STAC assets structure:
        {
                "assets": {
                    "cc_file.pdf": {
                        "href": "s3://bucket/path/cc_file.pdf",
                        "title": "cc_file.pdf",
                        "description": "size=1579135;checksumType=md5;checksum=deb1087d3e614f31b7c9eb461edea93a",
                        "file:size": 1579135,
                        "file:checksum": "deb1087d3e614f31b7c9eb461edea93a",
                        "roles": [
                            "data"
                        ]
                    },
                }
        }

        :param daac_config: DAAC configuration containing archiving_types
        :return: List of files in CNM format
        """
        if self.__archiving_granules_stac is None:
            raise ValueError('NULL archiving granule. Cannot extract files.')

        # Get assets from STAC item
        stac_assets = self.__archiving_granules_stac.assets

        # If no archiving types specified, include all assets
        if 'archiving_types' not in daac_config or len(daac_config['archiving_types']) < 1:
            LOGGER.debug('No archiving types specified in DAAC config, including all assets')
            return self._convert_all_assets_to_cnm_format(stac_assets)

        # Build archiving types mapping: {data_type: [file_extensions]}
        archiving_types = {}
        for archiving_type in daac_config['archiving_types']:
            data_type = archiving_type['data_type']
            file_extensions = archiving_type.get('file_extension', [])
            if not isinstance(file_extensions, list):
                file_extensions = [file_extensions] if file_extensions else []
            archiving_types[data_type] = file_extensions

        LOGGER.debug(f'Archiving types configuration: {archiving_types}')

        result_files = []
        for asset_key, asset in stac_assets.items():
            LOGGER.debug(f'Processing asset: {asset_key}')

            # Get asset type from roles (use first role as type, default to 'data')
            asset_type = 'data'  # Default type
            if hasattr(asset, 'roles') and asset.roles and len(asset.roles) > 0:
                asset_type = asset.roles[0]

            # Check if this asset type should be archived
            if asset_type not in archiving_types:
                LOGGER.debug(f'Asset {asset_key} type "{asset_type}" not in archiving types, skipping')
                continue

            # Get file extensions for this asset type
            file_extensions = archiving_types[asset_type]

            # Convert STAC asset to CNM file format
            cnm_file = self._convert_stac_asset_to_cnm_file(asset_key, asset)

            # If no file extensions specified for this type, include the file
            if len(file_extensions) == 0:
                LOGGER.debug(f'No file extensions specified for type "{asset_type}", including asset {asset_key}')
                result_files.append(cnm_file)
                continue

            # Check if file matches any of the specified extensions
            filename = cnm_file['name'].upper().strip()
            if any(filename.endswith(ext.upper()) for ext in file_extensions):
                LOGGER.debug(f'Asset {asset_key} matches extension filter, including')
                result_files.append(cnm_file)
            else:
                LOGGER.debug(f'Asset {asset_key} does not match extension filter {file_extensions}, skipping')

        LOGGER.info(f'Extracted {len(result_files)} files from {len(stac_assets)} STAC assets')
        return result_files

    def _convert_all_assets_to_cnm_format(self, stac_assets: dict):
        """Convert all STAC assets to CNM file format without filtering."""
        result_files = []
        for asset_key, asset in stac_assets.items():
            cnm_file = self._convert_stac_asset_to_cnm_file(asset_key, asset)
            result_files.append(cnm_file)
        return result_files

    def _convert_stac_asset_to_cnm_file(self, asset_key: str, asset):
        """
        Convert a single STAC asset to CNM file format.

        :param asset_key: The key/name of the asset in STAC
        :param asset: The STAC Asset object
        :return: Dictionary in CNM file format
        """
        # Extract filename from href or use asset_key
        filename = asset_key
        if hasattr(asset, 'href') and asset.href:
            filename = asset.href.split('/')[-1]

        # Get asset type from roles (use first role, default to 'data')
        asset_type = 'data'
        if hasattr(asset, 'roles') and asset.roles and len(asset.roles) > 0:
            asset_type = asset.roles[0]

        # Get file size
        file_size = -1
        if hasattr(asset, 'extra_fields') and 'file:size' in asset.extra_fields:
            file_size = asset.extra_fields['file:size']
        elif hasattr(asset, 'extra_fields') and 'file_size' in asset.extra_fields:
            file_size = asset.extra_fields['file_size']

        # Get checksum information
        checksum_type = 'md5'  # Default
        checksum_value = 'unknown'  # Default

        if hasattr(asset, 'extra_fields'):
            if 'file:checksum' in asset.extra_fields:
                checksum_value = asset.extra_fields['file:checksum']
            elif 'file_checksum' in asset.extra_fields:
                checksum_value = asset.extra_fields['file_checksum']

        # Try to parse checksum info from description if available
        if hasattr(asset, 'description') and asset.description:
            desc = asset.description.lower()
            if 'checksumtype=' in desc:
                # Parse description like "size=1579135;checksumType=md5;checksum=deb1087d3e614f31b7c9eb461edea93a"
                parts = desc.split(';')
                for part in parts:
                    if part.startswith('checksumtype='):
                        checksum_type = part.split('=')[1]
                    elif part.startswith('checksum='):
                        checksum_value = part.split('=')[1]
                    elif part.startswith('size=') and file_size == -1:
                        try:
                            file_size = int(part.split('=')[1])
                        except ValueError:
                            pass

        # Build CNM file structure
        cnm_file = {
            "type": asset_type,
            "name": filename,
            "uri": asset.href if hasattr(asset, 'href') else '',
            "checksumType": checksum_type,
            "checksum": checksum_value,
            "size": file_size
        }

        LOGGER.debug(f'Converted STAC asset {asset_key} to CNM file: {cnm_file}')
        return cnm_file

    def send_daac_sns(self, daac_config):
        """

        {
            "product": {
              "files": [
                {
                    "name":"TROPESS_CrIS-JPSS1_L2_Standard_CH4_20250108_MUSES_R1p23_megacity_los_angeles_MGLOS_F2p5_J0.nc",
                    "type":"data",
                    "uri":"s3://unity-test-unity-storage/URN:NASA:UNITY:unity:test:TRPSDL2ALLCRS1MGLOS___2/URN:NASA:UNITY:unity:test:TRPSDL2ALLCRS1MGLOS___2:datum/TROPESS_Standard/TRPSDL2ALLCRS1MGLOS.2/2025/01/08/TROPESS_CrIS-JPSS1_L2_Standard_CH4_20250108_MUSES_R1p23_megacity_los_angeles_MGLOS_F2p5_J0/TROPESS_CrIS-JPSS1_L2_Standard_CH4_20250108_MUSES_R1p23_megacity_los_angeles_MGLOS_F2p5_J0.nc",
                    "size":280595
                 }
              ],
              "name": "TROPESS_CrIS-JPSS1_L2_Standard_CH4_20250108_MUSES_R1p23_megacity_los_angeles_MGLOS_F2p5_J0"
            },
            "identifier ":"testIdentifier123456",
            "collection": {
                "name": "TRPSDL2ALLCRS1MGLOS",
                "version": "2"
            },
            "provider":"tropess_testing"
        }
        :param daac_config:
        :return:
        """
        sending_uuid = str(uuid4())
        update_status_svc = StatusUpdateSvc()\
            .load_manually(sending_uuid, self.__archiving_granules_stac.collection_id, self.__archiving_granules_stac.id)
        try:
            LOGGER.debug(f'send_daac_sns daac_config: {daac_config}')
            self.__sns.set_topic_arn(daac_config['sns_topic_arn'])
            # TODO store details to new DB.
            if self.__tracing_s3_url is not None:
                self.__uds_ctla_archiving_traces.add(sending_uuid, self.__tracing_s3_url, 'TODO', ['TODO'],
                                                     self.__archiving_granules_stac.collection_id, self.__archiving_granules_stac.id, TimeUtils().get_datetime_str())
            daac_cnm_message = {
                "collection": {
                    'name': daac_config['targetProject'],
                    'version': daac_config['data_version'],
                },
                'identifier': sending_uuid,  # "identifier": self.__archiving_granules_stac.id,  # Seems like it's the same granule IDuds_cnm_json['identifier'],
                # From DAAC: Unique identifier for the message as a whole. It is the senders responsibility to ensure uniqueness. This identifier can be used in response messages to provide tracability.
                "submissionTime": f'{TimeUtils.get_current_time()}Z',
                "provider": daac_config['provider'],  # NOTE: we can't use tenant as provider anymore coz we aren't sure tennt will be there in CATALIA. if 'daac_provider' in daac_config else granule_identifier.tenant
                "version": self.__cnm_msg_version,
                "product": {
                    "name": self.__archiving_granules_stac.id,  # NOTE: Original value = granule_identifier.granule. Should be the name of granule.
                    # "dataVersion": daac_config['daac_data_version'],
                    'files': self.extract_files(daac_config),
                }
            }
            LOGGER.debug(f'daac_cnm_message: {daac_cnm_message}')
            if 'role_arn' in daac_config and \
                'role_session_name' in daac_config and \
                daac_config['role_arn'] != '' and \
                daac_config['role_session_name'] != '':
                self.__sns.set_external_role(daac_config['role_arn'], daac_config['role_session_name']).publish_message(json.dumps(daac_cnm_message), True)
            else:
                self.__sns.publish_message(json.dumps(daac_cnm_message), False)

            update_status_svc.update_status({
                "status": "cnm-submit-success",
            })
        except Exception as e:
            LOGGER.exception(f'failed during archival process')
            update_status_svc.update_status(sending_uuid, {
                "status": "cnm-submit-failed",
                "errorMessage": str(e),
            })
        return
