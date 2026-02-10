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
    def test_01(self):
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
