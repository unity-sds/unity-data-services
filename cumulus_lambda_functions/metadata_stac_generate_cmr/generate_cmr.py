import hashlib
import json
import os
from copy import deepcopy

import xmltodict

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.utils.json_validator import JsonValidator
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.metadata_extraction.echo_metadata import EchoMetadata
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from cumulus_lambda_functions.metadata_stac_generate_cmr.stac_input_metadata import StacInputMetadata
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex

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
                                                        "url_path": {
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
                                                        "type"
                                                    ],
                                                    "anyOf": [
                                                        {"required": ["bucket", "key"]},
                                                        {"required": ["url_path"]}
                                                    ],
                                                }
                                            }
                                        },
                                        "required": [
                                            "granuleId",
                                            "files"
                                        ]
                                    }
                                },
                                "collection": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "version": {"type": "string"},
                                    },
                                    "required": ["name", "version"]
                                }
                            },
                            "required": [
                                "input_granules", "collection"
                            ]
                        }
                    },
                    "required": [
                        "meta"
                    ]
                },
                "extra_config": {
                    "required": [],
                    "properties": {
                        "add_extra_keys": {"type": "boolean"}
                    }
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
        self.__valid_filetype_name = os.getenv('VALID_FILETYPE', 'metadata').lower()
        self.__file_postfixes = os.getenv('FILE_POSTFIX', 'STAC.JSON')
        self.__file_postfixes = [k.upper().strip() for k in self.__file_postfixes.split(',')]
        self.__input_file_list = []

    def __validate_input(self):
        result = JsonValidator(INPUT_EVENT_SCHEMA).validate(self.__event)
        if result is None:
            return
        raise ValueError(f'input json has validation errors: {result}')

    def __get_potential_files(self):
        potential_files = []
        self.__input_file_list = self.__event['cma']['event']['meta']['input_granules'][0]['files']
        LOGGER.debug(f'before restructure: {self.__input_file_list}')
        for each_file in self.__input_file_list:
            if 'fileName' not in each_file and 'name' in each_file:  # add fileName if there is only name
                each_file['fileName'] = each_file['name']
            if 'url_path' in each_file:
                s3_bucket, s3_key = self.__s3.split_s3_url(each_file['url_path'])
                each_file['bucket'] = s3_bucket
                each_file['key'] = s3_key
            LOGGER.debug(f'checking file: {each_file}')
            if 'type' in each_file and each_file['type'].strip().lower() != self.__valid_filetype_name:
                LOGGER.debug(f'Not metadata. skipping {each_file}')
                continue
            file_key_upper = each_file['key'].upper().strip()
            LOGGER.debug(f'checking file_key_upper: {file_key_upper} against {self.__file_postfixes}')
            if any([file_key_upper.endswith(k) for k in self.__file_postfixes]):
                potential_files.append(each_file)
        LOGGER.debug(f'after restructure: {self.__input_file_list}')
        return potential_files

    def __read_pds_metadata_file(self, potential_file):
        self.__s3.target_bucket = potential_file['bucket']
        self.__s3.target_key = potential_file['key']
        return self.__s3.read_small_txt_file()

    def __is_adding_extra_keys(self):
        if 'extra_config' not in self.__event['cma']:
            return True
        if 'add_extra_keys' not in self.__event['cma']['extra_config']:
            return True
        return self.__event['cma']['extra_config']['add_extra_keys']

    def __generate_output_dict(self, echo_metadata_md5: str):
        output_dict = {
            "checksumType": "md5",
            "checksum": echo_metadata_md5,
            "type": "metadata",

            "key": self.__s3.target_key,
            "fileName": os.path.basename(self.__s3.target_key),
            "bucket": self.__s3.target_bucket,
            "size": int(self.__s3.get_size()),
        }
        if not self.__is_adding_extra_keys():
            return output_dict
        output_dict = {**output_dict, **{
            "path": os.path.dirname(self.__s3.target_key),
            "name": os.path.basename(self.__s3.target_key),
            "source_bucket": self.__s3.target_bucket,
            "url_path": f's3://{self.__s3.target_bucket}/{self.__s3.target_key}',
        }}
        return output_dict

    def __ingest_custom_metadata(self, custom_metadata: dict):
        if os.getenv('REGISTER_CUSTOM_METADATA', 'TRUE').strip().upper() != 'TRUE':
            LOGGER.debug(f'not registering custom metadata due to ENV setting. {custom_metadata}')
            return
        LOGGER.debug(f'custom_metadata: {custom_metadata}')
        if 'granule_id' not in custom_metadata or 'collection_id' not in custom_metadata:
            LOGGER.error(f'unable to write custom metadata w/o granule or collection id: {custom_metadata}')
            return
        collection_identifier = UdsCollections.decode_identifier(custom_metadata['collection_id'])
        GranulesDbIndex().add_entry(collection_identifier.tenant,
                                    collection_identifier.venue,
                                    custom_metadata,
                                    custom_metadata['granule_id']
                                    )
        return

    def start(self):
        """
        sample event
{
  "cma": {
    "task_config": {
      "bucket": "{$.meta.buckets.internal.name}",
      "collection": "{$.meta.collection}",
      "cumulus_message": {
        "outputs": [
          {
            "source": "{$.files}",
            "destination": "{$.payload}"
          }
        ]
      }
    },
    "event": {
      "cumulus_meta": {
        "cumulus_version": "11.1.1",
        "execution_name": "90c9c978-ca5e-47b1-9c4a-3d20c73a4743",
        "message_source": "sfn",
        "queueExecutionLimits": {
          "https://sqs.us-west-2.amazonaws.com/237868187491/uds-dev-cumulus-backgroundProcessing": 5
        },
        "state_machine": "arn:aws:states:us-west-2:237868187491:stateMachine:uds-dev-cumulus-IngestGranule",
        "system_bucket": "uds-dev-cumulus-internal",
        "workflow_start_time": 1655943753534,
        "parentExecutionArn": "arn:aws:states:us-west-2:237868187491:execution:uds-dev-cumulus-DiscoverGranules:707b8f70-ac78-4fa8-86f6-b74dcdfed287",
        "queueUrl": "arn:aws:sqs:us-west-2:237868187491:uds-dev-cumulus-startSF"
      },
      "exception": "None",
      "meta": {
        "buckets": {
          "internal": {
            "name": "uds-dev-cumulus-internal",
            "type": "internal"
          },
          "private": {
            "name": "uds-dev-cumulus-private",
            "type": "private"
          },
          "protected": {
            "name": "uds-dev-cumulus-protected",
            "type": "protected"
          },
          "public": {
            "name": "uds-dev-cumulus-public",
            "type": "public"
          },
          "sps": {
            "name": "uds-dev-cumulus-sps",
            "type": "protected"
          },
          "staging": {
            "name": "uds-dev-cumulus-staging",
            "type": "internal"
          }
        },
        "cmr": {
          "clientId": "CHANGEME",
          "cmrEnvironment": "UAT",
          "cmrLimit": 100,
          "cmrPageSize": 50,
          "oauthProvider": "earthdata",
          "passwordSecretName": "uds-dev-cumulus-message-template-cmr-password20220330223854670000000005",
          "provider": "CHANGEME",
          "username": "username"
        },
        "collection": {
          "duplicateHandling": "replace",
          "process": "snpp.level1",
          "files": [
            {
              "bucket": "protected",
              "regex": "^SNDR.SNPP.ATMS.L1A.*\\.nc$",
              "reportToEms": false,
              "sampleFileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
              "type": "data"
            },
            {
              "bucket": "protected",
              "regex": "^SNDR.SNPP.ATMS.L1A.*\\.nc\\.cas$",
              "reportToEms": false,
              "sampleFileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
              "type": "metadata"
            },
            {
              "bucket": "protected",
              "regex": "^SNDR.SNPP.ATMS.L1A.*\\.nc\\.cmr\\.xml$",
              "reportToEms": false,
              "sampleFileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cmr.xml",
              "type": "metadata"
            }
          ],
          "granuleId": "^SNDR.SNPP.ATMS.L1A.*$",
          "granuleIdExtraction": "(^SNDR.SNPP.ATMS.L1A.*)(\\.nc|\\.nc\\.cas|\\.nc\\.cmr\\.xml)",
          "name": "SNDR_SNPP_ATMS_L1A_1",
          "reportToEms": false,
          "sampleFileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
          "url_path": "{cmrMetadata.Granule.Collection.ShortName}",
          "version": "1",
          "updatedAt": 1655943525719,
          "createdAt": 1655943525719
        },
        "process": "snpp.level1",
        "distribution_endpoint": null,
        "launchpad": {
          "api": "launchpadApi",
          "certificate": "launchpad.pfx",
          "passphraseSecretName": ""
        },
        "provider": {
          "id": "snpp_l1_s3",
          "globalConnectionLimit": 1000,
          "host": "uds-dev-cumulus-staging",
          "protocol": "s3",
          "createdAt": 1655943376376,
          "updatedAt": 1655943376376
        },
        "stack": "uds-dev-cumulus",
        "template": "s3://uds-dev-cumulus-internal/uds-dev-cumulus/workflow_template.json",
        "workflow_name": "IngestGranule",
        "workflow_tasks": {
          "0": {
            "name": "uds-dev-cumulus-SyncGranule",
            "version": "$LATEST",
            "arn": "arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-SyncGranule"
          }
        },
        "staticValue": "aStaticValue",
        "interpolatedValueStackName": "uds-dev-cumulus",
        "input_granules": [
          {
            "granuleId": "SNDR.SNPP.ATMS.L1A.nominal2.01",
            "dataType": "SNDR_SNPP_ATMS_L1A_1",
            "version": "1",
            "files": [
              {
                "size": 9194361,
                "bucket": "uds-dev-cumulus-internal",
                "key": "file-staging/uds-dev-cumulus/SNDR_SNPP_ATMS_L1A_1___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
                "source": "SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
                "fileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
                "type": "data"
              },
              {
                "size": 2673,
                "bucket": "uds-dev-cumulus-internal",
                "key": "file-staging/uds-dev-cumulus/SNDR_SNPP_ATMS_L1A_1___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
                "source": "SNDR_SNPP_ATMS_L1A/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
                "fileName": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
                "type": "metadata"
              }
            ],
            "sync_granule_duration": 694,
            "createdAt": 1656010982847
          }
        ]
      },
      "payload": {},
      "replace": {
        "Bucket": "uds-dev-cumulus-internal",
        "Key": "events/172fbbc4-f8ee-4974-8a77-37bc669accb0",
        "TargetPath": "$.payload"
      }
    }
  }
}
        :return:
        """
        self.__validate_input()
        LOGGER.debug(f'input: {self.__event}')
        stac_input_meta = None
        potential_files = self.__get_potential_files()
        for each_potential_file in potential_files:
            try:
                stac_input_meta = StacInputMetadata(json.loads(self.__read_pds_metadata_file(each_potential_file)))
                granules_metadata_props = stac_input_meta.start()
                break
            except Exception as e:
                LOGGER.exception(f'most likely not a STAC file: {each_potential_file}')
        if stac_input_meta is None:
            raise RuntimeError(f'unable to find STAC JSON file in {potential_files}')
        LOGGER.debug(f'starting __ingest_custom_metadata')
        self.__ingest_custom_metadata(stac_input_meta.custom_properties)
        echo_metadata = EchoMetadata(granules_metadata_props).load().echo_metadata
        echo_metadata_xml_str = xmltodict.unparse(echo_metadata, pretty=True)
        self.__s3.target_key = os.path.join(os.path.dirname(self.__s3.target_key), f'{granules_metadata_props.granule_id}.cmr.xml')
        self.__s3.upload_bytes(echo_metadata_xml_str.encode())
        echo_metadata_md5 = hashlib.md5(echo_metadata_xml_str.encode()).hexdigest()
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
                        "dataType": granules_metadata_props.collection_name,
                        "version": f'{granules_metadata_props.collection_version}',
                        "files": self.__input_file_list + [self.__generate_output_dict(echo_metadata_md5)],
                        # "files": self.__input_file_list,
                        "sync_granule_duration": 20302,
                        "createdAt": TimeUtils.get_current_unix_milli(),
                    }
                ]
            }
        return returning_dict
