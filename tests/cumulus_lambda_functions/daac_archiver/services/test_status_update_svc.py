import os
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
