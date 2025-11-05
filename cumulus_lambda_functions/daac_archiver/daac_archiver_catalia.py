import json
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.aws.aws_sns import AwsSns
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stac_fast_api_client.sfa_client_factory import SFAClientFactory
from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils
from pystac import Item

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class DaacArchiverCatalia:
    archival_status_schema = {
      "type": "object",
      "required": [
        "status"
      ],
      "properties": {
        "status": {
          "type": "string",
          "enum": [
            "cnm-authorized-success",
            "cnm-authorized-failed",
            "cnm-staged-success",
            "cnm-staged-failed",
            "cnm-submit-success",
            "cnm-submit-failed",
            "cnm-receive-success",
            "cnm-receive-failed"
          ]
        },
        "errorCode": {
          "type": "string"
        },
        "errorMessage": {
          "type": "string"
        },
        "href": {
          "type": "string",
          "format": "iri-reference"
        },
          "datetime": {
              "title": "Date and Time",
              "description": "timestamp of this update, in UTC (Formatted in RFC 3339) ",
              "type": "string",
              "format": "date-time",
              "pattern": "(\\+00:00|Z)$"
          }
      },
      "additionalProperties": False
    }
    def __init__(self):
        self.__sns = AwsSns()
        self.__s3 = AwsS3()
        self.__staged_s3_bucket = 'TODO'  # TODO
        self.__sfa_client = SFAClientFactory().get_instance_from_env()
        self.__archiving_granules_stac = None
        self.__archiving_status_extension_url = "https://stac-extensions.github.io/archival_statuses/v1.0.0/schema.json"
        self.__cnm_msg_version = "1.6.0"
        self.__daac_agreements = []

    def archive_granule(self, collection_id, granule_id):
        # TODO look up granule details
        self.__archiving_granules_stac = self.__sfa_client.get_item(collection_id, item_id=granule_id)
        LOGGER.debug(f'retrieved stac_item from STAC Fast API: {self.__archiving_granules_stac}')
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
        self.add_archival_extension()
        self.get_daac_configs()
        if len(self.__daac_agreements) < 1:
            LOGGER.debug(f'this collection does not have any daac. {self.__archiving_granules_stac}')
            return
        self.stage_files()
        for each_agreement in self.__daac_agreements:
            LOGGER.debug(f'working on {each_agreement}')
            self.send_daac_sns(each_agreement)
        return

    def add_archival_extension(self):
        """
        1. Convert dictionary to pystac object. store the modified object back to the self.__archiving_granules_stac
        2. Check if it has a stac_extensions, and it has self.__archiving_status_extension_url
        3. If so, done
        4. If not, add that extension, done

        :return:
        """
        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot add archival extension.')

        # Convert to pystac Item if it's a dictionary
        if isinstance(self.__archiving_granules_stac, dict):
            self.__archiving_granules_stac = Item.from_dict(self.__archiving_granules_stac)

        # Check if the archival extension is already present
        if hasattr(self.__archiving_granules_stac, 'stac_extensions'):
            if self.__archiving_status_extension_url not in self.__archiving_granules_stac.stac_extensions:
                self.__archiving_granules_stac.stac_extensions.append(self.__archiving_status_extension_url)
                LOGGER.debug(f'Added archival extension to STAC item: {self.__archiving_status_extension_url}')
        else:
            # Initialize stac_extensions if it doesn't exist
            self.__archiving_granules_stac.stac_extensions = [self.__archiving_status_extension_url]
            LOGGER.debug(f'Initialized stac_extensions with archival extension: {self.__archiving_status_extension_url}')

        # Initialize archival:status property if it doesn't exist
        if 'archival:status' not in self.__archiving_granules_stac.properties:
            self.__archiving_granules_stac.properties['archival:status'] = []
            LOGGER.debug(f'Initialized archival:status property for STAC item')
        return self

    def get_daac_configs(self):
        # TODO
        # update self.__daac_agreements
        return

    def stage_files(self):
        """
        1. Check directory s3://<self.__staged_s3_bucket>/<collection-id>/<item-id>
        2. If not empty. log a warning message.
        3. Empty S3 directory
        4. Get file locations for each asset in self.__archiving_granules_stac which should be a pystac object.
        5. Copy them from source S3 to destination S3 from Step 1.
        6. After each copy, update the href of each asset to new location.
        7. If pystac is part of the assets, change its href to new location as well and upload it.
        8. How do I know if pystac is part of assets?
        :return:
        """
        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot stage files.')

        if self.__staged_s3_bucket == 'TODO':
            raise ValueError(f'Staged S3 bucket is not configured. Please set self.__staged_s3_bucket.')

        # Get collection and item IDs
        collection_id = self.__archiving_granules_stac.collection_id
        item_id = self.__archiving_granules_stac.id

        # Define staging directory path
        staging_prefix = f"{collection_id}/{item_id}/{TimeUtils.get_current_time()}/"
        staging_s3_path = f"s3://{self.__staged_s3_bucket}/{staging_prefix}"
        LOGGER.info(f'Staging files to: {staging_s3_path}')

        # Process each asset in the STAC item
        staged_assets = {}
        for asset_key, asset in self.__archiving_granules_stac.assets.items():
            if hasattr(asset, 'href') and asset.href:
                source_href = asset.href
                LOGGER.debug(f'Processing asset {asset_key} from {source_href}')

                # Parse S3 URL to get bucket and key
                if source_href.startswith('s3://'):
                    # Remove s3:// prefix and split
                    s3_path = source_href[5:]
                    bucket_key_parts = s3_path.split('/', 1)
                    if len(bucket_key_parts) == 2:
                        source_bucket, source_key = bucket_key_parts

                        # Define destination key (preserve original filename)
                        filename = source_key.split('/')[-1]
                        dest_key = f"{staging_prefix}{filename}"
                        dest_href = f"s3://{self.__staged_s3_bucket}/{dest_key}"

                        try:
                            # Copy file to staging bucket
                            self.__s3.copy_artifact(source_bucket, source_key, self.__staged_s3_bucket, dest_key, copy_tags=False, delete_original=False)
                            LOGGER.info(f'Copied {source_href} to {dest_href}')

                            # Update asset href to new location
                            asset.href = dest_href
                            staged_assets[asset_key] = dest_href

                        except Exception as e:
                            LOGGER.error(f'Failed to copy asset {asset_key} from {source_href} to {dest_href}: {e}')
                            raise
                    else:
                        LOGGER.warning(f'Invalid S3 URL format for asset {asset_key}: {source_href}')
                else:
                    LOGGER.warning(f'Non-S3 asset {asset_key} not staged: {source_href}')
        return self

    def update_status(self, archival_status: dict):
        """
        1. validate archival_status from parameter against self.archival_status_schema
        2. Add archival_status to self.__archiving_granules_stac>properties>archival:status
        3. get collection and item id from  self.__archiving_granules_stac
        4. convert self.__archiving_granules_stac to a json
        5. call self.__sfa_client.update_item()  # Note partial may not be available. Just update whole for now.
        :param archival_status:
        :return:
        """
        import jsonschema
        from datetime import datetime

        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot update status.')

        if not isinstance(archival_status, dict):
            raise ValueError(f'archival_status must be a dictionary, got {type(archival_status)}')

        # Validate archival_status against schema
        try:
            jsonschema.validate(archival_status, self.archival_status_schema)
            LOGGER.debug(f'archival_status validation successful: {archival_status}')
        except jsonschema.ValidationError as e:
            LOGGER.error(f'archival_status validation failed: {e}')
            raise ValueError(f'Invalid archival_status format: {e.message}')

        # Add timestamp to the status
        archival_status_with_timestamp = archival_status.copy()
        archival_status_with_timestamp['datetime'] = f'{TimeUtils.get_current_time()}Z'

        # Ensure archival:status property exists and is a list
        if 'archival:status' not in self.__archiving_granules_stac.properties:
            self.__archiving_granules_stac.properties['archival:status'] = []
        elif not isinstance(self.__archiving_granules_stac.properties['archival:status'], list):
            self.__archiving_granules_stac.properties['archival:status'] = []

        # Add the new status to the list
        self.__archiving_granules_stac.properties['archival:status'].append(archival_status_with_timestamp)
        LOGGER.info(f'Added archival status: {archival_status_with_timestamp}')

        # Get collection and item IDs
        collection_id = self.__archiving_granules_stac.collection_id
        item_id = self.__archiving_granules_stac.id

        if not collection_id or not item_id:
            raise ValueError(f'Missing collection_id or item_id from STAC item. collection_id: {collection_id}, item_id: {item_id}')

        try:
            # Convert STAC item to JSON dictionary
            stac_item_dict = self.__archiving_granules_stac.to_dict()

            # Update the item using the STAC Fast API client
            updated_item = self.__sfa_client.update_item(
                collection_id=collection_id,
                item_id=item_id,
                item=stac_item_dict
            )

            LOGGER.info(f'Successfully updated STAC item {item_id} in collection {collection_id} with new archival status')
            LOGGER.debug(f'Updated item response: {updated_item}')

            return self

        except Exception as e:
            LOGGER.error(f'Failed to update STAC item {item_id} in collection {collection_id}: {e}')
            raise RuntimeError(f'Failed to update STAC item status: {e}') from e

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
        try:
            self.__sns.set_topic_arn(daac_config['daac_sns_topic_arn'])
            daac_cnm_message = {
                "collection": {
                    'name': daac_config['daac_collection_name'],
                    'version': daac_config['daac_data_version'],
                },
                "identifier": self.__archiving_granules_stac.id,  # Seems like it's the same granule IDuds_cnm_json['identifier'],
                "submissionTime": f'{TimeUtils.get_current_time()}Z',
                "provider": daac_config['daac_provider'],  # NOTE: we can't use tenant as provider anymore coz we aren't sure tennt will be there in CATALIA. if 'daac_provider' in daac_config else granule_identifier.tenant
                "version": self.__cnm_msg_version,
                "product": {
                    "name": self.__archiving_granules_stac.id,  # NOTE: Original value = granule_identifier.granule. Should be the name of granule.
                    # "dataVersion": daac_config['daac_data_version'],
                    'files': self.extract_files(daac_config),
                }
            }
            LOGGER.debug(f'daac_cnm_message: {daac_cnm_message}')
            self.__sns.set_external_role(daac_config['daac_role_arn'], daac_config['daac_role_session_name']).publish_message(json.dumps(daac_cnm_message), True)
            self.update_status({
                "status": "cnm-submit-success",
            })
        except Exception as e:
            LOGGER.exception(f'failed during archival process')
            self.update_status({
                "status": "cnm-submit-failed",
                "errorMessage": str(e),
            })
        return
