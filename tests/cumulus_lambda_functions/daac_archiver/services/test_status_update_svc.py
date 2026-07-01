import os
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock
from cumulus_lambda_functions.daac_archiver.services.status_update_svc import StatusUpdateSvc

class TestStatusUpdateSvc(TestCase):

    def test_update_status_01(self):
        """
        Write a test case for from StatusUpdateSvc update_status_wrapper

        Mock 2 DDB MW classes since I don't want to hit DDBs.
        self.__uds_ctla_archiving_traces = CataliaArchivingTraces(os.getenv('CATALYA_TRACING_DB', None))
        self.__status_ddb = CataliaStatusDb(os.getenv('CATALYA_STATUS_DB', None))
        Similar to with patch('cumulus_lambda_functions.daac_archiver.daac_archiver_catalia.AwsS3') as mock_s3_class

        I want 2 updates where the first item is missing and 2nd item found something in ddb when hitting this line "existing_statuses = self.__status_ddb.get"

        I want 2 updates for each, success and failure where the result should have relative keys.
        I want to make sure timestamp is added.

        Oh.. when SfaClientMw is called, make sure it's not triggered by setting the env var "UPDATE_STATUS_TO_SFA" = FALSE
        :return:
        """
        # Set environment variable to disable SFA client updates
        with patch.dict(os.environ, {'UPDATE_STATUS_TO_SFA': 'FALSE'}):
            # Mock the DDB classes
            with patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.CataliaArchivingTraces') as MockArchivingTraces, \
                 patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.CataliaStatusDb') as MockStatusDb, \
                 patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.SfaClientMw') as MockSfaClientMw:

                # Configure the mock class to have the correct class attributes
                # This is crucial because the actual code uses CataliaStatusDb.collection as a dictionary key
                MockStatusDb.collection = 'collection'
                MockStatusDb.name_str = 'name'
                MockStatusDb.identifier = 'identifier'
                MockStatusDb.status = 'status'
                MockStatusDb.error_code = 'errorCode'
                MockStatusDb.error_message = 'errorMessage'
                MockStatusDb.href_str = 'href'
                MockStatusDb.datetime_str = 'datetime'

                # Setup mock instances
                mock_archiving_traces = MagicMock()
                mock_status_db = MagicMock()
                MockArchivingTraces.return_value = mock_archiving_traces
                MockStatusDb.return_value = mock_status_db

                # Test Case 1: Identifier not found in DDB (should raise ValueError)
                print("\n=== Test Case 1: Missing identifier in DDB ===")
                mock_status_db.get.return_value = []  # Empty list means not found

                svc = StatusUpdateSvc()

                cnm_msg_missing = {
                    'identifier': 'missing-identifier-123',
                    'response': {
                        'status': 'SUCCESS'
                    }
                }

                with self.assertRaises(ValueError) as context:
                    svc.update_status_wrapper(cnm_msg_missing)

                self.assertIn('unknown collection & granule', str(context.exception))
                print(f"✓ Correctly raised ValueError for missing identifier: {context.exception}")

                # Test Case 2a: Identifier found in DDB - SUCCESS status
                print("\n=== Test Case 2a: Found identifier - SUCCESS status ===")
                mock_status_db.get.return_value = [{
                    'collection': 'test-collection',
                    'name': 'test-granule-id'
                }]

                # Reset mock to track calls
                mock_status_db.add.reset_mock()

                svc2 = StatusUpdateSvc()

                cnm_msg_success = {
                    'identifier': 'success-identifier-456',
                    'response': {
                        'status': 'SUCCESS'
                    }
                }

                svc2.update_status_wrapper(cnm_msg_success)

                # Verify status_ddb.add was called
                self.assertTrue(mock_status_db.add.called, "status_ddb.add should be called")
                add_call_args = mock_status_db.add.call_args

                # Verify the arguments
                self.assertEqual(add_call_args[0][0], 'success-identifier-456', "Identifier should match")
                self.assertEqual(add_call_args[0][1], 'test-collection', "Collection should match")
                self.assertEqual(add_call_args[0][2], 'test-granule-id', "Granule ID should match")
                self.assertEqual(add_call_args[0][3], 'cnm-receive-success', "Status should be cnm-receive-success")

                # Verify timestamp is present and properly formatted
                timestamp = add_call_args[0][4]
                self.assertIsNotNone(timestamp, "Timestamp should be present")
                self.assertTrue(timestamp.endswith('Z'), "Timestamp should end with 'Z'")
                print(f"✓ Success status update called with timestamp: {timestamp}")

                # Test Case 2b: Identifier found in DDB - FAILURE status
                print("\n=== Test Case 2b: Found identifier - FAILURE status ===")
                mock_status_db.get.return_value = [{
                    'collection': 'test-collection-2',
                    'name': 'test-granule-id-2'
                }]

                # Reset mock to track calls
                mock_status_db.add.reset_mock()

                svc3 = StatusUpdateSvc()

                cnm_msg_failure = {
                    'identifier': 'failure-identifier-789',
                    'response': {
                        'status': 'FAILED',
                        'errorCode': 'TEST_ERROR_CODE',
                        'errorMessage': 'Test error message from DAAC'
                    }
                }

                svc3.update_status_wrapper(cnm_msg_failure)

                # Verify status_ddb.add was called
                self.assertTrue(mock_status_db.add.called, "status_ddb.add should be called for failure")
                add_call_args_failure = mock_status_db.add.call_args

                # Verify the arguments
                self.assertEqual(add_call_args_failure[0][0], 'failure-identifier-789', "Identifier should match")
                self.assertEqual(add_call_args_failure[0][1], 'test-collection-2', "Collection should match")
                self.assertEqual(add_call_args_failure[0][2], 'test-granule-id-2', "Granule ID should match")
                self.assertEqual(add_call_args_failure[0][3], 'cnm-receive-failed', "Status should be cnm-receive-failed")

                # Verify timestamp
                timestamp_failure = add_call_args_failure[0][4]
                self.assertIsNotNone(timestamp_failure, "Timestamp should be present")
                self.assertTrue(timestamp_failure.endswith('Z'), "Timestamp should end with 'Z'")

                # Verify error details are passed
                error_code = add_call_args_failure[0][5]
                error_message = add_call_args_failure[0][6]
                self.assertEqual(error_code, 'TEST_ERROR_CODE', "Error code should match")
                self.assertEqual(error_message, 'Test error message from DAAC', "Error message should match")

                print(f"✓ Failure status update called with timestamp: {timestamp_failure}")
                print(f"✓ Error code: {error_code}")
                print(f"✓ Error message: {error_message}")

                # Verify SfaClientMw was called (even though UPDATE_STATUS_TO_SFA is FALSE)
                # The service still calls it, but the SfaClientMw implementation checks the env var
                self.assertTrue(MockSfaClientMw.called, "SfaClientMw should be instantiated")

                print("\n=== All test cases passed ===")
                return

    def test_update_s3_url_from_traces_tbl(self):
        """
        Write a test case where
        1. archival status is not the cnm-receive-success. So, it quits
        2. It can't find it in the Traces DDB (which is mocked). So, it quits
        3. It found it and it should have a mock S3 URL.
        4. Make sure the correct updated URL is used to push S3. and the file is correct.
        :return:
        """
        # Mock dependencies
        with patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.CataliaArchivingTraces') as MockArchivingTraces, \
             patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.CataliaStatusDb') as MockStatusDb, \
             patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.AwsS3') as MockAwsS3:

            # Configure the mock class to have the correct class attributes
            MockStatusDb.collection = 'collection'
            MockStatusDb.name_str = 'name'

            # Setup mock instances
            mock_archiving_traces = MagicMock()

            MockArchivingTraces.identifier = 'identifier'
            MockArchivingTraces.s3_url = 's3Url'
            MockArchivingTraces.collection = 'collection'
            MockArchivingTraces.granule_id = 'granule'
            MockArchivingTraces.username = 'username'
            MockArchivingTraces.user_group = 'userGroup'
            MockArchivingTraces.datetime_str = 'datetime'

            mock_status_db = MagicMock()
            mock_s3 = MagicMock()

            MockArchivingTraces.return_value = mock_archiving_traces
            MockStatusDb.return_value = mock_status_db
            MockAwsS3.return_value = mock_s3

            # Mock S3 chaining methods
            mock_s3.set_s3_url.return_value = mock_s3
            mock_s3.upload_bytes.return_value = None

            # Test Case 1: Status is NOT cnm-receive-success (should quit early)
            print("\n=== Test Case 1: Status is NOT cnm-receive-success ===")

            svc1 = StatusUpdateSvc()
            svc1.load_manually('identifier-1', 'test-collection', 'test-granule')

            status_not_success = {
                'status': 'cnm-submit-success',  # Different status
                'datetime': '2024-01-01T00:00:00Z'
            }

            # Reset mocks
            mock_archiving_traces.get.reset_mock()
            mock_s3.set_s3_url.reset_mock()

            result1 = svc1.update_s3_url_from_traces_tbl(status_not_success)

            # Verify method returned early without calling traces or S3
            self.assertFalse(mock_archiving_traces.get.called,
                           "Should not call traces.get() when status is not cnm-receive-success")
            self.assertFalse(mock_s3.set_s3_url.called,
                           "Should not call S3 operations when status is not cnm-receive-success")
            self.assertEqual(result1, svc1, "Should return self")
            print("✓ Method quit early when status is not cnm-receive-success")
            print("✓ No traces or S3 operations performed")

            # Test Case 2: Entry not found in Traces DDB (should quit early)
            print("\n=== Test Case 2: Entry not found in Traces DDB ===")

            svc2 = StatusUpdateSvc()
            svc2.load_manually('identifier-2', 'test-collection', 'test-granule')

            # Mock traces.get to return empty list (not found)
            mock_archiving_traces.get.return_value = []

            status_success = {
                'status': 'cnm-receive-success',
                'datetime': '2024-01-01T01:00:00Z'
            }

            # Reset S3 mock
            mock_s3.set_s3_url.reset_mock()

            result2 = svc2.update_s3_url_from_traces_tbl(status_success)

            # Verify traces was queried but S3 was not called
            self.assertTrue(mock_archiving_traces.get.called,
                          "Should call traces.get() to check for entry")
            mock_archiving_traces.get.assert_called_with('identifier-2')
            self.assertFalse(mock_s3.set_s3_url.called,
                           "Should not call S3 when trace entry not found")
            self.assertEqual(result2, svc2, "Should return self")
            print("✓ Method quit early when trace entry not found")
            print("✓ Traces queried but no S3 operations performed")

            # Test Case 3: Entry found - should upload to S3 with correct URL
            print("\n=== Test Case 3: Entry found - upload to S3 ===")

            svc3 = StatusUpdateSvc()
            svc3.load_manually('identifier-3', 'test-collection-3', 'test-granule-3')

            # Mock traces.get to return a valid entry with S3 URL
            base_s3_url = 's3://test-bucket/path/to/catalog.json'
            mock_archiving_traces.get.return_value = [{
                's3Url': base_s3_url,
                'collection': 'test-collection-3',
                'granule': 'test-granule-3',
                'username': 'test-user',
                'datetime': '2024-01-01T00:00:00Z'
            }]

            status_success_with_time = {
                'status': 'cnm-receive-success',
                'datetime': '2024-01-01T02:00:00Z'
            }

            # Reset mocks
            mock_s3.set_s3_url.reset_mock()
            mock_s3.upload_bytes.reset_mock()

            result3 = svc3.update_s3_url_from_traces_tbl(status_success_with_time)

            # Verify traces was queried
            self.assertTrue(mock_archiving_traces.get.called,
                          "Should call traces.get() to retrieve entry")
            mock_archiving_traces.get.assert_called_with('identifier-3')

            # Verify S3 URL was constructed correctly
            expected_s3_url = f'{base_s3_url}.cnm_r.{status_success_with_time["datetime"]}'
            mock_s3.set_s3_url.assert_called_once_with(expected_s3_url)
            print(f"✓ S3 URL constructed correctly: {expected_s3_url}")

            # Verify upload_bytes was called
            self.assertTrue(mock_s3.upload_bytes.called,
                          "Should call upload_bytes to write status to S3")

            # Verify the uploaded content
            upload_call_args = mock_s3.upload_bytes.call_args
            uploaded_bytes = upload_call_args[0][0]
            uploaded_content = uploaded_bytes.decode('utf-8')
            uploaded_json = json.loads(uploaded_content)

            # Verify uploaded JSON contains expected fields
            self.assertEqual(uploaded_json['status'], 'cnm-receive-success',
                           "Uploaded content should have correct status")
            self.assertEqual(uploaded_json['datetime'], '2024-01-01T02:00:00Z',
                           "Uploaded content should have correct datetime")
            self.assertEqual(uploaded_json['identifier'], 'identifier-3',
                           "Uploaded content should have correct identifier")
            self.assertEqual(uploaded_json['collection'], 'test-collection-3',
                           "Uploaded content should have correct collection")
            self.assertEqual(uploaded_json['id'], 'test-granule-3',
                           "Uploaded content should have correct granule id")

            print(f"✓ Uploaded content has correct fields:")
            print(f"  - status: {uploaded_json['status']}")
            print(f"  - datetime: {uploaded_json['datetime']}")
            print(f"  - identifier: {uploaded_json['identifier']}")
            print(f"  - collection: {uploaded_json['collection']}")
            print(f"  - id: {uploaded_json['id']}")

            self.assertEqual(result3, svc3, "Should return self")

            # Test Case 4: Multiple entries found (should warn but use first one)
            print("\n=== Test Case 4: Multiple entries found (uses first) ===")

            svc4 = StatusUpdateSvc()
            svc4.load_manually('identifier-4', 'test-collection-4', 'test-granule-4')

            # Mock traces.get to return multiple entries
            base_s3_url_multi = 's3://test-bucket/path/to/catalog2.json'
            mock_archiving_traces.get.return_value = [
                {
                    's3Url': base_s3_url_multi,
                    'collection': 'test-collection-4',
                    'granule': 'test-granule-4',
                },
                {
                    's3Url': 's3://test-bucket/duplicate.json',
                    'collection': 'test-collection-4',
                    'granule': 'test-granule-4',
                }
            ]

            status_multi = {
                'status': 'cnm-receive-success',
                'datetime': '2024-01-01T03:00:00Z'
            }

            # Reset mocks
            mock_s3.set_s3_url.reset_mock()
            mock_s3.upload_bytes.reset_mock()

            # Capture warnings
            with patch('cumulus_lambda_functions.daac_archiver.services.status_update_svc.LOGGER') as mock_logger:
                result4 = svc4.update_s3_url_from_traces_tbl(status_multi)

                # Verify warning was logged
                warning_calls = [call for call in mock_logger.warning.call_args_list if call[0]]
                self.assertGreater(len(warning_calls), 0, "Should log warning for duplicate identifiers")

            # Verify S3 URL uses the first entry
            expected_s3_url_multi = f'{base_s3_url_multi}.cnm_r.{status_multi["datetime"]}'
            mock_s3.set_s3_url.assert_called_once_with(expected_s3_url_multi)
            print(f"✓ Used first entry despite duplicates: {expected_s3_url_multi}")
            print("✓ Warning logged for duplicate identifiers")

            print("\n=== All test cases passed ===")
            return
