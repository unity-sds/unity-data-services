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

