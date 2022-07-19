import json
import logging
import os

from cumulus_lambda_functions.cumulus_dapa_client.dapa_client import DapaClient
from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3
from cumulus_lambda_functions.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class DownloadGranules:
    COLLECTION_ID_KEY = 'COLLECTION_ID'
    DOWNLOAD_DIR_KEY = 'DOWNLOAD_DIR'

    LIMITS_KEY = 'LIMITS'
    DATE_FROM_KEY = 'DATE_FROM'
    DATE_TO_KEY = 'DATE_TO'
    VERIFY_SSL_KEY = 'VERIFY_SSL'

    def __init__(self):
        self.__collection_id = ''
        self.__date_from = ''
        self.__date_to = ''
        self.__limit = 1000
        self.__download_dir = '/tmp'
        self.__verify_ssl = True
        self.__s3 = AwsS3()

    def __set_props_from_env(self):
        missing_keys = [k for k in [self.COLLECTION_ID_KEY, self.DOWNLOAD_DIR_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self.__collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        self.__download_dir = os.environ.get(self.DOWNLOAD_DIR_KEY)
        self.__download_dir = self.__download_dir[:-1] if self.__download_dir.endswith('/') else self.__download_dir
        if self.LIMITS_KEY not in os.environ:
            LOGGER.warning(f'missing {self.LIMITS_KEY}. using default: {self.__limit}')
        else:
            self.__limit = int(os.environ.get(self.LIMITS_KEY))

        self.__date_from = os.environ.get(self.DATE_FROM_KEY, '')
        self.__date_to = os.environ.get(self.DATE_TO_KEY, '')
        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        return self

    def __get_downloading_urls(self, granules_result: list):
        if len(granules_result) < 1:
            LOGGER.warning(f'cannot find any granules')
            return []
        downloading_urls = [k['assets'] for k in granules_result]
        return downloading_urls

    def __download_one_granule(self, assets: dict):
        """
        sample assets
          {
            "data": {
              "href": "s3://am-uds-dev-cumulus-internal/ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16017044853900.PDS",
              "title": "P1570515ATMSSCIENCEAAT16017044853900.PDS",
              "description": "P1570515ATMSSCIENCEAAT16017044853900.PDS"
            },
            "metadata__data": {
              "href": "s3://am-uds-dev-cumulus-internal/ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16017044853901.PDS",
              "title": "P1570515ATMSSCIENCEAAT16017044853901.PDS",
              "description": "P1570515ATMSSCIENCEAAT16017044853901.PDS"
            },
            "metadata__xml": {
              "href": "s3://am-uds-dev-cumulus-internal/ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16017044853901.PDS.xml",
              "title": "P1570515ATMSSCIENCEAAT16017044853901.PDS.xml",
              "description": "P1570515ATMSSCIENCEAAT16017044853901.PDS.xml"
            },
            "metadata__cmr": {
              "href": "s3://am-uds-dev-cumulus-internal/ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16017044853900.PDS.cmr.xml",
              "title": "P1570515ATMSSCIENCEAAT16017044853900.PDS.cmr.xml",
              "description": "P1570515ATMSSCIENCEAAT16017044853900.PDS.cmr.xml"
            }
          }
        :param assets:
        :return:
        """
        error_log = []
        for k, v in assets.items():
            try:
                LOGGER.debug(f'downloading: {v["href"]}')
                self.__s3.set_s3_url(v['href']).download(self.__download_dir)
            except Exception as e:
                LOGGER.exception(f'failed to download {v}')
                v['cause'] = str(e)
                error_log.append(v)
        return error_log

    def start(self):
        self.__set_props_from_env()
        LOGGER.debug(f'creating download dir: {self.__download_dir}')
        FileUtils.mk_dir_p(self.__download_dir)
        dapa_client = DapaClient().with_verify_ssl(self.__verify_ssl)
        granules_result = dapa_client.get_granules(self.__collection_id, self.__limit, 0, self.__date_from, self.__date_to)
        downloading_urls = self.__get_downloading_urls(granules_result)
        error_list = []
        for each in downloading_urls:
            LOGGER.debug(f'working on {each}')
            current_error_list = self.__download_one_granule(each)
            error_list.extend(current_error_list)
        if len(error_list) > 0:
            with open(f'{self.__download_dir}/error.log', 'w') as error_file:
                error_file.write(json.dumps(error_list, indent=4))
        return
