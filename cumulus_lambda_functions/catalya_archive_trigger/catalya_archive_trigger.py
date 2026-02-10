import os
import json
from urllib.parse import urlparse
import requests
from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from pystac import Item, Catalog, Collection

from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CatalyaArchiveTrigger:
    def __init__(self):
        self.__s3 = AwsS3()
        self.__ssm = AwsParamStore()
        self.__uds_api_creds_key = os.getenv('UDS_API_CREDS', '')

    def retrieve_all_stac_items(self, stac_catalog: dict, catalog_s3_url: str):
        catalog_dir = os.path.dirname(catalog_s3_url)
        LOGGER.debug(f"catalog S3 Dir: {catalog_dir}")

        catalog = Catalog.from_dict(stac_catalog)
        LOGGER.info(f"Successfully parsed STAC catalog: {catalog.id}")

        # Extract STAC Items from the catalog (including items from collections)
        item_links = []

        # Get all child links from catalog
        all_links = [k for k in catalog.get_links() if k.rel in ['item', 'child', 'collection'] and not k.target.startswith('http')]
        LOGGER.info(f"Found {len(all_links)} total eligible links in catalog")
        for each in all_links:
            if os.path.isabs(each.target):
                continue
            each.target = os.path.join(catalog_dir, each.target)

        for link in all_links:
            # Check if link exists locally
            b, p = self.__s3.split_s3_url(link.target)
            if not self.__s3.exists(b, p):
                LOGGER.warning(f"Local link file not found: {link.target}")
                continue

            # Handle different link types
            if link.rel == 'item':
                # Direct item link
                item_links.append(link.target)
                LOGGER.info(f"Found item link: {link.target}")
            elif link.rel == 'child' or link.rel == 'collection':
                # Collection link - read collection and extract items
                try:
                    collection = self.__s3.set_s3_url(link.target).read_small_txt_file()
                    collection = Collection.from_dict(collection)
                    collection_item_links = list(collection.get_item_links())
                    collection_folder = os.path.dirname(link.target)
                    temp_item_links = [k.target for k in collection.get_links() if
                                       k.rel in ['item'] and not k.target.startswith('http')]
                    for each in temp_item_links:
                        if os.path.isabs(each):
                            continue
                        each.target = os.path.join(collection_folder, each)
                    item_links.extend(temp_item_links)
                    LOGGER.info(
                        f"Found collection '{collection.id}' with {len(collection_item_links)} items: {link.target}")
                except Exception as e:
                    LOGGER.warning(f"Failed to process collection link '{link.target}': {str(e)}")
                    continue
            else:
                # Other link types - log and ignore
                LOGGER.info(f"Ignoring link of type '{link.rel}': {link.target}")
        return list(set(item_links))


    def retrieve_items(self, item_urls: list):
        """
        Process a list of STAC item S3 URLs by downloading, parsing, and updating asset URLs.

        :param item_urls: List of S3 URLs (as strings or link objects with .target attribute) pointing to STAC item JSON files
        :return: Dictionary mapping S3 URL to processed STAC item dictionary
        """
        processed_items = {}

        for item_url_obj in item_urls:
            # Handle both string URLs and link objects
            item_s3_url = item_url_obj.target if hasattr(item_url_obj, 'target') else item_url_obj

            try:
                LOGGER.info(f'Processing STAC item: {item_s3_url}')

                # Download and parse STAC item
                item_content = self.__s3.set_s3_url(item_s3_url).read_small_txt_file()
                item_dict = json.loads(item_content)

                # Convert to pystac Item object
                stac_item = Item.from_dict(item_dict)
                if stac_item.collection_id is None or stac_item.collection_id == '':
                    LOGGER.warning(f'Missing collection_id for {item_s3_url}, skipping')
                    continue

                granule_id = stac_item.id
                LOGGER.debug(f'Downloaded STAC item: {granule_id}')

                # Convert relative asset URLs to absolute S3 URLs and verify they exist
                parsed_item_url = urlparse(item_s3_url)
                item_bucket = parsed_item_url.netloc
                item_path_parts = parsed_item_url.path.rsplit('/', 1)
                item_base_path = item_path_parts[0] if len(item_path_parts) > 1 else ''

                for asset_key, asset in stac_item.assets.items():
                    asset_href = asset.href

                    # If href is relative, convert to absolute S3 URL
                    if not asset_href.startswith('s3://') and not asset_href.startswith('http'):
                        # Remove leading ./ or /
                        asset_href = asset_href.lstrip('./')
                        absolute_s3_url = f's3://{item_bucket}{item_base_path}/{asset_href}'
                        LOGGER.debug(f'Converted relative URL {asset.href} to absolute: {absolute_s3_url}')
                        asset.href = absolute_s3_url

                    # Verify the S3 URL exists
                    if asset.href.startswith('s3://'):
                        bucket, path = self.__s3.split_s3_url(asset.href)
                        if not self.__s3.exists(bucket, path):
                            raise FileNotFoundError(f'Asset does not exist at S3 URL: {asset.href}')
                        LOGGER.debug(f'Verified asset exists: {asset.href}')

                # Store the updated item dictionary
                processed_items[item_s3_url] = stac_item.to_dict()
                LOGGER.info(f'Successfully processed STAC item: {granule_id}')

            except Exception as e:
                LOGGER.exception(f'Error processing STAC item {item_s3_url}: {str(e)}')
                raise

        LOGGER.info(f'Processed {len(processed_items)} STAC items')
        return processed_items

    def start_with_event(self, event: dict):
        result = AwsMessageTransformers().sqs_sns(event)
        result1 = AwsMessageTransformers().get_s3_from_sns(result)
        return self.start(f's3://{result1["bucket"]}/{result1["key"]}')

    def start(self, catalog_s3_url):
        """
        Steps:
        1. You will be given an S3 URL.
        Make sure it is an S3 URL.
        2. Download that catalog.json
        3. Call retrieve_all_stac_items with the downloaded dictionary.
        4. How they are retrieved will be abstracted.
            The return will be a set or dictionary of item S3 URLs
        5. For each STAC item, download them, and convert them to a STAC Item object.
        6. for each asset, they will be relative URLs.
            Convert them to S3 URL based on the item.json S3 URL where current folder is <bucket>/<path>/item.json
            Ensure those S3 URLs exist along the way.
            Throw an exception to quit for now.. we'll revisit later.
        7. from ssm, retrieve __uds_api_creds_key.
        8. For each, use the UDS_API_CRED to call this method
            @router.put("/{collection_id}/verbose_archive/{granule_id}")
            Check out the file /cumulus_lambda_functions/catalya_uds_api/granules_archive_api.py for more details.
            Do it in a serial fashion now.
        :param catalog_s3_url:
        :return:
        """
        # Step 1: Validate S3 URL
        LOGGER.info(f'Starting catalog archive trigger for: {catalog_s3_url}')
        if not catalog_s3_url or not catalog_s3_url.startswith('s3://'):
            raise ValueError(f'Invalid S3 URL: {catalog_s3_url}. Must start with s3://')

        parsed_url = urlparse(catalog_s3_url)
        if not parsed_url.netloc or not parsed_url.path:
            raise ValueError(f'Invalid S3 URL format: {catalog_s3_url}. Expected format: s3://<bucket>/<path>')

        # Step 2: Download catalog.json
        LOGGER.info(f'Downloading catalog from: {catalog_s3_url}')
        catalog_content = self.__s3.set_s3_url(catalog_s3_url).read_small_txt_file()
        catalog_dict = json.loads(catalog_content)
        LOGGER.debug(f'Catalog downloaded successfully')

        # Step 3: Retrieve all STAC items
        LOGGER.info('Retrieving all STAC items from catalog')
        item_s3_urls = self.retrieve_all_stac_items(catalog_dict, catalog_s3_url)
        LOGGER.info(f'Found {len(item_s3_urls)} STAC items to process')

        # Step 4-6: Process all items (download, parse, update assets)
        LOGGER.info('Processing and validating all STAC items')
        processed_items = self.retrieve_items(item_s3_urls)
        LOGGER.info(f'Successfully processed {len(processed_items)} STAC items')

        # Step 7: Retrieve UDS API credentials from SSM (do this once before loop)
        LOGGER.info(f'Retrieving UDS API credentials from SSM: {self.__uds_api_creds_key}')
        if not self.__uds_api_creds_key:
            raise ValueError('UDS_API_CREDS environment variable not set')

        uds_api_creds_str = self.__ssm.get_param(self.__uds_api_creds_key)
        uds_api_creds = json.loads(uds_api_creds_str)

        # Extract API base URL and bearer token
        api_base_url = uds_api_creds.get('api_base_url', '').rstrip('/')
        bearer_token = uds_api_creds.get('bearer_token', '')

        if not api_base_url or not bearer_token:
            raise ValueError('UDS API credentials must contain api_base_url and bearer_token')

        LOGGER.info(f'API base URL: {api_base_url}')

        # Step 8: Trigger archive API requests one by one
        LOGGER.info('Triggering archive requests for all processed items')
        for item_s3_url, item_dict in processed_items.items():
            try:
                collection_id = item_dict.get('collection')
                granule_id = item_dict.get('id')

                if not collection_id or not granule_id:
                    LOGGER.error(f'Missing collection_id or granule_id in item: {item_s3_url}')
                    raise ValueError(f'Invalid STAC item missing collection or id: {item_s3_url}')

                LOGGER.info(f'Triggering archive for granule: {granule_id} from collection: {collection_id}')

                # Call the UDS API verbose_archive endpoint
                api_url = f'{api_base_url}/collections/{collection_id}/verbose_archive/{granule_id}'
                headers = {
                    'Authorization': bearer_token,
                    'Content-Type': 'application/json'
                }
                params = {
                    'item_s3_url': item_s3_url
                }

                LOGGER.info(f'Calling archive API: PUT {api_url}')
                response = requests.put(api_url, headers=headers, params=params, json=item_dict, timeout=30)
                response.raise_for_status()

                LOGGER.info(f'Successfully triggered archive for granule {granule_id}: {response.json()}')

            except Exception as e:
                LOGGER.exception(f'Error triggering archive for item {item_s3_url}: {str(e)}')
                raise

        LOGGER.info(f'Completed triggering archive for all {len(processed_items)} STAC items')
        return
