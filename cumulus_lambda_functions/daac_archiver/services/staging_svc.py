from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from pystac import Item

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_utils import backoff_wrapper

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class StagingSvc:
    SET_ME_UP = 'SET_ME_UP'

    def __init__(self):
        self.__s3 = AwsS3()
        self.__archiving_granules_stac = None
        self.__staged_s3_bucket = self.SET_ME_UP  # DONE. There is validation to see if it's original value, it will throw an error.
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

    def stage_files(self, archiving_granules_stac: Item):
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
        self.__archiving_granules_stac = archiving_granules_stac

        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot stage files.')

        if self.__staged_s3_bucket == self.SET_ME_UP:
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
                            backoff_wrapper(self.__s3.copy_artifact, source_bucket, source_key, self.__staged_s3_bucket, dest_key, copy_tags=False, delete_original=False)
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
