import json
import os
from time import sleep

from cumulus_lambda_functions.daac_archiver.daac_archiver_logic import DaacArchiverLogic
from mdps_ds_lib.lib.utils.file_utils import FileUtils

from mdps_ds_lib.lib.cumulus_stac.item_transformer import ItemTransformer

from cumulus_lambda_functions.lib.uds_db.uds_collections import UdsCollections

from cumulus_lambda_functions.metadata_stac_generate_cmr.stac_input_metadata import StacInputMetadata

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from mdps_ds_lib.lib.aws.aws_message_transformers import AwsMessageTransformers
from cumulus_lambda_functions.lib.uds_db.granules_db_index import GranulesDbIndex

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class GranulesIndexer:
    CUMULUS_SCHEMA = {
        'type': 'object',
        'required': ['event', 'record'],
        'properties': {
            'event': {'type': 'string'},
            'record': {'type': 'object'},
        }
    }

    def __init__(self, event) -> None:
        self.__event = event
        LOGGER.debug(f'event: {event}')
        self.__cumulus_record = {}
        self.__file_postfixes = os.getenv('FILE_POSTFIX', 'STAC.JSON')
        self.__valid_filetype_name = os.getenv('VALID_FILETYPE', 'metadata').lower()
        self.__file_postfixes = [k.upper().strip() for k in self.__file_postfixes.split(',')]
        self.__input_file_list = []
        self.__s3 = AwsS3()

    def __get_potential_files(self):
        potential_files = []
        self.__input_file_list = self.__cumulus_record['files']
        for each_file in self.__input_file_list:
            if 'type' in each_file and each_file['type'].strip().lower() != self.__valid_filetype_name:
                LOGGER.debug(f'Not metadata. skipping {each_file}')
                continue
            if 'fileName' not in each_file and 'name' in each_file:  # add fileName if there is only name
                each_file['fileName'] = each_file['name']
            if 'url_path' in each_file:
                s3_bucket, s3_key = self.__s3.split_s3_url(each_file['url_path'])
                each_file['bucket'] = s3_bucket
                each_file['key'] = s3_key
            LOGGER.debug(f'checking file: {each_file}')
            file_key_upper = each_file['key'].upper().strip()
            LOGGER.debug(f'checking file_key_upper: {file_key_upper} against {self.__file_postfixes}')
            if any([file_key_upper.endswith(k) for k in self.__file_postfixes]):
                potential_files.append(each_file)
        return potential_files

    def __read_pds_metadata_file(self, potential_file):
        self.__s3.target_bucket = potential_file['bucket']
        self.__s3.target_key = potential_file['key']
        return self.__s3.read_small_txt_file()

    def start(self):
        incoming_msg = AwsMessageTransformers().sqs_sns(self.__event)
        result = JsonValidator(self.CUMULUS_SCHEMA).validate(incoming_msg)
        if result is not None:
            raise ValueError(f'input json has CUMULUS validation errors: {result}')
        self.__cumulus_record = incoming_msg['record']
        if len(self.__cumulus_record['files']) < 1:
            # TODO ingest updating stage?
            return
        stac_input_meta = None
        potential_files = self.__get_potential_files()
        LOGGER.debug(f'potential_files: {potential_files}')
        for each_potential_file in potential_files:
            try:
                LOGGER.debug(f'trying each_potential_file: {each_potential_file}')
                stac_input_meta = StacInputMetadata(json.loads(self.__read_pds_metadata_file(each_potential_file)))
                granules_metadata_props = stac_input_meta.start()
                break
            except:
                LOGGER.exception(f'most likely not a STAC file: {each_potential_file}')
        if stac_input_meta is not None:
            self.__cumulus_record['custom_metadata'] = stac_input_meta.custom_properties
        else:
            LOGGER.warning(f'unable to find STAC JSON file in {potential_files}')
        stac_item = ItemTransformer().to_stac(self.__cumulus_record)
        if 'bbox' in stac_item:
            stac_item['bbox'] = GranulesDbIndex.to_es_bbox(stac_item['bbox'])
        collection_identifier = UdsCollections.decode_identifier(self.__cumulus_record['collectionId'])
        LOGGER.debug(f'stac_item: {stac_item}')
        GranulesDbIndex().add_entry(collection_identifier.tenant,
                                    collection_identifier.venue,
                                    stac_item,
                                    self.__cumulus_record['granuleId']
                                    )
        LOGGER.debug(f'added to GranulesDbIndex')
        daac_archiver = DaacArchiverLogic()
        cnm_response = daac_archiver.get_cnm_response_json_file(list(stac_item['assets'].values())[0], stac_item['id'])
        if cnm_response is None:
            LOGGER.error(f'no CNM Response file. Not continuing to DAAC Archiving')
            return self
        daac_archiver.send_to_daac_internal(cnm_response)
        return self
