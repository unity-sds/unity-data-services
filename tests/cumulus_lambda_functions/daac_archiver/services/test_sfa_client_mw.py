import uuid
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from pystac import Item
from cumulus_lambda_functions.daac_archiver.services.sfa_client_mw import SfaClientMw


class TestSfaClientMw(TestCase):
    def test_01_add_archival_extension(self):
        """
        Write a test for add_archival_extension to see if the extension is added, and empty array is added in the properties.
        Create multiple items to see if it is added if missing, and not duplicating it if exists. Same thing for Properties
        :return:
        """
        extension_url = SfaClientMw.archiving_status_extension_url

        # Test Case 1: Item without stac_extensions (should add extension and property)
        print("\n=== Test Case 1: Item without stac_extensions ===")
        item1 = Item(
            id='test-item-1',
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}
        )
        # Ensure no stac_extensions
        item1.stac_extensions = []

        result1 = SfaClientMw.add_archival_extension(item1)

        # Verify extension was added
        self.assertIn(extension_url, result1.stac_extensions,
                      "Extension URL should be added to stac_extensions")
        self.assertEqual(len(result1.stac_extensions), 1,
                        "Should have exactly 1 extension")

        # Verify archival:status property was initialized
        self.assertIn('archival:status', result1.properties,
                      "archival:status property should be added")
        self.assertEqual(result1.properties['archival:status'], [],
                        "archival:status should be an empty array")
        print("✓ Extension added to item without stac_extensions")
        print("✓ archival:status property initialized as empty array")

        # Test Case 2: Item with stac_extensions but missing archival extension
        print("\n=== Test Case 2: Item with stac_extensions but missing archival extension ===")
        item2 = Item(
            id='test-item-2',
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}
        )
        # Add some other extension
        item2.stac_extensions = ['https://example.com/other-extension']

        result2 = SfaClientMw.add_archival_extension(item2)

        # Verify extension was added without removing existing ones
        self.assertIn(extension_url, result2.stac_extensions,
                      "Archival extension should be added")
        self.assertIn('https://example.com/other-extension', result2.stac_extensions,
                      "Existing extension should be preserved")
        self.assertEqual(len(result2.stac_extensions), 2,
                        "Should have 2 extensions")

        # Verify archival:status property was initialized
        self.assertIn('archival:status', result2.properties,
                      "archival:status property should be added")
        self.assertEqual(result2.properties['archival:status'], [],
                        "archival:status should be an empty array")
        print("✓ Extension added without removing existing extensions")
        print("✓ archival:status property initialized")

        # Test Case 3: Item that already has the archival extension (should not duplicate)
        print("\n=== Test Case 3: Item with existing archival extension ===")
        item3 = Item(
            id='test-item-3',
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={}
        )
        # Already has the archival extension
        item3.stac_extensions = [extension_url, 'https://example.com/other']

        result3 = SfaClientMw.add_archival_extension(item3)

        # Verify extension was not duplicated
        extension_count = result3.stac_extensions.count(extension_url)
        self.assertEqual(extension_count, 1,
                        f"Extension should appear exactly once, found {extension_count}")
        self.assertEqual(len(result3.stac_extensions), 2,
                        "Should still have 2 extensions (not duplicated)")

        # Verify archival:status property was initialized
        self.assertIn('archival:status', result3.properties,
                      "archival:status property should be added")
        self.assertEqual(result3.properties['archival:status'], [],
                        "archival:status should be an empty array")
        print("✓ Extension not duplicated when already present")
        print("✓ archival:status property initialized")

        # Test Case 4: Item with existing archival:status property (should not modify)
        print("\n=== Test Case 4: Item with existing archival:status property ===")
        item4 = Item(
            id='test-item-4',
            geometry={
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            bbox=[-180, -90, 180, 90],
            datetime=datetime.now(),
            properties={
                'archival:status': [
                    {'status': 'cnm-submit-success', 'datetime': '2024-01-01T00:00:00Z'}
                ]
            }
        )
        item4.stac_extensions = []

        result4 = SfaClientMw.add_archival_extension(item4)

        # Verify extension was added
        self.assertIn(extension_url, result4.stac_extensions,
                      "Extension should be added")

        # Verify existing archival:status was not modified
        self.assertEqual(len(result4.properties['archival:status']), 1,
                        "archival:status should still have 1 entry")
        self.assertEqual(result4.properties['archival:status'][0]['status'], 'cnm-submit-success',
                        "Existing status entry should be preserved")
        print("✓ Extension added without modifying existing archival:status")
        print("✓ Existing status entries preserved")

        # Test Case 5: Test with dictionary input (should convert to Item)
        print("\n=== Test Case 5: Dictionary input (should convert to Item) ===")
        item5_dict = {
            'type': 'Feature',
            'id': 'test-item-5',
            'geometry': {
                "type": "Polygon",
                "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
            },
            'bbox': [-180, -90, 180, 90],
            'properties': {
                'datetime': '2024-01-01T00:00:00Z'
            },
            'assets': {},
            'links': [],
            'stac_version': '1.0.0'
        }

        result5 = SfaClientMw.add_archival_extension(item5_dict)

        # Verify result is a pystac Item
        self.assertIsInstance(result5, Item,
                             "Result should be a pystac Item object")

        # Verify extension was added
        self.assertIn(extension_url, result5.stac_extensions,
                      "Extension should be added to converted Item")

        # Verify archival:status property was initialized
        self.assertIn('archival:status', result5.properties,
                      "archival:status property should be added")
        self.assertEqual(result5.properties['archival:status'], [],
                        "archival:status should be an empty array")
        print("✓ Dictionary successfully converted to Item")
        print("✓ Extension and property added to converted Item")

        # Test Case 6: Null input (should raise ValueError)
        print("\n=== Test Case 6: Null input (should raise ValueError) ===")
        with self.assertRaises(ValueError) as context:
            SfaClientMw.add_archival_extension(None)

        self.assertIn('NULL archiving granule', str(context.exception),
                      "Should raise ValueError for null input")
        print("✓ Correctly raises ValueError for null input")

        print("\n=== All test cases passed ===")
        return
