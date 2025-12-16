import json
import os
import tempfile
import uuid
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from pystac import Item, Asset
from cumulus_lambda_functions.daac_archiver.daac_archiver_catalia import DaacArchiverCatalia


class TestDaacArchiverCatalia(TestCase):

    def setUp(self):
        return

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
                      copy_tags: float = True, update_old_metadata_style: bool = True, delete_original: bool = False):
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
            with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
                 patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
                 patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory:

                # Setup mocks
                mock_s3 = Mock()
                mock_s3_class.return_value = mock_s3
                mock_sns = Mock()
                mock_sns_class.return_value = mock_sns
                mock_sfa_client = Mock()
                mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

                # Mock S3 get_child_s3_files to return empty list (no existing files in staging)
                mock_s3.get_child_s3_files.return_value = []

                # Mock S3 copy operations with our custom function
                mock_s3.copy_artifact.side_effect = mock_s3_cp

                # Mock S3 upload operations
                mock_s3.set_s3_url.return_value = mock_s3
                mock_s3.upload_bytes.side_effect = mock_upload_bytes

                # Create archiver instance
                archiver = DaacArchiverCatalia()

                # Set the staged bucket (override the 'TODO' value)
                archiver._DaacArchiverCatalia__staged_s3_bucket = self.s3_staged_bucket

                # Set the STAC item to be archived
                archiver._DaacArchiverCatalia__archiving_granules_stac = stac_item

                # Call stage_files method
                result = archiver.stage_files()

                # Verify the method returns self
                self.assertEqual(result, archiver)

                # Get the updated STAC item from the archiver
                updated_stac = archiver._DaacArchiverCatalia__archiving_granules_stac

                # Verify that asset URLs were updated to staging locations with timestamp pattern
                # Expected pattern: s3://<staged_bucket>/<collection>/<item-id>/<yyyy-MM-ddTHH:mm:ss.fff>/<filename>

                # Check data asset
                data_asset = updated_stac.assets['data']
                data_href = data_asset.href
                self.assertTrue(data_href.startswith(f's3://{self.s3_staged_bucket}/{self.collection_id}/{self.item_id}/'),
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
                self.assertTrue(metadata_href.startswith(f's3://{self.s3_staged_bucket}/{self.collection_id}/{self.item_id}/'),
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
                self.assertEqual(len(metadata_dest_parts), 4, f"Metadata dest key should have 4 parts: {metadata_dest_parts}")
                self.assertEqual(metadata_dest_parts[0], self.collection_id)
                self.assertEqual(metadata_dest_parts[1], self.item_id)
                self.assertEqual(metadata_dest_parts[2], data_dest_parts[2], "Same timestamp should be used for both files")
                self.assertEqual(metadata_dest_parts[3], self.test_metadata_filename)

                # Verify that both assets now point to the same timestamped staging directory
                data_staging_dir = '/'.join(data_href.split('/')[:-1])  # Remove filename
                metadata_staging_dir = '/'.join(metadata_href.split('/')[:-1])  # Remove filename
                self.assertEqual(data_staging_dir, metadata_staging_dir,
                               "Both assets should be in the same timestamped staging directory")

                print(f"✅ Test passed! Assets staged to: {data_staging_dir}")
        return

    def test_update_status_01(self):
        """
        Test update_status method with progressive status updates:
        1. Creates STAC item without archival extension or status
        2. Adds archival statuses one by one in sequence
        3. Verifies each status is added correctly and in order
        4. Verifies STAC Fast API client update_item is called
        """
        # Setup test data
        collection_id = 'example-collection'
        item_id = f'example-item-{uuid.uuid4().hex[:8]}'

        # Create STAC Item without any archival extension or properties
        stac_item = Item(
            id=item_id,
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}  # No archival extension or status initially
        )
        stac_item.collection_id = collection_id

        # Define status updates to apply in sequence
        status_updates = [
            {
                "status": "cnm-authorized-success"
            },
            {
                "status": "cnm-staged-success",
                "href": "s3://uds-staging/example-collection/example-item-with-archival-status"
            },
            {
                "status": "cnm-submit-success"
            },
            {
                "status": "cnm-receive-failed",
                "errorCode": "NETWORK_TIMEOUT",
                "errorMessage": "Failed to receive CNM response within timeout period",
                "href": "https://example.com/cnm/receive/def456"
            }
        ]

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory:

            # Setup mocks
            mock_s3 = Mock()
            mock_s3_class.return_value = mock_s3
            mock_sns = Mock()
            mock_sns_class.return_value = mock_sns
            mock_sfa_client = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

            # Storage for captured SFA client calls
            sfa_calls = []

            # Mock SFA client update_item to capture and verify parameters
            def mock_update_item(collection_id, item_id, item, update_whole=True):
                # Store the call details for verification
                call_info = {
                    'collection_id': collection_id,
                    'item_id': item_id,
                    'item_dict': item.copy()  # Make a copy to preserve state
                }
                sfa_calls.append(call_info)

                # Verify the basic parameters are correct
                expected_collection_id = 'example-collection'
                expected_item_id = item_id  # This will be the generated item_id

                if collection_id != expected_collection_id:
                    raise AssertionError(f"Expected collection_id '{expected_collection_id}', got '{collection_id}'")

                return item

            mock_sfa_client.update_item.side_effect = mock_update_item

            # Create archiver instance
            archiver = DaacArchiverCatalia()

            # Set the STAC item to be updated
            archiver._DaacArchiverCatalia__archiving_granules_stac = stac_item

            # Verify initial state - no archival extension or status
            initial_stac = archiver._DaacArchiverCatalia__archiving_granules_stac
            self.assertNotIn('archival:status', initial_stac.properties,
                           "Initially should have no archival:status property")

            # Check if stac_extensions exists and if it does, verify no archival extension
            if hasattr(initial_stac, 'stac_extensions') and initial_stac.stac_extensions:
                self.assertNotIn(archiver._DaacArchiverCatalia__archiving_status_extension_url, initial_stac.stac_extensions,
                               "Initially should have no archival extension")
            archiver.add_archival_extension()
            # Apply status updates one by one and verify each
            for i, status_update in enumerate(status_updates):
                # Call update_status with the current status
                result = archiver.update_status(status_update)

                # Verify method returns self
                self.assertEqual(result, archiver, f"update_status should return self (iteration {i+1})")

                # Get updated STAC item
                updated_stac = archiver._DaacArchiverCatalia__archiving_granules_stac

                # Verify archival extension was added (should happen on first call)
                self.assertIn(archiver._DaacArchiverCatalia__archiving_status_extension_url, updated_stac.stac_extensions,
                            f"Archival extension should be present after update {i+1}")

                # Verify archival:status property exists and is a list
                self.assertIn('archival:status', updated_stac.properties,
                            f"archival:status property should exist after update {i+1}")
                archival_statuses = updated_stac.properties['archival:status']
                self.assertIsInstance(archival_statuses, list,
                                    f"archival:status should be a list after update {i+1}")

                # Verify correct number of status entries
                expected_count = i + 1
                self.assertEqual(len(archival_statuses), expected_count,
                               f"Should have {expected_count} status entries after update {i+1}")

                # Verify the latest status was added correctly
                latest_status = archival_statuses[-1]

                # Check required status field
                self.assertEqual(latest_status['status'], status_update['status'],
                               f"Status field should match for update {i+1}")

                # Check optional fields if present in the update
                if 'href' in status_update:
                    self.assertEqual(latest_status['href'], status_update['href'],
                                   f"href field should match for update {i+1}")

                if 'errorCode' in status_update:
                    self.assertEqual(latest_status['errorCode'], status_update['errorCode'],
                                   f"errorCode field should match for update {i+1}")

                if 'errorMessage' in status_update:
                    self.assertEqual(latest_status['errorMessage'], status_update['errorMessage'],
                                   f"errorMessage field should match for update {i+1}")

                # Verify datetime was automatically added
                self.assertIn('datetime', latest_status,
                            f"datetime should be automatically added for update {i+1}")

                # Verify timestamp format (should end with 'Z' for UTC)
                timestamp = latest_status['datetime']
                self.assertTrue(timestamp.endswith('Z'),
                              f"timestamp should end with 'Z' for update {i+1}: {timestamp}")

                # Verify SFA client update_item was called
                expected_call_count = i + 1
                self.assertEqual(mock_sfa_client.update_item.call_count, expected_call_count,
                               f"SFA client update_item should be called {expected_call_count} times")

                # Verify the captured SFA call details
                self.assertEqual(len(sfa_calls), expected_call_count,
                               f"Should have captured {expected_call_count} SFA calls")

                # Get the latest SFA call details
                latest_sfa_call = sfa_calls[-1]

                # Verify call parameters
                self.assertEqual(latest_sfa_call['collection_id'], collection_id,
                               f"SFA call collection_id should be correct for update {i+1}")
                self.assertEqual(latest_sfa_call['item_id'], item_id,
                               f"SFA call item_id should be correct for update {i+1}")

                # Verify the item_dict content that was sent to SFA client
                sent_item_dict = latest_sfa_call['item_dict']
                self.assertIsInstance(sent_item_dict, dict,
                                    f"SFA call item_dict should be a dict for update {i+1}")

                # Verify basic STAC structure in sent item_dict
                self.assertEqual(sent_item_dict['id'], item_id,
                               f"SFA item_dict should have correct id for update {i+1}")
                self.assertEqual(sent_item_dict['collection'], collection_id,
                               f"SFA item_dict should have correct collection for update {i+1}")

                # Verify archival extension was added to sent item_dict
                self.assertIn('stac_extensions', sent_item_dict,
                            f"SFA item_dict should have stac_extensions for update {i+1}")
                self.assertIn(archiver._DaacArchiverCatalia__archiving_status_extension_url, sent_item_dict['stac_extensions'],
                            f"SFA item_dict should have archival extension for update {i+1}")

                # Verify archival:status property in sent item_dict
                self.assertIn('properties', sent_item_dict,
                            f"SFA item_dict should have properties for update {i+1}")
                properties = sent_item_dict['properties']
                self.assertIn('archival:status', properties,
                            f"SFA item_dict properties should have archival:status for update {i+1}")

                # Verify archival:status content in sent item_dict
                sent_archival_statuses = properties['archival:status']
                self.assertIsInstance(sent_archival_statuses, list,
                                    f"SFA item_dict archival:status should be a list for update {i+1}")
                self.assertEqual(len(sent_archival_statuses), expected_count,
                               f"SFA item_dict should have {expected_count} status entries for update {i+1}")

                # Verify the latest status in sent item_dict matches what we just added
                sent_latest_status = sent_archival_statuses[-1]
                self.assertEqual(sent_latest_status['status'], status_update['status'],
                               f"SFA item_dict latest status should match for update {i+1}")

                # Verify datetime was added to sent item_dict
                self.assertIn('datetime', sent_latest_status,
                            f"SFA item_dict latest status should have datetime for update {i+1}")
                sent_timestamp = sent_latest_status['datetime']
                self.assertTrue(sent_timestamp.endswith('Z'),
                              f"SFA item_dict timestamp should end with 'Z' for update {i+1}: {sent_timestamp}")

                # Verify optional fields in sent item_dict
                if 'href' in status_update:
                    self.assertIn('href', sent_latest_status,
                                f"SFA item_dict should have href for update {i+1}")
                    self.assertEqual(sent_latest_status['href'], status_update['href'],
                                   f"SFA item_dict href should match for update {i+1}")

                if 'errorCode' in status_update:
                    self.assertIn('errorCode', sent_latest_status,
                                f"SFA item_dict should have errorCode for update {i+1}")
                    self.assertEqual(sent_latest_status['errorCode'], status_update['errorCode'],
                                   f"SFA item_dict errorCode should match for update {i+1}")

                if 'errorMessage' in status_update:
                    self.assertIn('errorMessage', sent_latest_status,
                                f"SFA item_dict should have errorMessage for update {i+1}")
                    self.assertEqual(sent_latest_status['errorMessage'], status_update['errorMessage'],
                                   f"SFA item_dict errorMessage should match for update {i+1}")

            # Final verification - check all statuses are in correct order
            final_stac = archiver._DaacArchiverCatalia__archiving_granules_stac
            final_statuses = final_stac.properties['archival:status']

            # Verify all status values are in the correct sequence
            expected_status_sequence = [update['status'] for update in status_updates]
            actual_status_sequence = [status['status'] for status in final_statuses]
            self.assertEqual(actual_status_sequence, expected_status_sequence,
                           "Status updates should be in the correct order")

            # Verify statuses with href field have correct href values
            statuses_with_href = [(i, status) for i, status in enumerate(final_statuses) if 'href' in status]
            expected_hrefs = [
                (1, "s3://uds-staging/example-collection/example-item-with-archival-status"),  # cnm-staged-success
                (3, "https://example.com/cnm/receive/def456")  # cnm-receive-failed
            ]

            for status_index, expected_href in expected_hrefs:
                found_status = final_statuses[status_index]
                self.assertEqual(found_status['href'], expected_href,
                               f"Status at index {status_index} should have href: {expected_href}")

            # Verify error information for failed status
            failed_status = final_statuses[3]  # cnm-receive-failed
            self.assertEqual(failed_status['errorCode'], "NETWORK_TIMEOUT")
            self.assertEqual(failed_status['errorMessage'], "Failed to receive CNM response within timeout period")

            # Final verification of the last item_dict sent to SFA client
            final_sfa_call = sfa_calls[-1]
            final_sent_item_dict = final_sfa_call['item_dict']

            # Verify the final sent item_dict has all status updates in correct order
            final_sent_properties = final_sent_item_dict['properties']
            final_sent_statuses = final_sent_properties['archival:status']

            # Verify all status values are in the correct sequence in sent item_dict
            final_sent_status_sequence = [status['status'] for status in final_sent_statuses]
            self.assertEqual(final_sent_status_sequence, expected_status_sequence,
                           "Status updates should be in correct order in final sent item_dict")

            # Verify specific statuses in final sent item_dict
            # Status 0: cnm-authorized-success (basic status only)
            sent_status_0 = final_sent_statuses[0]
            self.assertEqual(sent_status_0['status'], "cnm-authorized-success")
            self.assertIn('datetime', sent_status_0)
            self.assertNotIn('href', sent_status_0)
            self.assertNotIn('errorCode', sent_status_0)

            # Status 1: cnm-staged-success (with href)
            sent_status_1 = final_sent_statuses[1]
            self.assertEqual(sent_status_1['status'], "cnm-staged-success")
            self.assertEqual(sent_status_1['href'], "s3://uds-staging/example-collection/example-item-with-archival-status")
            self.assertIn('datetime', sent_status_1)
            self.assertNotIn('errorCode', sent_status_1)

            # Status 2: cnm-submit-success (basic status only)
            sent_status_2 = final_sent_statuses[2]
            self.assertEqual(sent_status_2['status'], "cnm-submit-success")
            self.assertIn('datetime', sent_status_2)
            self.assertNotIn('href', sent_status_2)
            self.assertNotIn('errorCode', sent_status_2)

            # Status 3: cnm-receive-failed (with href and error details)
            sent_status_3 = final_sent_statuses[3]
            self.assertEqual(sent_status_3['status'], "cnm-receive-failed")
            self.assertEqual(sent_status_3['href'], "https://example.com/cnm/receive/def456")
            self.assertEqual(sent_status_3['errorCode'], "NETWORK_TIMEOUT")
            self.assertEqual(sent_status_3['errorMessage'], "Failed to receive CNM response within timeout period")
            self.assertIn('datetime', sent_status_3)

            # Verify all statuses have unique timestamps (they should be different due to sequential calls)
            sent_timestamps = [status['datetime'] for status in final_sent_statuses]
            self.assertEqual(len(sent_timestamps), len(set(sent_timestamps)),
                           "All status timestamps should be unique in sent item_dict")

            print(f"✅ Test passed! All {len(status_updates)} status updates applied correctly in sequence")
            print(f"📤 Verified SFA client received correct item_dict with {len(final_sent_statuses)} status entries")

    def test_extract_files_01(self):
        """
        Test extract_files method with specific DAAC config and STAC assets:
        1. Creates STAC item with various file types (.nc, browse, .xml, .json)
        2. Uses DAAC config with specific archiving types and extensions
        3. Verifies correct files are filtered and converted to CNM format
        4. Checks CNM format structure and field values
        """
        # Setup test data
        collection_id = 'test-collection-extract'
        item_id = f'test-item-extract-{uuid.uuid4().hex[:8]}'

        # Create STAC Item with various assets
        stac_item = Item(
            id=item_id,
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}
        )
        stac_item.collection_id = collection_id

        # Add assets with different types and extensions
        # 1. .nc data file (should be included - matches 'data' type and '.nc' extension)
        stac_item.add_asset(
            'data_file.nc',
            Asset(
                href='s3://test-bucket/path/data_file.nc',
                media_type='application/netcdf',
                title='NetCDF Data File',
                description='size=2048000;checksumType=md5;checksum=abc123def456',
                roles=['data'],
                extra_fields={
                    'file:size': 2048000,
                    'file:checksum': 'abc123def456'
                }
            )
        )

        # 2. Browse file (should be included - matches 'browse' type, no extension filter)
        stac_item.add_asset(
            'browse_image.png',
            Asset(
                href='s3://test-bucket/path/browse_image.png',
                media_type='image/png',
                title='Browse Image',
                description='size=512000;checksumType=sha256;checksum=xyz789abc123',
                roles=['browse'],
                extra_fields={
                    'file:size': 512000,
                    'file:checksum': 'xyz789abc123'
                }
            )
        )

        # 3. .xml metadata file (should be excluded - no metadata assets match the extensions)
        # Actually, let's create a different metadata file to test filtering
        stac_item.add_asset(
            'metadata_file.txt',
            Asset(
                href='s3://test-bucket/path/metadata_file.txt',
                media_type='text/plain',
                title='Metadata Text File',
                description='size=1024;checksumType=md5;checksum=meta123456',
                roles=['metadata'],
                extra_fields={
                    'file:size': 1024,
                    'file:checksum': 'meta123456'
                }
            )
        )

        # 4. .json data file (should be included - matches 'data' type and '.json' extension)
        stac_item.add_asset(
            'config.json',
            Asset(
                href='s3://test-bucket/path/config.json',
                media_type='application/json',
                title='Configuration JSON',
                description='size=4096;checksumType=md5;checksum=json987654',
                roles=['data'],
                extra_fields={
                    'file:size': 4096,
                    'file:checksum': 'json987654'
                }
            )
        )

        # 5. .tif data file (should be excluded - 'data' type but wrong extension)
        stac_item.add_asset(
            'image.tif',
            Asset(
                href='s3://test-bucket/path/image.tif',
                media_type='image/tiff',
                title='TIFF Image',
                description='size=8192000;checksumType=md5;checksum=tiff111222',
                roles=['data'],
                extra_fields={
                    'file:size': 8192000,
                    'file:checksum': 'tiff111222'
                }
            )
        )

        # Define DAAC config with specific archiving types
        daac_config = {
            'daac_collection_name': 'TEST_COLLECTION',
            'daac_data_version': '1.0',
            'daac_provider': 'test_provider',
            'archiving_types': [
                {'data_type': 'data', 'file_extension': ['.json', '.nc']},
                {'data_type': 'metadata', 'file_extension': ['.xml']},
                {'data_type': 'browse'},  # No file_extension means all files of this type
            ],
        }

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory:

            # Setup mocks
            mock_s3 = Mock()
            mock_s3_class.return_value = mock_s3
            mock_sns = Mock()
            mock_sns_class.return_value = mock_sns
            mock_sfa_client = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

            # Create archiver instance
            archiver = DaacArchiverCatalia()

            # Set the STAC item
            archiver._DaacArchiverCatalia__archiving_granules_stac = stac_item

            # Call extract_files method
            extracted_files = archiver.extract_files(daac_config)

            # Verify correct number of files extracted
            # Expected: data_file.nc, browse_image.png, config.json (3 files)
            # Excluded: metadata_file.txt (.txt not in .xml filter), image.tif (.tif not in data extensions)
            expected_file_count = 3
            self.assertEqual(len(extracted_files), expected_file_count,
                           f"Should extract {expected_file_count} files, got {len(extracted_files)}")

            # Verify each extracted file has correct CNM format structure
            for cnm_file in extracted_files:
                # Check required CNM fields are present
                self.assertIn('type', cnm_file, "CNM file should have 'type' field")
                self.assertIn('name', cnm_file, "CNM file should have 'name' field")
                self.assertIn('uri', cnm_file, "CNM file should have 'uri' field")
                self.assertIn('checksumType', cnm_file, "CNM file should have 'checksumType' field")
                self.assertIn('checksum', cnm_file, "CNM file should have 'checksum' field")
                self.assertIn('size', cnm_file, "CNM file should have 'size' field")

                # Check field types
                self.assertIsInstance(cnm_file['type'], str, "'type' should be string")
                self.assertIsInstance(cnm_file['name'], str, "'name' should be string")
                self.assertIsInstance(cnm_file['uri'], str, "'uri' should be string")
                self.assertIsInstance(cnm_file['checksumType'], str, "'checksumType' should be string")
                self.assertIsInstance(cnm_file['checksum'], str, "'checksum' should be string")
                self.assertIsInstance(cnm_file['size'], int, "'size' should be integer")

            # Create a map of extracted files by name for easier verification
            extracted_files_by_name = {cnm_file['name']: cnm_file for cnm_file in extracted_files}

            # Verify specific files were included with correct values
            # 1. Verify data_file.nc was included
            self.assertIn('data_file.nc', extracted_files_by_name, "data_file.nc should be included")
            nc_file = extracted_files_by_name['data_file.nc']
            self.assertEqual(nc_file['type'], 'data', "NC file should have type 'data'")
            self.assertEqual(nc_file['uri'], 's3://test-bucket/path/data_file.nc', "NC file URI should match")
            self.assertEqual(nc_file['size'], 2048000, "NC file size should match")
            self.assertEqual(nc_file['checksum'], 'abc123def456', "NC file checksum should match")
            self.assertEqual(nc_file['checksumType'], 'md5', "NC file checksum type should be md5")

            # 2. Verify browse_image.png was included
            self.assertIn('browse_image.png', extracted_files_by_name, "browse_image.png should be included")
            browse_file = extracted_files_by_name['browse_image.png']
            self.assertEqual(browse_file['type'], 'browse', "Browse file should have type 'browse'")
            self.assertEqual(browse_file['uri'], 's3://test-bucket/path/browse_image.png', "Browse file URI should match")
            self.assertEqual(browse_file['size'], 512000, "Browse file size should match")
            self.assertEqual(browse_file['checksum'], 'xyz789abc123', "Browse file checksum should match")
            self.assertEqual(browse_file['checksumType'], 'sha256', "Browse file checksum type should be sha256")

            # 3. Verify config.json was included
            self.assertIn('config.json', extracted_files_by_name, "config.json should be included")
            json_file = extracted_files_by_name['config.json']
            self.assertEqual(json_file['type'], 'data', "JSON file should have type 'data'")
            self.assertEqual(json_file['uri'], 's3://test-bucket/path/config.json', "JSON file URI should match")
            self.assertEqual(json_file['size'], 4096, "JSON file size should match")
            self.assertEqual(json_file['checksum'], 'json987654', "JSON file checksum should match")
            self.assertEqual(json_file['checksumType'], 'md5', "JSON file checksum type should be md5")

            # 4. Verify excluded files are NOT present
            self.assertNotIn('metadata_file.txt', extracted_files_by_name,
                           "metadata_file.txt should be excluded (wrong extension)")
            self.assertNotIn('image.tif', extracted_files_by_name,
                           "image.tif should be excluded (wrong extension for data type)")

            # Verify filtering logic worked correctly
            expected_files = {'data_file.nc', 'browse_image.png', 'config.json'}
            actual_files = set(extracted_files_by_name.keys())
            self.assertEqual(actual_files, expected_files,
                           f"Extracted files should match expected. Expected: {expected_files}, Got: {actual_files}")

            # Verify URI format (should all be S3 URLs)
            for cnm_file in extracted_files:
                self.assertTrue(cnm_file['uri'].startswith('s3://'),
                              f"URI should be S3 URL: {cnm_file['uri']}")

            # Verify sizes are positive
            for cnm_file in extracted_files:
                self.assertGreater(cnm_file['size'], 0,
                                 f"File size should be positive: {cnm_file['name']} has size {cnm_file['size']}")

            # Verify checksums are not 'unknown' for our test files
            for cnm_file in extracted_files:
                self.assertNotEqual(cnm_file['checksum'], 'unknown',
                                  f"Checksum should be extracted from STAC for: {cnm_file['name']}")

            print(f"✅ Test passed! Extracted {len(extracted_files)} files with correct filtering:")
            for cnm_file in extracted_files:
                print(f"  - {cnm_file['name']} (type: {cnm_file['type']}, size: {cnm_file['size']})")
            print(f"📋 Filtering worked correctly: included expected files, excluded non-matching files")

    def test_extract_files_02(self):
        """
        Test extract_files method with NO archiving_types in DAAC config:
        1. Creates STAC item with various file types and extensions
        2. Uses DAAC config WITHOUT archiving_types field
        3. Verifies ALL files are extracted (no filtering)
        4. Checks CNM format structure for all files
        """
        # Setup test data
        collection_id = 'test-collection-no-filter'
        item_id = f'test-item-no-filter-{uuid.uuid4().hex[:8]}'

        # Create STAC Item with various assets
        stac_item = Item(
            id=item_id,
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}
        )
        stac_item.collection_id = collection_id

        # Add diverse set of assets - all should be included
        # 1. NetCDF data file
        stac_item.add_asset(
            'science_data.nc',
            Asset(
                href='s3://test-bucket/data/science_data.nc',
                media_type='application/netcdf',
                title='Science Data NetCDF',
                description='size=5242880;checksumType=md5;checksum=science123abc',
                roles=['data'],
                extra_fields={
                    'file:size': 5242880,
                    'file:checksum': 'science123abc'
                }
            )
        )

        # 2. XML metadata file
        stac_item.add_asset(
            'metadata.xml',
            Asset(
                href='s3://test-bucket/metadata/metadata.xml',
                media_type='application/xml',
                title='Granule Metadata',
                description='size=8192;checksumType=sha1;checksum=meta456def',
                roles=['metadata'],
                extra_fields={
                    'file:size': 8192,
                    'file:checksum': 'meta456def'
                }
            )
        )

        # 3. Browse image
        stac_item.add_asset(
            'quicklook.jpg',
            Asset(
                href='s3://test-bucket/browse/quicklook.jpg',
                media_type='image/jpeg',
                title='Browse Image',
                description='size=204800;checksumType=md5;checksum=browse789ghi',
                roles=['browse'],
                extra_fields={
                    'file:size': 204800,
                    'file:checksum': 'browse789ghi'
                }
            )
        )

        # 4. Documentation file
        stac_item.add_asset(
            'readme.txt',
            Asset(
                href='s3://test-bucket/docs/readme.txt',
                media_type='text/plain',
                title='Documentation',
                description='size=2048;checksumType=sha256;checksum=docs123jkl',
                roles=['documentation'],
                extra_fields={
                    'file:size': 2048,
                    'file:checksum': 'docs123jkl'
                }
            )
        )

        # 5. Configuration JSON
        stac_item.add_asset(
            'processing_params.json',
            Asset(
                href='s3://test-bucket/config/processing_params.json',
                media_type='application/json',
                title='Processing Parameters',
                description='size=1024;checksumType=md5;checksum=config456mno',
                roles=['data'],
                extra_fields={
                    'file:size': 1024,
                    'file:checksum': 'config456mno'
                }
            )
        )

        # 6. Binary data file with unusual extension
        stac_item.add_asset(
            'calibration.cal',
            Asset(
                href='s3://test-bucket/cal/calibration.cal',
                media_type='application/octet-stream',
                title='Calibration Data',
                description='size=16384;checksumType=sha256;checksum=cal789pqr',
                roles=['data'],
                extra_fields={
                    'file:size': 16384,
                    'file:checksum': 'cal789pqr'
                }
            )
        )

        # Define DAAC config WITHOUT archiving_types field
        daac_config = {
            'daac_collection_name': 'TEST_COLLECTION_ALL',
            'daac_data_version': '2.0',
            'daac_provider': 'test_provider_all'
            # NOTE: No 'archiving_types' field - should extract all files
        }

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory:

            # Setup mocks
            mock_s3 = Mock()
            mock_s3_class.return_value = mock_s3
            mock_sns = Mock()
            mock_sns_class.return_value = mock_sns
            mock_sfa_client = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

            # Create archiver instance
            archiver = DaacArchiverCatalia()

            # Set the STAC item
            archiver._DaacArchiverCatalia__archiving_granules_stac = stac_item

            # Call extract_files method
            extracted_files = archiver.extract_files(daac_config)

            # Verify ALL files were extracted (no filtering)
            expected_file_count = 6  # All 6 assets should be included
            self.assertEqual(len(extracted_files), expected_file_count,
                           f"Should extract ALL {expected_file_count} files when no archiving_types specified, got {len(extracted_files)}")

            # Verify each extracted file has correct CNM format structure
            for cnm_file in extracted_files:
                # Check required CNM fields are present
                self.assertIn('type', cnm_file, "CNM file should have 'type' field")
                self.assertIn('name', cnm_file, "CNM file should have 'name' field")
                self.assertIn('uri', cnm_file, "CNM file should have 'uri' field")
                self.assertIn('checksumType', cnm_file, "CNM file should have 'checksumType' field")
                self.assertIn('checksum', cnm_file, "CNM file should have 'checksum' field")
                self.assertIn('size', cnm_file, "CNM file should have 'size' field")

                # Check field types
                self.assertIsInstance(cnm_file['type'], str, "'type' should be string")
                self.assertIsInstance(cnm_file['name'], str, "'name' should be string")
                self.assertIsInstance(cnm_file['uri'], str, "'uri' should be string")
                self.assertIsInstance(cnm_file['checksumType'], str, "'checksumType' should be string")
                self.assertIsInstance(cnm_file['checksum'], str, "'checksum' should be string")
                self.assertIsInstance(cnm_file['size'], int, "'size' should be integer")

            # Create a map of extracted files by name for easier verification
            extracted_files_by_name = {cnm_file['name']: cnm_file for cnm_file in extracted_files}

            # Verify ALL assets were included with correct values
            expected_files = {
                'science_data.nc', 'metadata.xml', 'quicklook.jpg',
                'readme.txt', 'processing_params.json', 'calibration.cal'
            }
            actual_files = set(extracted_files_by_name.keys())
            self.assertEqual(actual_files, expected_files,
                           f"All files should be extracted. Expected: {expected_files}, Got: {actual_files}")

            # Verify specific files with their expected properties
            # 1. NetCDF file
            nc_file = extracted_files_by_name['science_data.nc']
            self.assertEqual(nc_file['type'], 'data')
            self.assertEqual(nc_file['uri'], 's3://test-bucket/data/science_data.nc')
            self.assertEqual(nc_file['size'], 5242880)
            self.assertEqual(nc_file['checksum'], 'science123abc')
            self.assertEqual(nc_file['checksumType'], 'md5')

            # 2. XML metadata file
            xml_file = extracted_files_by_name['metadata.xml']
            self.assertEqual(xml_file['type'], 'metadata')
            self.assertEqual(xml_file['uri'], 's3://test-bucket/metadata/metadata.xml')
            self.assertEqual(xml_file['size'], 8192)
            self.assertEqual(xml_file['checksum'], 'meta456def')
            self.assertEqual(xml_file['checksumType'], 'sha1')

            # 3. Browse image
            browse_file = extracted_files_by_name['quicklook.jpg']
            self.assertEqual(browse_file['type'], 'browse')
            self.assertEqual(browse_file['uri'], 's3://test-bucket/browse/quicklook.jpg')
            self.assertEqual(browse_file['size'], 204800)
            self.assertEqual(browse_file['checksum'], 'browse789ghi')
            self.assertEqual(browse_file['checksumType'], 'md5')

            # 4. Documentation file
            docs_file = extracted_files_by_name['readme.txt']
            self.assertEqual(docs_file['type'], 'documentation')
            self.assertEqual(docs_file['uri'], 's3://test-bucket/docs/readme.txt')
            self.assertEqual(docs_file['size'], 2048)
            self.assertEqual(docs_file['checksum'], 'docs123jkl')
            self.assertEqual(docs_file['checksumType'], 'sha256')

            # 5. JSON config file
            json_file = extracted_files_by_name['processing_params.json']
            self.assertEqual(json_file['type'], 'data')
            self.assertEqual(json_file['uri'], 's3://test-bucket/config/processing_params.json')
            self.assertEqual(json_file['size'], 1024)
            self.assertEqual(json_file['checksum'], 'config456mno')
            self.assertEqual(json_file['checksumType'], 'md5')

            # 6. Binary calibration file
            cal_file = extracted_files_by_name['calibration.cal']
            self.assertEqual(cal_file['type'], 'data')
            self.assertEqual(cal_file['uri'], 's3://test-bucket/cal/calibration.cal')
            self.assertEqual(cal_file['size'], 16384)
            self.assertEqual(cal_file['checksum'], 'cal789pqr')
            self.assertEqual(cal_file['checksumType'], 'sha256')

            # Verify variety of asset types were preserved
            extracted_types = {cnm_file['type'] for cnm_file in extracted_files}
            expected_types = {'data', 'metadata', 'browse', 'documentation'}
            self.assertEqual(extracted_types, expected_types,
                           f"Should preserve all asset types. Expected: {expected_types}, Got: {extracted_types}")

            # Verify variety of checksum types were preserved
            extracted_checksum_types = {cnm_file['checksumType'] for cnm_file in extracted_files}
            expected_checksum_types = {'md5', 'sha1', 'sha256'}
            self.assertEqual(extracted_checksum_types, expected_checksum_types,
                           f"Should preserve all checksum types. Expected: {expected_checksum_types}, Got: {extracted_checksum_types}")

            # Verify file extensions variety (no filtering applied)
            extracted_extensions = {cnm_file['name'].split('.')[-1] for cnm_file in extracted_files}
            expected_extensions = {'nc', 'xml', 'jpg', 'txt', 'json', 'cal'}
            self.assertEqual(extracted_extensions, expected_extensions,
                           f"Should include all file extensions. Expected: {expected_extensions}, Got: {extracted_extensions}")

            # Verify URI format (should all be S3 URLs)
            for cnm_file in extracted_files:
                self.assertTrue(cnm_file['uri'].startswith('s3://'),
                              f"URI should be S3 URL: {cnm_file['uri']}")

            # Verify sizes are positive
            for cnm_file in extracted_files:
                self.assertGreater(cnm_file['size'], 0,
                                 f"File size should be positive: {cnm_file['name']} has size {cnm_file['size']}")

            # Verify no 'unknown' checksums (all extracted from STAC)
            for cnm_file in extracted_files:
                self.assertNotEqual(cnm_file['checksum'], 'unknown',
                                  f"Checksum should be extracted from STAC for: {cnm_file['name']}")

            print(f"✅ Test passed! Extracted ALL {len(extracted_files)} files (no filtering applied):")
            for cnm_file in extracted_files:
                print(f"  - {cnm_file['name']} (type: {cnm_file['type']}, size: {cnm_file['size']}, checksum: {cnm_file['checksumType']})")
            print(f"📂 No archiving_types filter: All asset types and extensions included")
            print(f"🎯 Asset types found: {sorted(extracted_types)}")
            print(f"🔐 Checksum types found: {sorted(extracted_checksum_types)}")

    def test_archive_granules_concurrent_processing(self):
        """
        Test archive_granules method with concurrent processing:
        1. Creates multiple mock granule JSON objects
        2. Mocks the archive_granule_json method to simulate different outcomes
        3. Verifies parallel processing works correctly
        4. Checks success/failure tracking and logging
        5. Verifies thread safety with separate archiver instances
        """
        import time
        from unittest.mock import call

        # Create test granule JSON objects (simulating STAC Fast API response)
        test_granules = [
            {
                'id': f'granule_{i:03d}',
                'collection': 'test_collection',
                'type': 'Feature',
                'geometry': {
                    "type": "Polygon",
                    "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
                },
                'properties': {
                    'datetime': '2024-01-01T00:00:00Z'
                },
                'assets': {
                    f'data_{i:03d}.nc': {
                        'href': f's3://test-bucket/data_{i:03d}.nc',
                        'roles': ['data'],
                        'type': 'application/netcdf'
                    }
                }
            }
            for i in range(10)  # Create 10 test granules
        ]

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.DaacArchiverCatalia.archive_granule_json', autospec=True) as mock_archive_granule_json:

            # Setup mocks
            mock_s3 = Mock()
            mock_s3_class.return_value = mock_s3
            mock_sns = Mock()
            mock_sns_class.return_value = mock_sns
            mock_sfa_client = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

            # Track calls to archive_granule_json to verify concurrent execution
            call_times = []
            processed_granule_ids = []

            def mock_archive_granule_json_impl(self):
                """Mock implementation that simulates processing time and tracks calls"""
                # Get the granule ID from the current archiver instance
                current_granule = self._DaacArchiverCatalia__archiving_granules_stac
                granule_id = current_granule.get('id', 'unknown') if isinstance(current_granule, dict) else current_granule.id

                # # Record call time and granule ID
                call_times.append(time.time())
                processed_granule_ids.append(granule_id)

                # Simulate different processing outcomes based on granule ID
                if granule_id == 'granule_003':
                    # Simulate a failure for granule_003
                    raise RuntimeError(f"Simulated failure for {granule_id}")
                elif granule_id == 'granule_007':
                    # Simulate another failure for granule_007
                    raise ValueError(f"Validation error for {granule_id}")
                else:
                    # Simulate successful processing with some delay
                    time.sleep(0.1)  # Small delay to simulate real processing
                    return self
                return self

            # Apply the mock implementation
            mock_archive_granule_json.side_effect = mock_archive_granule_json_impl

            # Create main archiver instance
            archiver = DaacArchiverCatalia()
            archiver._DaacArchiverCatalia__staged_s3_bucket = 'test-staged-bucket'
            archiver._DaacArchiverCatalia__daac_agreements = [
                {
                    'daac_collection_name': 'TEST_COLLECTION',
                    'daac_data_version': '1.0',
                    'daac_provider': 'test_provider',
                    'daac_sns_topic_arn': 'arn:aws:sns:us-west-2:123456789012:test-topic',
                    'daac_role_arn': 'arn:aws:iam::123456789012:role/test-role',
                    'daac_role_session_name': 'test-session'
                }
            ]

            # Record start time
            start_time = time.time()

            # Call archive_granules with different worker counts for testing
            result = archiver.archive_granules(test_granules, max_workers=5)

            # Record end time
            end_time = time.time()
            total_execution_time = end_time - start_time

            # Verify method returns self

            # Verify archive_granule_json was called for each granule
            expected_call_count = len(test_granules)
            self.assertEqual(mock_archive_granule_json.call_count, expected_call_count,
                           f"archive_granule_json should be called {expected_call_count} times")

            # Verify all granules were processed (including failed ones)
            expected_granule_ids = {granule['id'] for granule in test_granules}
            actual_granule_ids = set(processed_granule_ids)
            self.assertEqual(actual_granule_ids, expected_granule_ids,
                           f"All granules should be processed. Expected: {expected_granule_ids}, Got: {actual_granule_ids}")

            # Verify concurrent execution occurred (total time should be less than sequential)
            sequential_time_estimate = len(test_granules) * 0.1  # 0.1s per granule
            self.assertLess(total_execution_time, sequential_time_estimate * 0.8,
                          f"Execution should be faster than sequential. Total: {total_execution_time:.2f}s, Sequential estimate: {sequential_time_estimate:.2f}s")

            # Verify parallel execution by checking call time distribution
            if len(call_times) > 1:
                # Check that calls started within a reasonable window (parallel execution)
                call_time_range = max(call_times) - min(call_times)
                # Most calls should start within first 0.5 seconds (parallel startup)
                early_calls = [t for t in call_times if t - min(call_times) < 0.5]
                self.assertGreaterEqual(len(early_calls), min(5, len(test_granules)),
                                      f"At least {min(5, len(test_granules))} calls should start early (parallel execution)")

            # Test with empty granule list
            result_empty = archiver.archive_granules([])
            self.assertEqual(result_empty, archiver, "archive_granules should handle empty list")

            # Reset mock call count for next test
            mock_archive_granule_json.reset_mock()
            call_times.clear()
            processed_granule_ids.clear()

            # Test with single granule
            single_granule = [test_granules[0]]
            result_single = archiver.archive_granules(single_granule, max_workers=1)
            self.assertEqual(result_single, archiver, "archive_granules should handle single granule")
            self.assertEqual(mock_archive_granule_json.call_count, 1, "Should call archive_granule_json once for single granule")

            print(f"✅ Test passed! Concurrent processing verification:")
            print(f"  - Processed {len(test_granules)} granules concurrently")
            print(f"  - Total execution time: {total_execution_time:.2f}s (vs {sequential_time_estimate:.2f}s sequential)")
            print(f"  - Expected failures occurred for granule_003 and granule_007")
            print(f"  - Thread safety verified with separate archiver instances")

    def test_archive_granules_error_handling_and_isolation(self):
        """
        Test archive_granules method error handling and failure isolation:
        1. Creates granules with different failure scenarios
        2. Verifies individual failures don't stop other processing
        3. Checks error logging and result tracking
        4. Tests edge cases and validation
        """
        import time
        from unittest.mock import call

        # Create test granules with various scenarios
        test_granules = [
            # Normal granules that should succeed
            {'id': 'success_001', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T00:00:00Z'}, 'assets': {}},
            {'id': 'success_002', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T01:00:00Z'}, 'assets': {}},
            {'id': 'success_003', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T02:00:00Z'}, 'assets': {}},
            # Granules that will fail
            {'id': 'fail_network', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T03:00:00Z'}, 'assets': {}},
            {'id': 'fail_validation', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T04:00:00Z'}, 'assets': {}},
            # More successful granules to verify isolation
            {'id': 'success_004', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T05:00:00Z'}, 'assets': {}},
            {'id': 'success_005', 'collection': 'test_collection', 'type': 'Feature', 'properties': {'datetime': '2024-01-01T06:00:00Z'}, 'assets': {}},
        ]

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.DaacArchiverCatalia.archive_granule_json', autospec=True) as mock_archive_granule_json:

            # Setup mocks
            mock_s3 = Mock()
            mock_s3_class.return_value = mock_s3
            mock_sns = Mock()
            mock_sns_class.return_value = mock_sns
            mock_sfa_client = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = mock_sfa_client

            # Track processing results
            processing_results = {}

            def mock_archive_granule_json_impl(self):
                """Mock implementation with controlled failures"""
                current_granule = self._DaacArchiverCatalia__archiving_granules_stac
                granule_id = current_granule.get('id', 'unknown') if isinstance(current_granule, dict) else current_granule.id

                # Simulate different failure types
                if granule_id == 'fail_network':
                    processing_results[granule_id] = 'network_error'
                    raise ConnectionError("Network timeout during archival process")
                elif granule_id == 'fail_validation':
                    processing_results[granule_id] = 'validation_error'
                    raise ValueError("Invalid granule metadata format")
                else:
                    # Successful processing
                    processing_results[granule_id] = 'success'
                    time.sleep(0.05)  # Small delay to simulate processing
                    return self

            mock_archive_granule_json.side_effect = mock_archive_granule_json_impl

            # Create archiver instance
            archiver = DaacArchiverCatalia()
            archiver._DaacArchiverCatalia__staged_s3_bucket = 'test-staged-bucket'
            archiver._DaacArchiverCatalia__daac_agreements = [{'test': 'agreement'}]

            # Capture log messages to verify error logging
            with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.LOGGER') as mock_logger:
                # Execute archive_granules
                result = archiver.archive_granules(test_granules, max_workers=3)

                # Verify method returns self even with failures
                self.assertEqual(result, archiver, "archive_granules should return self even with failures")

                # Verify all granules were processed
                self.assertEqual(len(processing_results), len(test_granules),
                               f"All {len(test_granules)} granules should be processed")

                # Verify success and failure counts
                successful_granules = [gid for gid, status in processing_results.items() if status == 'success']
                failed_granules = [gid for gid, status in processing_results.items() if status != 'success']

                expected_successful = ['success_001', 'success_002', 'success_003', 'success_004', 'success_005']
                expected_failed = ['fail_network', 'fail_validation']

                self.assertEqual(set(successful_granules), set(expected_successful),
                               f"Expected successful granules: {expected_successful}, Got: {successful_granules}")
                self.assertEqual(set(failed_granules), set(expected_failed),
                               f"Expected failed granules: {expected_failed}, Got: {failed_granules}")

                # Verify archive_granule_json was called for each granule
                self.assertEqual(mock_archive_granule_json.call_count, len(test_granules),
                               f"archive_granule_json should be called {len(test_granules)} times")

                # Verify error logging occurred
                error_calls = [call for call in mock_logger.error.call_args_list if call[0]]
                self.assertGreaterEqual(len(error_calls), 2, "Should log errors for failed granules")

                # Check that error messages contain granule IDs
                error_messages = [str(call[0][0]) for call in error_calls]
                self.assertTrue(any('fail_network' in msg for msg in error_messages),
                              "Should log error for fail_network granule")
                self.assertTrue(any('fail_validation' in msg for msg in error_messages),
                              "Should log error for fail_validation granule")

                # Verify info logging occurred
                info_calls = [call for call in mock_logger.info.call_args_list if call[0]]
                self.assertGreater(len(info_calls), 0, "Should log info messages during processing")

                # Check completion summary was logged
                completion_messages = [str(call[0][0]) for call in info_calls]
                completion_summary = next((msg for msg in completion_messages if 'Parallel archival completed' in msg), None)
                self.assertIsNotNone(completion_summary, "Should log completion summary")

                # Verify summary contains correct counts
                self.assertIn(f'{len(successful_granules)}/{len(test_granules)} successful', completion_summary)
                self.assertIn(f'{len(failed_granules)} failed', completion_summary)

            print(f"✅ Test passed! Error handling and isolation verification:")
            print(f"  - Processed {len(test_granules)} granules with mixed success/failure")
            print(f"  - Successful: {len(successful_granules)}, Failed: {len(failed_granules)}")
            print(f"  - Failures were isolated and didn't stop other processing")
            print(f"  - Error logging verified for all failure types")
            print(f"  - Method returned successfully despite individual failures")

    def test_archive_granules_thread_safety_validation(self):
        """
        Test archive_granules method thread safety:
        1. Verifies each worker gets its own DaacArchiverCatalia instance
        2. Checks that configuration is properly copied to worker instances
        3. Validates no shared state issues between workers
        4. Tests worker instance isolation
        """
        # Create test granules
        test_granules = [
            {'id': f'thread_test_{i}', 'collection': 'test_collection', 'type': 'Feature',
             'properties': {'datetime': '2024-01-01T00:00:00Z'}, 'assets': {}}
            for i in range(6)
        ]

        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsSns') as mock_sns_class, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.SFAClientFactory') as mock_sfa_factory, \
             patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.DaacArchiverCatalia.archive_granule_json', autospec=True) as mock_archive_granule_json:

            # Setup mocks
            mock_s3_class.return_value = Mock()
            mock_sns_class.return_value = Mock()
            mock_sfa_factory.return_value.get_instance_from_env.return_value = Mock()

            # Track worker instances and their configurations
            worker_instances = []
            worker_configs = []
            processed_granules_by_instance = {}

            def mock_archive_granule_json_impl(instance):
                """Mock that tracks worker instances and their configurations"""
                # Record this worker instance
                instance_id = id(instance)  # Unique identifier for each instance
                if instance_id not in processed_granules_by_instance:
                    processed_granules_by_instance[instance_id] = []
                    worker_instances.append(instance)
                    # Capture configuration
                    worker_configs.append({
                        'instance_id': instance_id,
                        'staged_s3_bucket': instance._DaacArchiverCatalia__staged_s3_bucket,
                        'daac_agreements': instance._DaacArchiverCatalia__daac_agreements,
                        'current_granule_id': instance._DaacArchiverCatalia__archiving_granules_stac.get('id')
                    })

                # Track which granule this instance is processing
                current_granule = instance._DaacArchiverCatalia__archiving_granules_stac
                granule_id = current_granule.get('id', 'unknown')
                processed_granules_by_instance[instance_id].append(granule_id)

                return instance

            mock_archive_granule_json.side_effect = mock_archive_granule_json_impl

            # Create main archiver instance with specific configuration
            main_archiver = DaacArchiverCatalia()
            main_archiver._DaacArchiverCatalia__staged_s3_bucket = 'main-staged-bucket'
            main_archiver._DaacArchiverCatalia__daac_agreements = [
                {'daac_name': 'test_daac', 'config': 'main_config'}
            ]

            # Execute archive_granules
            result = main_archiver.archive_granules(test_granules, max_workers=3)

            # Verify method returns self
            self.assertEqual(result, main_archiver, "archive_granules should return main archiver instance")

            # Verify multiple worker instances were created
            unique_instance_ids = set(id(instance) for instance in worker_instances)
            self.assertGreater(len(unique_instance_ids), 1, "Multiple worker instances should be created")
            self.assertLessEqual(len(unique_instance_ids), len(test_granules),
                               "Should not create more instances than granules")

            # Verify main archiver is not used as worker (thread safety)
            main_instance_id = id(main_archiver)
            worker_instance_ids = {id(instance) for instance in worker_instances}
            self.assertNotIn(main_instance_id, worker_instance_ids,
                           "Main archiver instance should not be used as worker")

            # Verify each worker instance has correct configuration
            for config in worker_configs:
                self.assertEqual(config['staged_s3_bucket'], 'main-staged-bucket',
                               f"Worker instance {config['instance_id']} should have correct staged_s3_bucket")
                self.assertEqual(config['daac_agreements'], [{'daac_name': 'test_daac', 'config': 'main_config'}],
                               f"Worker instance {config['instance_id']} should have correct daac_agreements")
                self.assertIn(config['current_granule_id'], [g['id'] for g in test_granules],
                             f"Worker instance {config['instance_id']} should process valid granule")

            # Verify all granules were processed exactly once
            all_processed_granules = []
            for granules_list in processed_granules_by_instance.values():
                all_processed_granules.extend(granules_list)

            expected_granule_ids = [g['id'] for g in test_granules]
            self.assertEqual(sorted(all_processed_granules), sorted(expected_granule_ids),
                           "All granules should be processed exactly once")

            # Verify no granule was processed by multiple instances
            granule_processing_count = {}
            for granule_id in all_processed_granules:
                granule_processing_count[granule_id] = granule_processing_count.get(granule_id, 0) + 1

            for granule_id, count in granule_processing_count.items():
                self.assertEqual(count, 1, f"Granule {granule_id} should be processed exactly once, got {count}")

            # Verify worker instances are separate classes (not the same instance reused)
            worker_classes = [type(instance) for instance in worker_instances]
            expected_class = DaacArchiverCatalia
            for worker_class in worker_classes:
                self.assertEqual(worker_class, expected_class, "All workers should be DaacArchiverCatalia instances")

            # Test edge case: max_workers larger than granule count
            worker_instances.clear()
            worker_configs.clear()
            processed_granules_by_instance.clear()

            single_granule = [test_granules[0]]
            result_single = main_archiver.archive_granules(single_granule, max_workers=10)
            self.assertEqual(result_single, main_archiver, "Should handle max_workers > granule count")

            # Should only create one worker instance for one granule
            unique_instance_ids_single = set(id(instance) for instance in worker_instances)
            self.assertEqual(len(unique_instance_ids_single), 1, "Should create only one worker for one granule")

            print(f"✅ Test passed! Thread safety validation:")
            print(f"  - Created {len(unique_instance_ids)} separate worker instances")
            print(f"  - Main archiver instance isolated from workers")
            print(f"  - Configuration correctly copied to all workers")
            print(f"  - Each granule processed by exactly one worker instance")
            print(f"  - No shared state issues detected")


