import logging
import os
import re
from collections import defaultdict
from glob import glob
from urllib.parse import urlparse, unquote_plus

from cumulus_lambda_functions.cumulus_dapa_client.dapa_client import DapaClient
from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3

LOGGER = logging.getLogger(__name__)


class UploadGranules:
    COLLECTION_ID_KEY = 'COLLECTION_ID'
    PROVIDER_ID_KEY = 'PROVIDER_ID'
    UPLOAD_DIR_KEY = 'UPLOAD_DIR'
    STAGING_BUCKET_KEY = 'STAGING_BUCKET'

    VERIFY_SSL_KEY = 'VERIFY_SSL'
    DELETE_FILES_KEY = 'DELETE_FILES'

    def __init__(self):
        self.__collection_id = ''
        self.__collection_details = {}
        self.__uploading_granules = []
        self.__provider_id = ''
        self.__staging_bucket = ''
        self.__upload_dir = '/tmp'
        self.__verify_ssl = True
        self.__delete_files = False
        self.__s3 = AwsS3()
        self.__raw_files = []

    def __set_props_from_env(self):
        missing_keys = [k for k in [self.COLLECTION_ID_KEY, self.PROVIDER_ID_KEY, self.UPLOAD_DIR_KEY, self.STAGING_BUCKET_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self.__collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        self.__provider_id = os.environ.get(self.PROVIDER_ID_KEY)
        self.__staging_bucket = os.environ.get(self.STAGING_BUCKET_KEY)

        self.__upload_dir = os.environ.get(self.UPLOAD_DIR_KEY)
        self.__upload_dir = self.__upload_dir[:-1] if self.__upload_dir.endswith('/') else self.__upload_dir

        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        self.__delete_files = os.environ.get(self.DELETE_FILES_KEY, 'FALSE').strip().upper() == 'TRUE'
        return self

    def __get_href(self, input_href: str):
        parse_result = urlparse(input_href)
        if parse_result.query == '':
            return ''
        query_dict = [k.split('=') for k in parse_result.query.split('&')]
        query_dict = {k[0]: unquote_plus(k[1]) for k in query_dict}
        if 'regex' not in query_dict:
            raise ValueError(f'missing regex in {input_href}')
        return query_dict['regex']

    def __sort_granules(self):
        file_regex_list = {k['type']: self.__get_href(k['href']) for k in self.__collection_details['links'] if k['rel'] != 'root' and not k['title'].endswith('cmr.xml')}
        granule_id_extraction = self.__collection_details['summaries']['granuleIdExtraction'][0]
        granules = defaultdict(dict)
        for each_file in self.__raw_files:
            each_filename = os.path.basename(each_file)
            each_granule_id = re.findall(granule_id_extraction, each_filename)
            if len(each_granule_id) < 1:
                LOGGER.warning(f'skipping file that cannot be matched to granule_id: {each_file}')
                continue
            each_granule_id = each_granule_id[0]
            if isinstance(each_granule_id, tuple):
                each_granule_id = each_granule_id[0]
            data_type = [k for k, v in file_regex_list.items() if len(re.findall(v, each_filename)) > 0]
            if len(data_type) != 1:
                LOGGER.warning(f'skipping file that cannot be matched to a datatype: {each_file}.. data_type: {data_type}')
                continue
            data_type = data_type[0]
            if data_type in granules[each_granule_id]:
                LOGGER.warning(f'duplicated data type: {data_type}. file: {each_file}. existing data_type: {granules[each_granule_id][data_type]}')
                continue
            granules[each_granule_id][data_type] = {
                'href': each_file
            }
        LOGGER.debug(f'filtering granules w/o data. original len: {len(granules)} original granules: {granules}')
        granules = {k: v for k, v in granules.items() if 'data' in v}
        LOGGER.debug(f'filtered granules. original len: {len(granules)}. granules: {granules}')
        return granules

    def __upload_granules(self, granule_assets: dict, granule_id: str):
        for data_type, href_dict in granule_assets.items():
            LOGGER.debug(f'uploading {href_dict}')
            s3_url = self.__s3.upload(href_dict['href'], self.__staging_bucket, f'{self.__collection_id}:{granule_id}', self.__delete_files)
            href_dict['href'] = s3_url
        return self

    def start(self):
        """

        1. recursively get all files from upload dir
        2. use collection id to get the links
        3. group files from step-1 into granules
        4. get granule ID ???
        5. upload to staging bucket with granuleID as key
        6. call DAPA endpoint to start the registration to cumulus
        :return:
        """
        self.__set_props_from_env()
        LOGGER.debug(f'listing files recursively in dir: {self.__upload_dir}')
        self.__raw_files = glob(f'{self.__upload_dir}/**/*', recursive=True)
        dapa_client = DapaClient().with_verify_ssl(self.__verify_ssl)
        self.__collection_details = dapa_client.get_collection(self.__collection_id)
        on_disk_granules = self.__sort_granules()
        LOGGER.debug(f'on_disk_granules: {on_disk_granules}')
        dapa_body_granules = []
        for granule_id, granule_hrefs in on_disk_granules.items():
            self.__upload_granules(granule_hrefs, granule_id)
            dapa_body_granules.append({
                'id': f'{self.__collection_id}:{granule_id}',
                'collection': self.__collection_id,
                'assets': granule_hrefs,
            })
        LOGGER.debug(f'dapa_body_granules: {dapa_body_granules}')
        dapa_body = {
            "provider_id": self.__provider_id,
            "features": dapa_body_granules
        }
        LOGGER.debug(f'dapa_body_granules: {dapa_body}')
        dapa_ingest_result = dapa_client.ingest_granules_w_cnm(dapa_body)
        return dapa_ingest_result
