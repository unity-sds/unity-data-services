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
        self.__archiving_status_extension_url = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
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
        staging_prefix = f"{collection_id}/{item_id}/"
        staging_s3_path = f"s3://{self.__staged_s3_bucket}/{staging_prefix}"

        LOGGER.info(f'Staging files to: {staging_s3_path}')

        # Check if staging directory exists and has content
        try:
            existing_objects = list(self.__s3.get_child_s3_files(self.__staged_s3_bucket, staging_prefix))
            if existing_objects:
                LOGGER.warning(f'Staging directory {staging_s3_path} is not empty. Found {len(existing_objects)} objects. Cleaning up...')
                # Empty the staging directory using delete_multiple in chunks
                object_keys = [obj_key for obj_key, obj_size in existing_objects]  # Extract just the keys from (key, size) tuples

                # Delete in chunks to avoid overwhelming S3 delete API
                for chunk in StageInOutUtils.chunk_list(object_keys, 50):
                    try:
                        self.__s3.delete_multiple(s3_bucket=self.__staged_s3_bucket, s3_paths=chunk)
                        LOGGER.debug(f'Removed {len(chunk)} objects from staging directory')
                    except Exception as chunk_e:
                        LOGGER.error(f'Failed to delete chunk of objects: {chunk_e}')
                        raise
                LOGGER.info(f'Successfully cleaned up {len(object_keys)} objects from staging directory')
        except Exception as e:
            LOGGER.debug(f'No existing objects found in staging directory or error checking: {e}')

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

        # Check if there's a STAC metadata file in assets and handle it
        stac_metadata_key = None
        for asset_key, asset in self.__archiving_granules_stac.assets.items():
            if asset_key.lower() in ['metadata', 'stac', 'item'] or asset.href.endswith('.json'):
                stac_metadata_key = asset_key
                break

        # Upload the updated STAC item to staging area
        stac_filename = f"{item_id}.json"
        stac_dest_key = f"{staging_prefix}{stac_filename}"
        stac_dest_href = f"s3://{self.__staged_s3_bucket}/{stac_dest_key}"

        try:
            # Convert STAC item to JSON and upload
            stac_json = self.__archiving_granules_stac.to_dict()
            self.__s3.set_s3_url(f's3://{self.__staged_s3_bucket}/{stac_dest_key}').upload_bytes(
                bytes(str(stac_json).encode('utf-8')),
                content_type='application/json'
            )
            LOGGER.info(f'Uploaded updated STAC metadata to {stac_dest_href}')

            # Update or add STAC metadata asset reference
            if stac_metadata_key:
                self.__archiving_granules_stac.assets[stac_metadata_key].href = stac_dest_href
            else:
                # Add new asset for STAC metadata
                from pystac import Asset
                self.__archiving_granules_stac.add_asset(
                    'stac-metadata',
                    Asset(href=stac_dest_href, media_type='application/json', title='STAC Metadata')
                )

        except Exception as e:
            LOGGER.error(f'Failed to upload STAC metadata to {stac_dest_href}: {e}')
            raise

        LOGGER.info(f'Successfully staged {len(staged_assets)} assets for granule {item_id}')
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

    def send_daac_sns(self, daac_config):
        try:
            self.__sns.set_topic_arn(daac_config['daac_sns_topic_arn'])
            daac_cnm_message = {
                "collection": {
                    'name': daac_config['daac_collection_name'],
                    'version': daac_config['daac_data_version'],
                },
                "identifier": uds_cnm_json['identifier'],
                "submissionTime": f'{TimeUtils.get_current_time()}Z',
                "provider": daac_config['daac_provider'] if 'daac_provider' in daac_config else granule_identifier.tenant,
                "version": "1.6.0",  # TODO this is hardcoded?
                "product": {
                    "name": granule_identifier.granule,
                    # "dataVersion": daac_config['daac_data_version'],
                    'files': self.__extract_files(uds_cnm_json, daac_config),
                }
            }
            LOGGER.debug(f'daac_cnm_message: {daac_cnm_message}')
            self.__sns.set_external_role(daac_config['daac_role_arn'], daac_config['daac_role_session_name']).publish_message(json.dumps(daac_cnm_message), True)
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_success',
                'archive_error_message': '',
                'archive_error_code': '',
            }, uds_cnm_json['identifier'])
        except Exception as e:
            LOGGER.exception(f'failed during archival process')
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_failed',
                'archive_error_message': str(e),
            }, uds_cnm_json['identifier'])

        return
