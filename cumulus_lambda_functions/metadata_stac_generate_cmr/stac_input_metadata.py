from copy import deepcopy
from pystac import Item

from mdps_ds_lib.lib.cumulus_stac.item_transformer import ItemTransformer
from cumulus_lambda_functions.lib.metadata_extraction.granule_metadata_props import GranuleMetadataProps
from mdps_ds_lib.lib.utils.time_utils import TimeUtils


class StacInputMetadata:
    def __init__(self, input_stac_dict: dict):
        self.__input_stac_dict = input_stac_dict
        self.__beginning_dt = None
        self.__ending_dt = None
        self.__collection_name = None
        self.__collection_version = None
        self.__granule_id = None
        self.__prod_dt = None
        self.__insert_dt = None
        self.__custom_properties = {}

    @property
    def custom_properties(self):
        return self.__custom_properties

    @custom_properties.setter
    def custom_properties(self, val):
        """
        :param val:
        :return: None
        """
        self.__custom_properties = val
        return

    @property
    def beginning_dt(self):
        return self.__beginning_dt

    @beginning_dt.setter
    def beginning_dt(self, val):
        """
        :param val:
        :return: None
        """
        self.__beginning_dt = val
        return

    @property
    def ending_dt(self):
        return self.__ending_dt

    @ending_dt.setter
    def ending_dt(self, val):
        """
        :param val:
        :return: None
        """
        self.__ending_dt = val
        return

    @property
    def collection_name(self):
        return self.__collection_name

    @collection_name.setter
    def collection_name(self, val):
        """
        :param val:
        :return: None
        """
        self.__collection_name = val
        return

    @property
    def collection_version(self):
        return self.__collection_version

    @collection_version.setter
    def collection_version(self, val):
        """
        :param val:
        :return: None
        """
        self.__collection_version = val
        return

    @property
    def granule_id(self):
        return self.__granule_id

    @granule_id.setter
    def granule_id(self, val):
        """
        :param val:
        :return: None
        """
        self.__granule_id = val
        return

    @property
    def prod_dt(self):
        return self.__prod_dt

    @prod_dt.setter
    def prod_dt(self, val):
        """
        :param val:
        :return: None
        """
        self.__prod_dt = val
        return

    @property
    def insert_dt(self):
        return self.__insert_dt

    @insert_dt.setter
    def insert_dt(self, val):
        """
        :param val:
        :return: None
        """
        self.__insert_dt = val
        return

    def __remove_default_keys_in_custom_props(self):
        ignoring_keys = ['start_datetime', 'end_datetime', 'created', 'updated', 'datetime']
        for each_key in ignoring_keys:
            if each_key in self.__custom_properties:
                self.__custom_properties.pop(each_key)
        return
    def start(self) -> GranuleMetadataProps:
        stac_item: Item = ItemTransformer().from_stac(self.__input_stac_dict)
        self.__custom_properties = deepcopy(stac_item.properties)
        self.__remove_default_keys_in_custom_props()
        # self.__custom_properties['collection_id'] = stac_item.collection_id  # TODO version is included
        # collection_led_granule_id = stac_item.id if stac_item.id.startswith(stac_item.collection_id) else f'{stac_item.collection_id}:{stac_item.id}'
        # self.__custom_properties['granule_id'] = collection_led_granule_id  # This needs to be start with collection_id to be consistent with cumulus granule_id which starts with collection
        granule_metadata_props = GranuleMetadataProps()
        granule_metadata_props.granule_id = stac_item.id
        collection_id_split = stac_item.collection_id.split('___')
        granule_metadata_props.collection_name = collection_id_split[0]
        granule_metadata_props.collection_version = stac_item.collection_id.split('___')[1] if len(collection_id_split) > 1 else ''
        granule_metadata_props.prod_dt = TimeUtils().parse_from_unix(stac_item.datetime.timestamp()).get_datetime_str(fmt='%Y-%m-%dT%H:%M:%S.%fZ')
        granule_metadata_props.beginning_dt = stac_item.properties['start_datetime'] if stac_item.properties['start_datetime'] else TimeUtils().parse_from_unix(0).get_datetime_str()
        granule_metadata_props.ending_dt = stac_item.properties['end_datetime'] if stac_item.properties['end_datetime'] else TimeUtils().parse_from_unix(0).get_datetime_str()
        return granule_metadata_props
