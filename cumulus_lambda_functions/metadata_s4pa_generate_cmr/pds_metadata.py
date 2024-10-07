import xmltodict

from mdps_ds_lib.lib.utils.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.metadata_extraction.granule_metadata_props import GranuleMetadataProps

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())
PDS_METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "S4PAGranuleMetaDataFile": {
            "type": "object",
            "properties": {
                "DataGranule": {
                    "type": "object",
                    "properties": {
                        "GranuleID": {"type": "string"},
                        "ProductionDateTime": {"type": "string"},
                        "InsertDateTime": {"type": "string"},
                    },
                    "required": ["GranuleID", "InsertDateTime", "ProductionDateTime"]
                },
                "RangeDateTime": {
                    "type": "object",
                    "properties": {
                        "RangeEndingDate": {"type": "string"},
                        "RangeEndingTime": {"type": "string"},
                        "RangeBeginningDate": {"type": "string"},
                        "RangeBeginningTime": {"type": "string"},
                    },
                    "required": ["RangeEndingDate", "RangeEndingTime", "RangeBeginningDate", "RangeBeginningTime"]

                },
                "CollectionMetaData": {
                    "type": "object",
                    "properties": {
                        "ShortName": {"type": "string"},
                        "VersionID": {"type": "string"}
                    },
                    "required": ["ShortName", "VersionID"]

                },
            },
            "required": ["RangeDateTime"]
        }
    },
    "required": ["S4PAGranuleMetaDataFile"]
}


class PdsMetadata:
    def __init__(self, input_pds_metadata: dict):
        """
        :param input_pds_metadata_str: str - XML string
        """
        self.__input_pds_metadata = input_pds_metadata
        self.__granule_metadata_props = GranuleMetadataProps()

    def __validate_pds_metadata(self):
        result = JsonValidator(PDS_METADATA_SCHEMA).validate(self.__input_pds_metadata)
        if result is None:
            return
        raise ValueError(f'pds metadata has validation errors: {result}')

    def __load_time_range(self):
        range_dt = self.__input_pds_metadata['S4PAGranuleMetaDataFile']['RangeDateTime']
        self.__granule_metadata_props.beginning_dt = f"{range_dt['RangeBeginningDate']}T{range_dt['RangeBeginningTime']}"
        self.__granule_metadata_props.ending_dt = f"{range_dt['RangeEndingDate']}T{range_dt['RangeEndingTime']}"
        return

    def __load_collection_metadata(self):
        collection_met = self.__input_pds_metadata['S4PAGranuleMetaDataFile']['CollectionMetaData']
        self.__granule_metadata_props.collection_name = collection_met['ShortName']
        self.__granule_metadata_props.collection_version = collection_met['VersionID']
        return

    def __load_granule_metadata(self):
        granule_met = self.__input_pds_metadata['S4PAGranuleMetaDataFile']['DataGranule']
        self.__granule_metadata_props.granule_id = granule_met['GranuleID']
        self.__granule_metadata_props.prod_dt = granule_met['ProductionDateTime']
        self.__granule_metadata_props.insert_dt = granule_met['InsertDateTime']
        return

    def load(self) -> GranuleMetadataProps:
        self.__validate_pds_metadata()
        self.__load_time_range()
        self.__load_collection_metadata()
        self.__load_granule_metadata()
        return self.__granule_metadata_props
