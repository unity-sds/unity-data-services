import json
import os

from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore
from mdps_ds_lib.stac_fast_api_client.sfa_client_factory import SFAClientFactory
from pystac import Item
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from cumulus_lambda_functions.lib.uds_utils import backoff_wrapper

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class SfaClientMw:
    archiving_status_extension_url = "https://stac-extensions.github.io/archival_statuses/v1.0.0/schema.json"

    @staticmethod
    def add_archival_extension(archiving_granules_stac):
        """
        1. Convert dictionary to pystac object. store the modified object back to the self.__archiving_granules_stac
        2. Check if it has a stac_extensions, and it has self.__archiving_status_extension_url
        3. If so, done
        4. If not, add that extension, done

        :return:
        """
        if archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot add archival extension.')

        # Convert to pystac Item if it's a dictionary
        if isinstance(archiving_granules_stac, dict):
            archiving_granules_stac = Item.from_dict(archiving_granules_stac)

        # Check if the archival extension is already present
        if hasattr(archiving_granules_stac, 'stac_extensions'):
            if SfaClientMw.archiving_status_extension_url not in archiving_granules_stac.stac_extensions:
                archiving_granules_stac.stac_extensions.append(SfaClientMw.archiving_status_extension_url)
                LOGGER.debug(f'Added archival extension to STAC item: {SfaClientMw.archiving_status_extension_url}')
        else:
            # Initialize stac_extensions if it doesn't exist
            archiving_granules_stac.stac_extensions = [SfaClientMw.archiving_status_extension_url]
            LOGGER.debug(f'Initialized stac_extensions with archival extension: {SfaClientMw.archiving_status_extension_url}')

        # Initialize archival:status property if it doesn't exist
        if 'archival:status' not in archiving_granules_stac.properties:
            archiving_granules_stac.properties['archival:status'] = []
            LOGGER.debug(f'Initialized archival:status property for STAC item')
        return archiving_granules_stac

    def __init__(self):
        self.__sfa_client = None
        self.__update_status_to_sfa = os.getenv('UPDATE_STATUS_TO_SFA', 'FALSE').strip().upper() == 'TRUE'
        self.__collection, self.__granule = None, None
        self.__archiving_granules_stac = None

    def load_sfa_client(self):
        sfa_auth_ssm_key = os.getenv('SFA_AUTH', None)
        LOGGER.debug(f'retrieving SSM details from {sfa_auth_ssm_key}')
        sfa_auth_ssm_dict = AwsParamStore().get_param(sfa_auth_ssm_key)
        if sfa_auth_ssm_dict is None:
            raise ValueError(f'missing SSM detaails for SFA Auth: {sfa_auth_ssm_dict}')
        self.__sfa_client = SFAClientFactory().get_instance_from_dict(json.loads(sfa_auth_ssm_dict))
        return

    @property
    def sfa_client(self):
        if self.__sfa_client is None:
            self.load_sfa_client()
        return self.__sfa_client

    @sfa_client.setter
    def sfa_client(self, val):
        """
        :param val:
        :return: None
        """
        self.__sfa_client = val
        return

    def load_manually(self, collection, granule_id):
        self.__collection, self.__granule = collection, granule_id
        return self

    def update_sfa_item_status(self, archival_status_with_timestamp):
        if not self.__update_status_to_sfa:
            LOGGER.debug(f'NOT updating SFA catalog due to setting UPDATE_STATUS_TO_SFA')
            return self
        
        if self.__sfa_client is None:
            self.load_sfa_client()
            return self

        self.__archiving_granules_stac = backoff_wrapper(self.__sfa_client.get_item, self.__collection, tem_id=self.__granule)
        if self.__archiving_granules_stac is None:
            raise ValueError(f'NULL archiving granule. Cannot update status.')
        self.add_archival_extension()
        if 'archival:status' not in self.__archiving_granules_stac.properties:
            self.__archiving_granules_stac.properties['archival:status'] = []
        elif not isinstance(self.__archiving_granules_stac.properties['archival:status'], list):
            self.__archiving_granules_stac.properties['archival:status'] = []

        # Add the new status to the list
        self.__archiving_granules_stac.properties['archival:status'].append(archival_status_with_timestamp)
        LOGGER.info(f'Added archival status: {archival_status_with_timestamp}')

        try:
            # Convert STAC item to JSON dictionary
            stac_item_dict = self.__archiving_granules_stac.to_dict()

            # Update the item using the STAC Fast API client
            updated_item = backoff_wrapper(self.__sfa_client.update_item,
                                           collection_id=self.__collection,
                                           item_id=self.__granule,
                                           item=stac_item_dict
                                           )
            LOGGER.info(
                f'Successfully updated STAC item {self.__granule} in collection {self.__collection} with new archival status')
            LOGGER.debug(f'Updated item response: {updated_item}')
        except Exception as e:
            LOGGER.exception(f'Failed to update STAC item {self.__granule} in collection {self.__collection}')
            raise e
        return self
