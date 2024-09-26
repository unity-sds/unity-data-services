import os
from copy import deepcopy

import xmltodict

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.utils.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.metadata_extraction.echo_metadata import EchoMetadata
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from cumulus_lambda_functions.metadata_s4pa_generate_cmr.pds_metadata import PdsMetadata

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

INPUT_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "cma": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "object",
                    "properties": {
                        "meta": {
                            "type": "object",
                            "properties": {
                                "input_granules": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "granuleId": {
                                                "type": "string"
                                            },
                                            "files": {
                                                "type": "array",
                                                "minItems": 1,
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "bucket": {
                                                            "type": "string"
                                                        },
                                                        "key": {
                                                            "type": "string"
                                                        },
                                                        "source": {
                                                            "type": "string"
                                                        },
                                                        "fileName": {
                                                            "type": "string"
                                                        },
                                                        "type": {
                                                            "type": "string"
                                                        },
                                                        "size": {
                                                            "type": "number"
                                                        }
                                                    },
                                                    "required": [
                                                        "bucket",
                                                        "key",
                                                        "type"
                                                    ]
                                                }
                                            }
                                        },
                                        "required": [
                                            "granuleId",
                                            "files"
                                        ]
                                    }
                                }
                            },
                            "required": [
                                "input_granules"
                            ]
                        }
                    },
                    "required": [
                        "meta"
                    ]
                }
            },
            "required": []
        }
    },
    "required": [
        "cma"
    ]
}


class GenerateCmr:
    def __init__(self, event):
        self.__event = event
        self.__s3 = AwsS3()
        self._pds_file_dict = None
        self.__file_postfixes = os.getenv('FILE_POSTFIX', '1.PDS.XML, NC.XML')
        self.__file_postfixes = [k.upper().strip() for k in self.__file_postfixes.split(',')]
        self.__input_file_list = []

    def __validate_input(self):
        result = JsonValidator(INPUT_EVENT_SCHEMA).validate(self.__event)
        if result is None:
            return
        raise ValueError(f'input json has validation errors: {result}')

    def __get_pds_metadata_file(self):
        self.__input_file_list = self.__event['cma']['event']['meta']['input_granules'][0]['files']
        for each_file in self.__input_file_list:
            LOGGER.debug(f'checking file: {each_file}')
            file_key_upper = each_file['key'].upper().strip()
            LOGGER.debug(f'checking file_key_upper: {file_key_upper} against {self.__file_postfixes}')
            if any([file_key_upper.endswith(k) for k in self.__file_postfixes]):
                return each_file
        return None

    def __read_pds_metadata_file(self):
        self._pds_file_dict = self.__get_pds_metadata_file()
        if self._pds_file_dict is None:
            raise ValueError('missing PDS metadata file')
        self.__s3.target_bucket = self._pds_file_dict['bucket']
        self.__s3.target_key = self._pds_file_dict['key']
        return self.__s3.read_small_txt_file()

    def start(self):
        self.__validate_input()
        LOGGER.error(f'input: {self.__event}')
        pds_metadata = PdsMetadata(xmltodict.parse(self.__read_pds_metadata_file())).load()
        echo_metadata = EchoMetadata(pds_metadata).load().echo_metadata
        echo_metadata_xml_str = xmltodict.unparse(echo_metadata, pretty=True)
        self.__s3.target_key = os.path.join(os.path.dirname(self.__s3.target_key), f'{pds_metadata.granule_id}.cmr.xml')
        self.__s3.upload_bytes(echo_metadata_xml_str.encode())

        # put payload
        # remove replace
        # add             "task_config": {
        #                 "inputGranules": "{$.meta.input_granules}",
        #                 "granuleIdExtraction": "{$.meta.collection.granuleIdExtraction}"
        #             },
        # return {
        #     'files': ['example', 'mock', 'return'],
        #     'granules': self.__event
        # }
        returning_dict = deepcopy(self.__event['cma']['event'])
        if 'replace' in returning_dict:
            returning_dict.pop('replace')
        # TODO This is a hack since distribution_endpoint = null is complained by MoveGranule.
        """
        {
          "errorType": "CumulusMessageAdapterExecutionError",
          "errorMessage": "warning setting command to loadAndUpdateRemoteEvent\\nwarning setting command to loadNestedEvent\\nUnexpected Error <class 'jsonschema.exceptions.ValidationError'>. config schema: None is not of type 'string'\\n\\nFailed validating 'type' in schema['properties']['distribution_endpoint']:\\n    {'description': 'The api distribution endpoint', 'type': 'string'}\\n\\nOn instance['distribution_endpoint']:\\n    None\\n\\nFailed validating 'type' in schema['properties']['distribution_endpoint']:\\n    {'description': 'The api distribution endpoint', 'type': 'string'}\\n\\nOn instance['distribution_endpoint']:\\n    None",
          "trace": [
            "CumulusMessageAdapterExecutionError: warning setting command to loadAndUpdateRemoteEvent",
            "warning setting command to loadNestedEvent",
            "Unexpected Error <class 'jsonschema.exceptions.ValidationError'>. config schema: None is not of type 'string'",
            "",
            "Failed validating 'type' in schema['properties']['distribution_endpoint']:",
            "    {'description': 'The api distribution endpoint', 'type': 'string'}",
            "",
            "On instance['distribution_endpoint']:",
            "    None",
            "",
            "Failed validating 'type' in schema['properties']['distribution_endpoint']:",
            "    {'description': 'The api distribution endpoint', 'type': 'string'}",
            "",
            "On instance['distribution_endpoint']:",
            "    None",
            "    at Interface.<anonymous> (/var/task/webpack:/node_modules/@cumulus/cumulus-message-adapter-js/dist/cma.js:155:1)",
            "    at Interface.emit (events.js:326:22)",
            "    at Interface.EventEmitter.emit (domain.js:483:12)",
            "    at Interface.close (readline.js:416:8)",
            "    at Socket.onend (readline.js:194:10)",
            "    at Socket.emit (events.js:326:22)",
            "    at Socket.EventEmitter.emit (domain.js:483:12)",
            "    at endReadableNT (_stream_readable.js:1241:12)",
            "    at processTicksAndRejections (internal/process/task_queues.js:84:21)"
          ]
        }
        """
        if 'distribution_endpoint' in returning_dict['meta'] and returning_dict['meta']['distribution_endpoint'] is None:
            returning_dict['meta']['distribution_endpoint'] = f's3://{self.__s3.target_bucket}/'
        returning_dict['task_config'] = {
            "inputGranules": "{$.meta.input_granules}",
            "granuleIdExtraction": "{$.meta.collection.granuleIdExtraction}"
        }
        returning_dict['payload'] = {
                "granules": [
                    {
                        "granuleId": self.__event['cma']['event']['meta']['input_granules'][0]['granuleId'],
                        "dataType": pds_metadata.collection_name,
                        "version": f'{pds_metadata.collection_version}',
                        "files": self.__input_file_list + [{
                                "key": self.__s3.target_key,
                                "fileName": os.path.basename(self.__s3.target_key),
                                "bucket": self.__s3.target_bucket,
                                "size": int(self.__s3.get_size()),
                            }],
                        # "files": self.__input_file_list,
                        "sync_granule_duration": 20302,
                        "createdAt": TimeUtils.get_current_unix_milli(),
                    }
                ]
            }
        return returning_dict
