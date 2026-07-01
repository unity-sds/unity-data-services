from unittest import TestCase
import json
import os
import tempfile
import uuid
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from pystac import Item, Asset

from cumulus_lambda_functions.daac_archiver.services.staging_svc import StagingSvc


class TestStagingSvc(TestCase):
    def test_stage_files_01(self):
        """
        Test stage_files method with complete workflow:
        1. Creates actual dummy data and metadata files in temp directories
        2. Creates STAC item with assets pointing to source S3 locations
        3. Calls stage_files method
        4. Verifies files are copied to staging bucket with correct content
        5. Verifies STAC metadata has updated asset URLs and correct content
        """
        """Set up test fixtures before each test method."""
        self.s3_source_bucket = 'test-source-bucket'  # Fill this with actual bucket name later
        self.s3_staged_bucket = 'test-staged-bucket'  # Fill this with actual staged bucket name later

        # Create test collection and item IDs
        self.collection_id = 'test-collection'
        self.item_id = f'test-item-{uuid.uuid4().hex[:8]}'

        # Create test data content
        self.test_data_content = b'This is test granule data content for testing'
        self.test_metadata_content = b'This is test metadata content for testing'

        # Create test filenames
        self.test_data_filename = f'{self.item_id}_data.tif'
        self.test_metadata_filename = f'{self.item_id}_metadata.xml'

        # Setup mock S3 paths
        self.source_data_key = f'source/{self.collection_id}/{self.test_data_filename}'
        self.source_metadata_key = f'source/{self.collection_id}/{self.test_metadata_filename}'
        self.source_stac_key = f'source/{self.collection_id}/{self.item_id}.json'

        # Expected staging paths
        self.staging_prefix = f'{self.collection_id}/{self.item_id}/'
        self.staged_data_key = f'{self.staging_prefix}{self.test_data_filename}'
        self.staged_metadata_key = f'{self.staging_prefix}{self.test_metadata_filename}'
        self.staged_stac_key = f'{self.staging_prefix}{self.item_id}.json'
        with tempfile.TemporaryDirectory() as temp_source_dir, \
                tempfile.TemporaryDirectory() as temp_staged_dir:

            # Create actual source files in temp directory
            source_data_file = os.path.join(temp_source_dir, self.test_data_filename)
            source_metadata_file = os.path.join(temp_source_dir, self.test_metadata_filename)

            # Write test content to source files
            with open(source_data_file, 'wb') as f:
                f.write(self.test_data_content)
            with open(source_metadata_file, 'wb') as f:
                f.write(self.test_metadata_content)

            # Create STAC Item with assets pointing to source S3 locations
            stac_item = Item(
                id=self.item_id,
                geometry={
                    "type": "Polygon",
                    "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
                },
                bbox=[-180, -90, 180, 90],
                datetime=datetime.now(),
                properties={}
            )

            # Add assets pointing to source S3 locations
            stac_item.add_asset(
                'data',
                Asset(
                    href=f's3://{self.s3_source_bucket}/{self.source_data_key}',
                    media_type='image/tiff',
                    title='Test Data File'
                )
            )

            stac_item.add_asset(
                'metadata',
                Asset(
                    href=f's3://{self.s3_source_bucket}/{self.source_metadata_key}',
                    media_type='application/xml',
                    title='Test Metadata File'
                )
            )

            # Set collection ID
            stac_item.collection_id = self.collection_id

            # Storage for captured upload content
            uploaded_files = {}
            uploaded_stac_content = None

            def mock_s3_cp(source_bucket, source_key, dest_bucket, dest_key,
                           copy_tags: float = True, update_old_metadata_style: bool = True,
                           delete_original: bool = False):
                """Mock S3 copy that saves content to temp staged directory"""
                # Simulate copying from source to destination
                source_file_path = None
                if source_key == self.source_data_key:
                    source_file_path = source_data_file
                elif source_key == self.source_metadata_key:
                    source_file_path = source_metadata_file

                if source_file_path and os.path.exists(source_file_path):
                    # Create destination directory structure
                    dest_dir = os.path.join(temp_staged_dir, os.path.dirname(dest_key))
                    os.makedirs(dest_dir, exist_ok=True)

                    # Copy file content to simulate S3 copy
                    dest_file_path = os.path.join(temp_staged_dir, dest_key)
                    with open(source_file_path, 'rb') as src, open(dest_file_path, 'wb') as dst:
                        dst.write(src.read())

                    # Store for verification
                    uploaded_files[dest_key] = dest_file_path

            def mock_upload_bytes(content, content_type=None):
                """Mock S3 upload_bytes that captures the STAC content"""
                nonlocal uploaded_stac_content
                if isinstance(content, bytes):
                    uploaded_stac_content = content.decode('utf-8')
                else:
                    uploaded_stac_content = str(content)

            # Create DaacArchiverCatalia instance with mocked dependencies
            with patch('cumulus_lambda_functions.daac_archiver.services.staging_svc.AwsS3') as mock_s3_class:

                # Setup mocks
                mock_s3 = Mock()
                mock_s3_class.return_value = mock_s3

                # Mock S3 get_child_s3_files to return empty list (no existing files in staging)
                mock_s3.get_child_s3_files.return_value = []

                # Mock S3 copy operations with our custom function
                mock_s3.copy_artifact.side_effect = mock_s3_cp

                # Mock S3 upload operations
                mock_s3.set_s3_url.return_value = mock_s3
                mock_s3.upload_bytes.side_effect = mock_upload_bytes

                # Create archiver instance
                archiver = StagingSvc()

                # Set the staged bucket (override the 'TODO' value)
                archiver._StagingSvc__staged_s3_bucket = self.s3_staged_bucket
                archiver._StagingSvc__archiving_granules_stac = None

                # Call stage_files method
                result = archiver.stage_files(stac_item)

                # Verify the method returns self
                self.assertEqual(result, archiver)

                # Get the updated STAC item from the archiver
                updated_stac = archiver._StagingSvc__archiving_granules_stac

                # Verify that asset URLs were updated to staging locations with timestamp pattern
                # Expected pattern: s3://<staged_bucket>/<collection>/<item-id>/<yyyy-MM-ddTHH:mm:ss.fff>/<filename>

                # Check data asset
                data_asset = updated_stac.assets['data']
                data_href = data_asset.href
                self.assertTrue(
                    data_href.startswith(f's3://{self.s3_staged_bucket}/{self.collection_id}/{self.item_id}/'),
                    f"Data asset href should start with staging path: {data_href}")
                self.assertTrue(data_href.endswith(f'/{self.test_data_filename}'),
                                f"Data asset href should end with filename: {data_href}")

                # Extract timestamp portion from the path
                # Format: s3://bucket/collection/item-id/timestamp/filename
                path_parts = data_href.replace(f's3://{self.s3_staged_bucket}/', '').split('/')
                self.assertEqual(len(path_parts), 4, f"Data asset path should have 4 parts: {path_parts}")
                self.assertEqual(path_parts[0], self.collection_id, "First path part should be collection ID")
                self.assertEqual(path_parts[1], self.item_id, "Second path part should be item ID")
                timestamp_part = path_parts[2]
                filename_part = path_parts[3]

                # Verify timestamp format: yyyy-MM-ddTHH:mm:ss.fff (ISO 8601 format)
                import re
                timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,}$'
                self.assertIsNotNone(re.match(timestamp_pattern, timestamp_part),
                                     f"Timestamp should match yyyy-MM-ddTHH:mm:ss.fff format: {timestamp_part}")
                self.assertEqual(filename_part, self.test_data_filename,
                                 f"Filename should match original: {filename_part}")

                # Check metadata asset
                metadata_asset = updated_stac.assets['metadata']
                metadata_href = metadata_asset.href
                self.assertTrue(
                    metadata_href.startswith(f's3://{self.s3_staged_bucket}/{self.collection_id}/{self.item_id}/'),
                    f"Metadata asset href should start with staging path: {metadata_href}")
                self.assertTrue(metadata_href.endswith(f'/{self.test_metadata_filename}'),
                                f"Metadata asset href should end with filename: {metadata_href}")

                # Extract timestamp from metadata path and verify it matches data asset timestamp
                metadata_path_parts = metadata_href.replace(f's3://{self.s3_staged_bucket}/', '').split('/')
                metadata_timestamp_part = metadata_path_parts[2]
                self.assertEqual(timestamp_part, metadata_timestamp_part,
                                 "Both assets should have the same timestamp in their paths")

                # Verify S3 copy operations were called for each asset with correct staging paths
                self.assertEqual(mock_s3.copy_artifact.call_count, 2, "Should copy both data and metadata files")

                # Check that cp was called with the correct staging paths containing timestamps
                cp_calls = mock_s3.copy_artifact.call_args_list

                # Verify data file copy
                data_cp_call = cp_calls[0][0]  # (source_bucket, source_key, dest_bucket, dest_key)
                self.assertEqual(data_cp_call[0], self.s3_source_bucket, "Data copy source bucket")
                self.assertEqual(data_cp_call[1], self.source_data_key, "Data copy source key")
                self.assertEqual(data_cp_call[2], self.s3_staged_bucket, "Data copy dest bucket")

                # Verify destination key has correct format: collection/item-id/timestamp/filename
                data_dest_key = data_cp_call[3]
                data_dest_parts = data_dest_key.split('/')
                self.assertEqual(len(data_dest_parts), 4, f"Data dest key should have 4 parts: {data_dest_parts}")
                self.assertEqual(data_dest_parts[0], self.collection_id)
                self.assertEqual(data_dest_parts[1], self.item_id)
                self.assertIsNotNone(re.match(timestamp_pattern, data_dest_parts[2]),
                                     f"Dest key timestamp should match format: {data_dest_parts[2]}")
                self.assertEqual(data_dest_parts[3], self.test_data_filename)

                # Verify metadata file copy
                metadata_cp_call = cp_calls[1][0]
                self.assertEqual(metadata_cp_call[0], self.s3_source_bucket, "Metadata copy source bucket")
                self.assertEqual(metadata_cp_call[1], self.source_metadata_key, "Metadata copy source key")
                self.assertEqual(metadata_cp_call[2], self.s3_staged_bucket, "Metadata copy dest bucket")

                metadata_dest_key = metadata_cp_call[3]
                metadata_dest_parts = metadata_dest_key.split('/')
                self.assertEqual(len(metadata_dest_parts), 4,
                                 f"Metadata dest key should have 4 parts: {metadata_dest_parts}")
                self.assertEqual(metadata_dest_parts[0], self.collection_id)
                self.assertEqual(metadata_dest_parts[1], self.item_id)
                self.assertEqual(metadata_dest_parts[2], data_dest_parts[2],
                                 "Same timestamp should be used for both files")
                self.assertEqual(metadata_dest_parts[3], self.test_metadata_filename)

                # Verify that both assets now point to the same timestamped staging directory
                data_staging_dir = '/'.join(data_href.split('/')[:-1])  # Remove filename
                metadata_staging_dir = '/'.join(metadata_href.split('/')[:-1])  # Remove filename
                self.assertEqual(data_staging_dir, metadata_staging_dir,
                                 "Both assets should be in the same timestamped staging directory")

                print(f"✅ Test passed! Assets staged to: {data_staging_dir}")
        return
