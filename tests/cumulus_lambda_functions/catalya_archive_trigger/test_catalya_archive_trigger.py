import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch
from cumulus_lambda_functions.catalya_archive_trigger.catalya_archive_trigger import CatalyaArchiveTrigger
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3


class TestCatalyaArchiveTrigger(TestCase):
    def test_01_join_s3_url(self):
        """
join_s3_url('s3://bucket/a/b/c/d', '../../data/abc.json') -> 's3://bucket/a/b/data/abc.json'
join_s3_url('s3://bucket/a/b/c/d', './file.json') -> 's3://bucket/a/b/c/file.json'
join_s3_url('s3://bucket/a/b/c/d', '../../../file.json') -> 's3://bucket/a/file.json'

        :return:
        """
        base_path = 's3://bucket/a/b/c/d'
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, '../../data/abc.json'),
                         's3://bucket/a/b/data/abc.json')
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, './file/abc.json'),
                         's3://bucket/a/b/c/d/file/abc.json')
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, './file.json'),
                         's3://bucket/a/b/c/d/file.json')
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, 'file.json'),
                         's3://bucket/a/b/c/d/file.json')
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, '../../../file.json'),
                         's3://bucket/a/file.json')
        self.assertEqual(CatalyaArchiveTrigger.join_s3_url(base_path, '../.././fake/../../file.json'),
                         's3://bucket/a/file.json')
        return

    def test_01_retrieve_all_stac_items(self):
        """
        1. Create a temp directory using tempfile.
        2. copy all contents recursively from ../test_data into that temp directory.
        3. test retrieve_all_stac_items method from catalya_archive_trigger class
        4. Mock S3 so that the paths look like s3://test_bucket/my-user/cardiman = base temp directory
        5. Whenever "self.__s3.set_s3_url(link.target).read_small_txt_file()" is called, replace the file during set_s3_url and read the respective file and return it as a text.
        6. the method entry should be the file at /tests/test_data/1.0.0/2026/02/04/00/28/41/421236/catalog.json.
            Read it yourself and pass that as an S3 URL based on logic from step 4.
        :return:
        """
        # Step 1: Create a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 2: Copy all contents recursively from ../test_data into temp directory
            test_data_source = Path(__file__).parent.parent.parent / 'test_data'
            temp_path = Path(temp_dir)

            # Copy the test data directory structure
            shutil.copytree(test_data_source, temp_path / 'test_data')

            # Define the base path mapping: s3://test_bucket/my-user/cardiman -> temp_dir/test_data
            base_temp_dir = temp_path / 'test_data'
            s3_base_url = 's3://test_bucket/my-user/cardiman'

            # Step 4 & 5: Mock S3 operations
            # Create a mock S3 instance that will be used by CatalyaArchiveTrigger
            mock_s3_instance = MagicMock()

            # Track the current file being accessed
            current_file_path = {'path': None}

            def mock_set_s3_url(s3_url):
                """Mock set_s3_url to map S3 URL to local file path"""
                # Convert S3 URL to local file path
                if s3_url.startswith(s3_base_url):
                    # Remove the S3 base URL and map to temp directory
                    relative_path = s3_url[len(s3_base_url):].lstrip('/')
                    local_path = base_temp_dir / relative_path
                    current_file_path['path'] = local_path
                else:
                    # Handle other S3 URLs if needed
                    current_file_path['path'] = None

                return mock_s3_instance

            def mock_read_small_txt_file():
                """Mock read_small_txt_file to read from local file"""
                if current_file_path['path'] and current_file_path['path'].exists():
                    with open(current_file_path['path'], 'r') as f:
                        content = f.read()
                        # Return as dict if JSON, otherwise as string
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            return content
                else:
                    raise FileNotFoundError(f"File not found: {current_file_path['path']}")

            def mock_exists(bucket, path):
                """Mock exists to check if file exists in temp directory"""
                # Construct the S3 URL from bucket and path
                s3_url = f's3://{bucket}/{path}'

                # Convert S3 URL to local file path
                if s3_url.startswith(s3_base_url):
                    # Remove the S3 base URL and map to temp directory
                    relative_path = s3_url[len(s3_base_url):].lstrip('/')
                    local_path = base_temp_dir / relative_path
                    return local_path.exists()

                # If it doesn't match our base URL, return False
                return False

            # Use the real split_s3_url helper method
            real_s3 = AwsS3()

            # Attach mock methods to the mock instance
            mock_s3_instance.set_s3_url = mock_set_s3_url
            mock_s3_instance.read_small_txt_file = mock_read_small_txt_file
            mock_s3_instance.exists = mock_exists
            mock_s3_instance.split_s3_url = real_s3.split_s3_url

            # Step 6: Define the entry point - catalog.json
            catalog_s3_url = f'{s3_base_url}/1.0.0/2026/02/04/00/28/41/421236/catalog.json'

            # Read the catalog file to pass to retrieve_all_stac_items
            catalog_path = base_temp_dir / '1.0.0' / '2026' / '02' / '04' / '00' / '28' / '41' / '421236' / 'catalog.json'
            with open(catalog_path, 'r') as f:
                catalog_dict = json.load(f)

            # Step 3: Create instance and patch the S3 client
            with patch('cumulus_lambda_functions.catalya_archive_trigger.catalya_archive_trigger.AwsS3') as MockAwsS3:
                MockAwsS3.return_value = mock_s3_instance

                # Create the trigger instance
                trigger = CatalyaArchiveTrigger()

                # Call retrieve_all_stac_items
                item_links = trigger.retrieve_all_stac_items(catalog_dict, catalog_s3_url)

                # Assertions
                self.assertIsNotNone(item_links, "retrieve_all_stac_items should return a list")
                self.assertIsInstance(item_links, list, "Result should be a list")
                self.assertEqual(len(item_links), 1, "Should find exactly 1 item")

                # Verify that item_links contains S3 URLs (strings), not link objects
                for item_url in item_links:
                    self.assertIsInstance(item_url, str, "Item link should be a string (S3 URL)")
                    self.assertTrue(item_url.startswith(s3_base_url),
                                    f"Item URL should start with {s3_base_url}")
                    print(f"Found STAC item: {item_url}")

    def test_01_retrieve_items(self):
        """
        Test retrieve_items method:
        1. Create temp directory and copy test data
        2. Mock S3 operations
        3. Pass in a list with one item S3 URL
        4. Verify result has the URL as key with proper item dictionary
        5. Verify assets have correct S3 URLs that exist
        """
        # Step 1: Create temp directory and copy test data
        with tempfile.TemporaryDirectory() as temp_dir:
            test_data_source = Path(__file__).parent.parent.parent / 'test_data'
            temp_path = Path(temp_dir)

            # Copy the test data directory structure
            shutil.copytree(test_data_source, temp_path / 'test_data')

            # Define the base path mapping: s3://test_bucket/my-user/cardiman -> temp_dir/test_data
            base_temp_dir = temp_path / 'test_data'
            s3_base_url = 's3://test_bucket/my-user/cardiman'

            # Step 2: Mock S3 operations
            mock_s3_instance = MagicMock()

            # Track the current file being accessed
            current_file_path = {'path': None}

            def mock_set_s3_url(s3_url):
                """Mock set_s3_url to map S3 URL to local file path"""
                if s3_url.startswith(s3_base_url):
                    relative_path = s3_url[len(s3_base_url):].lstrip('/')
                    local_path = base_temp_dir / relative_path
                    current_file_path['path'] = local_path
                else:
                    current_file_path['path'] = None
                return mock_s3_instance

            def mock_read_small_txt_file():
                """Mock read_small_txt_file to read from local file"""
                if current_file_path['path'] and current_file_path['path'].exists():
                    with open(current_file_path['path'], 'r') as f:
                        return f.read()
                else:
                    raise FileNotFoundError(f"File not found: {current_file_path['path']}")

            def mock_exists(bucket, path):
                """Mock exists to check if file exists in temp directory"""
                s3_url = f's3://{bucket}/{path}'
                if s3_url.startswith(s3_base_url):
                    relative_path = s3_url[len(s3_base_url):].lstrip('/')
                    local_path = base_temp_dir / relative_path
                    return local_path.exists()
                return False

            # Use the real split_s3_url helper method
            real_s3 = AwsS3()

            # Attach mock methods to the mock instance
            mock_s3_instance.set_s3_url = mock_set_s3_url
            mock_s3_instance.read_small_txt_file = mock_read_small_txt_file
            mock_s3_instance.exists = mock_exists
            mock_s3_instance.split_s3_url = real_s3.split_s3_url

            # Step 3: Create instance and patch the S3 client
            with patch('cumulus_lambda_functions.catalya_archive_trigger.catalya_archive_trigger.AwsS3') as MockAwsS3:
                MockAwsS3.return_value = mock_s3_instance

                # Create the trigger instance
                trigger = CatalyaArchiveTrigger()

                # Define the item S3 URL to test
                item_s3_url = f'{s3_base_url}/1.0.0/2026/02/04/00/28/41/421236/cardamom-co2/items/co2_1979_01.json'
                item_s3_url1 = f'{s3_base_url}/1.0.0/2026/02/04/00/28/41/421236/cardamom-co2/items/co2_1979_01_01.json'
                item_urls = [item_s3_url, item_s3_url1]

                # Step 4: Call retrieve_items
                processed_items = trigger.retrieve_items(item_urls)

                # Assertions
                self.assertIsNotNone(processed_items, "retrieve_items should return a dictionary")
                self.assertIsInstance(processed_items, dict, "Result should be a dictionary")
                self.assertEqual(len(processed_items), 1, "Should have exactly 1 processed item")

                # Verify the item S3 URL is a key in the result
                self.assertIn(item_s3_url1, processed_items, f"Result should contain key: {item_s3_url}")

                # Get the processed item dictionary
                item_dict = processed_items[item_s3_url1]
                self.assertIsInstance(item_dict, dict, "Item should be a dictionary")

                # Verify item has required fields
                self.assertIn('id', item_dict, "Item should have 'id' field")
                self.assertIn('collection', item_dict, "Item should have 'collection' field")
                self.assertIn('assets', item_dict, "Item should have 'assets' field")

                print(f"Item ID: {item_dict.get('id')}")
                print(f"Collection: {item_dict.get('collection')}")

                # Step 5: Verify assets have correct S3 URLs and they exist
                assets = item_dict.get('assets', {})
                self.assertGreater(len(assets), 0, "Item should have at least one asset")

                for asset_key, asset in assets.items():
                    self.assertIn('href', asset, f"Asset '{asset_key}' should have 'href' field")
                    asset_href = asset['href']

                    print(f"Asset '{asset_key}': {asset_href}")

                    # Verify asset href is an S3 URL
                    self.assertTrue(asset_href.startswith('s3://'),
                                    f"Asset href should be an S3 URL: {asset_href}")

                    # Verify the asset exists using the mock exists method
                    bucket, path = real_s3.split_s3_url(asset_href)
                    self.assertTrue(mock_exists(bucket, path),
                                    f"Asset should exist at: {asset_href}")
