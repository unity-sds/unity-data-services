from mdps_ds_lib.lib.aws.aws_s3 import AwsS3
from mdps_ds_lib.lib.aws.aws_sns import AwsSns
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stac_fast_api_client.sfa_client_factory import SFAClientFactory
from pystac import Item

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

class DaacArchiverCatalia:
    archival_status_schema = {
      "type": "object",
      "required": [
        "status"
      ],
      "properties": {
        "status": {
          "type": "string",
          "enum": [
            "cnm-authorized-success",
            "cnm-authorized-failed",
            "cnm-staged-success",
            "cnm-staged-failed",
            "cnm-submit-success",
            "cnm-submit-failed",
            "cnm-receive-success",
            "cnm-receive-failed"
          ]
        },
        "errorCode": {
          "type": "string"
        },
        "errorMessage": {
          "type": "string"
        },
        "href": {
          "type": "string",
          "format": "iri-reference"
        }
      },
      "additionalProperties": False
    }
    def __init__(self):
        self.__sns = AwsSns()
        self.__s3 = AwsS3()
        self.__staged_s3_bucket = 'TODO'  # TODO
        self.__sfa_client = SFAClientFactory().get_instance_from_env()
        self.__archiving_granules_stac = None
        self.__archiving_status_extension_url = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
        self.__daac_agreements = []

    def archive_granule(self, collection_id, granule_id):
        # TODO look up granule details
        self.__archiving_granules_stac = self.__sfa_client.get_item(collection_id, item_id=granule_id)
        LOGGER.debug(f'retrieved stac_item from STAC Fast API: {self.__archiving_granules_stac}')
        self.archive_granule_json()
        return self

    def archive_granule_json(self):
        """
        1. Check UDS API if this granule is being pushed to archive(s)
        2. Copy Data and Metadata to staging bucket
        3. Update STAC Metadata to staging bucket. + Re-upload.
        4. Send message to DAAC SNS

        :param stac_granule_json:
        :return:
        """
        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Pls retrieve it first.')
        self.add_archival_extension()
        self.get_daac_configs()
        if len(self.__daac_agreements) < 1:
            LOGGER.debug(f'this collection does not have any daac. {self.__archiving_granules_stac}')
            return
        self.stage_files()
        for each_agreement in self.__daac_agreements:
            LOGGER.debug(f'working on {each_agreement}')
            self.send_daac_sns(each_agreement)
        return

    def add_archival_extension(self):
        """
        1. Convert dictionary to pystac object. store the modified object back to the self.__archiving_granules_stac
        2. Check if it has a stac_extensions, and it has self.__archiving_status_extension_url
        3. If so, done
        4. If not, add that extension, done

        :return:
        """
        return self

    def get_daac_configs(self):
        # TODO
        # update self.__daac_agreements
        return

    def stage_files(self):
        """
        1. Check directory s3://<self.__staged_s3_bucket>/<collection-id>/<item-id>
        2. If not empty. log a warning message.
        3. Empty S3 directory
        4. Get file locations for each asset in self.__archiving_granules_stac which should be a pystac object.
        5. Copy them from source S3 to destination S3 from Step 1.
        6. After each copy, update the href of each asset to new location.
        7. If pystac is part of the assets, change its href to new location as well and upload it.
        8. How do I know if pystac is part of assets?
        :return:
        """
        return self

    def update_status(self, archival_status: dict):
        """
        1. validate archival_status from parameter against self.archival_status_schema
        2. Add archival_status to self.__archiving_granules_stac>properties>archival:status
        3. get collection and item id from  self.__archiving_granules_stac
        4. convert self.__archiving_granules_stac to a json
        5. call self.__sfa_client.update_item()  # Note partial may not be available. Just update whole for now.
        :param archival_status:
        :return:
        """
        return self

    def send_daac_sns(self, daac_config):
        try:
            self.__sns.set_topic_arn(daac_config['daac_sns_topic_arn'])
            daac_cnm_message = {
                "collection": {
                    'name': daac_config['daac_collection_name'],
                    'version': daac_config['daac_data_version'],
                },
                "identifier": uds_cnm_json['identifier'],
                "submissionTime": f'{TimeUtils.get_current_time()}Z',
                "provider": daac_config['daac_provider'] if 'daac_provider' in daac_config else granule_identifier.tenant,
                "version": "1.6.0",  # TODO this is hardcoded?
                "product": {
                    "name": granule_identifier.granule,
                    # "dataVersion": daac_config['daac_data_version'],
                    'files': self.__extract_files(uds_cnm_json, daac_config),
                }
            }
            LOGGER.debug(f'daac_cnm_message: {daac_cnm_message}')
            self.__sns.set_external_role(daac_config['daac_role_arn'], daac_config['daac_role_session_name']).publish_message(json.dumps(daac_cnm_message), True)
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_success',
                'archive_error_message': '',
                'archive_error_code': '',
            }, uds_cnm_json['identifier'])
        except Exception as e:
            LOGGER.exception(f'failed during archival process')
            self.__granules_index.update_entry(granule_identifier.tenant, granule_identifier.venue, {
                'archive_status': 'cnm_s_failed',
                'archive_error_message': str(e),
            }, uds_cnm_json['identifier'])

        return

    def
