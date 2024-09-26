from mdps_ds_lib.lib.utils.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.metadata_extraction.granule_metadata_props import GranuleMetadataProps

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())
L1A_INPUT_METADATA_SCHEMA = {
    "type": "object",
    "required": ["cas:metadata"],
    "properties": {
        "cas:metadata": {
            "type": "object",
            "required": ["keyval"],
            "properties": {
                "keyval": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["key", "val"],
                        "properties": {
                            "key": {
                                "type": "string",
                            },
                            "val": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}},
                                ]
                            },
                        }
                    },
                },
            },
        }
    },
}


class L1AInputMetadata:
    def __init__(self, input_l1a_metadata: dict):
        """
        :param input_l1a_metadata: str - XML string
        """
        self.__granule_metadata_props = GranuleMetadataProps()
        self.__input_l1a_metadata = input_l1a_metadata
        self.__l1a_metadata_dict = {}
        self.__mandatory_keys = ['EndDateTime', 'ProductName', 'ProductionDateTime', 'StartDateTime']

    def __validate_pds_metadata(self):
        result = JsonValidator(L1A_INPUT_METADATA_SCHEMA).validate(self.__input_l1a_metadata)
        if result is not None:
            raise ValueError(f'pds metadata has validation errors: {result}')
        return

    def __load_to_dict(self):
        self.__l1a_metadata_dict = {k['key']: k['val'] for k in self.__input_l1a_metadata['cas:metadata']['keyval']}
        missing_keys = [k for k in self.__mandatory_keys if k not in self.__l1a_metadata_dict]
        if len(missing_keys) > 0:
            raise ValueError(f'missing mandatory keys: {missing_keys}')
        return

    def load(self):
        self.__validate_pds_metadata()
        self.__load_to_dict()
        self.__granule_metadata_props.beginning_dt = self.__l1a_metadata_dict['StartDateTime']
        self.__granule_metadata_props.ending_dt = self.__l1a_metadata_dict['EndDateTime']
        self.__granule_metadata_props.prod_dt = self.__l1a_metadata_dict['ProductionDateTime']
        # self.__granule_metadata_props.prod_name = self.__l1a_metadata_dict['ProductName']  # NOT in used at this moment.
        return self.__granule_metadata_props
