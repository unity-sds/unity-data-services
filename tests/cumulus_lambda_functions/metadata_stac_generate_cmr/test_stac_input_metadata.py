import json
from unittest import TestCase

from pystac import Item, Asset

from cumulus_lambda_functions.metadata_stac_generate_cmr.stac_input_metadata import StacInputMetadata
from mdps_ds_lib.lib.utils.time_utils import TimeUtils


class TestStacInputMetadata(TestCase):
    def test_01(self):
        custom_metadata_core = {
            "custom_entry_1": "test1",
            "custom_entry_2": True,
            "custom_entry_3": 3.14159,
            "custom_entry_4": -20107,
        }
        stac_item = Item(id='sample_granule_id',
                         geometry={
                             "type": "Point",
                             "coordinates": [0.0, 0.0]
                         },
                         bbox=[0.0, 0.0, 0.0, 0.0],
                         datetime=TimeUtils().parse_from_unix(9876543210, True).get_datetime_obj(),
                         properties={
                             **custom_metadata_core,
                             "start_datetime": "2016-01-31T18:00:00.009057Z",
                             "end_datetime": "2016-01-31T19:59:59.991043Z",
                             "created": "2016-02-01T02:45:59.639000Z",
                             "updated": "2022-03-23T15:48:21.578000Z",
                             "datetime": "2022-03-23T15:48:19.079000Z",
                         },
                         collection='sample_collection___23',
                         assets={
                             'data': Asset('test_file01.nc', title='main data'),
                             'metadata__cas': Asset('test_file01.nc.cas', title='metadata cas'),
                             'metadata__stac': Asset('test_file01.nc.stac.json', title='metadata stac'),
                         })
        stac_item_dict = stac_item.to_dict(False, False)
        stac_metadata = StacInputMetadata(stac_item_dict)
        granule_metadata_props = stac_metadata.start()
        self.assertEqual(granule_metadata_props.granule_id, stac_item.id, f'wrong granule id')
        self.assertEqual(granule_metadata_props.collection_name, stac_item.collection_id.split('___')[0], f'wrong collection_name')
        self.assertEqual(granule_metadata_props.collection_version, stac_item.collection_id.split('___')[1], f'wrong collection_version')
        self.assertEqual(granule_metadata_props.prod_dt, TimeUtils().parse_from_unix(stac_item.datetime.timestamp()).get_datetime_str(fmt='%Y-%m-%dT%H:%M:%S.%fZ'), f'wrong prod_dt')
        self.assertEqual(granule_metadata_props.beginning_dt, stac_item.properties['start_datetime'], f'wrong prod_dt')
        self.assertEqual(granule_metadata_props.ending_dt, stac_item.properties['end_datetime'], f'wrong prod_dt')
        expected_custom = {
            **custom_metadata_core,
            # 'granule_id': stac_item.id,
            # 'collection_id': stac_item.collection_id
        }
        self.assertEqual(sorted(json.dumps(expected_custom)), sorted(json.dumps(stac_metadata.custom_properties)), f'mismatch: {stac_metadata.custom_properties}, {expected_custom}')
        return

    def test_02(self):
        stac_item = Item(id='sample_granule_id',
                         geometry={
                             "type": "Point",
                             "coordinates": [0.0, 0.0]
                         },
                         bbox=[0.0, 0.0, 0.0, 0.0],
                         datetime=TimeUtils().parse_from_unix(11210045, True).get_datetime_obj(),
                         properties={
                             "start_datetime": "2016-01-31T18:00:00.009057Z",
                             "end_datetime": "2016-01-31T19:59:59.991043Z",
                             "created": "2016-02-01T02:45:59.639000Z",
                             "updated": "2022-03-23T15:48:21.578000Z",
                             "datetime": "2022-03-23T15:48:19.079000Z"
                         },
                         collection='sample_collection_23',
                         assets={
                             'data': Asset('test_file01.nc', title='main data'),
                             'metadata__cas': Asset('test_file01.nc.cas', title='metadata cas'),
                             'metadata__stac': Asset('test_file01.nc.stac.json', title='metadata stac'),
                         })
        stac_item_dict = stac_item.to_dict(False, False)
        stac_metadata = StacInputMetadata(stac_item_dict)
        granule_metadata_props = stac_metadata.start()
        self.assertEqual(granule_metadata_props.granule_id, stac_item.id, f'wrong granule id')
        self.assertEqual(granule_metadata_props.collection_name, 'sample_collection_23', f'wrong collection_name')
        self.assertEqual(granule_metadata_props.collection_version, '', f'wrong collection_version')
        self.assertEqual(granule_metadata_props.prod_dt, TimeUtils().parse_from_unix(stac_item.datetime.timestamp()).get_datetime_str(fmt='%Y-%m-%dT%H:%M:%S.%fZ'), f'wrong prod_dt')
        self.assertEqual(granule_metadata_props.beginning_dt, stac_item.properties['start_datetime'], f'wrong prod_dt')
        self.assertEqual(granule_metadata_props.ending_dt, stac_item.properties['end_datetime'], f'wrong prod_dt')
        return
