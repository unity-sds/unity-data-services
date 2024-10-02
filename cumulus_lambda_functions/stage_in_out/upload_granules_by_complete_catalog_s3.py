import json
import time
from multiprocessing import Manager

from cumulus_lambda_functions.lib.time_utils import TimeUtils

from cumulus_lambda_functions.lib.utils.file_utils import FileUtils

from cumulus_lambda_functions.lib.constants import Constants
from pystac import ItemCollection

from cumulus_lambda_functions.cumulus_stac.granules_catalog import GranulesCatalog
from cumulus_lambda_functions.lib.processing_jobs.job_executor_abstract import JobExecutorAbstract
from cumulus_lambda_functions.lib.processing_jobs.job_manager_abstract import JobManagerProps
from cumulus_lambda_functions.lib.processing_jobs.job_manager_memory import JobManagerMemory
from cumulus_lambda_functions.lib.processing_jobs.multithread_processor import MultiThreadProcessorProps, \
    MultiThreadProcessor
from cumulus_lambda_functions.stage_in_out.upload_granules_abstract import UploadGranulesAbstract
import logging
import os
from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3

LOGGER = logging.getLogger(__name__)


class UploadItemExecutor(JobExecutorAbstract):
    def __init__(self, result_list, error_list, collection_id, staging_bucket, retry_wait_time_sec, retry_times, delete_files: bool) -> None:
        super().__init__()
        self.__collection_id = collection_id
        self.__staging_bucket = staging_bucket
        self.__delete_files = delete_files

        self.__result_list = result_list
        self.__error_list = error_list
        self.__gc = GranulesCatalog()
        self.__s3 = AwsS3()
        self.__retry_wait_time_sec = retry_wait_time_sec
        self.__retry_times = retry_times

    def validate_job(self, job_obj):
        return True

    # def __upload_function_w_retry(self, ):
    # NOTE: 2023-10-09: we are not proceeding with "retry" logic at this moment as most the errors (when failed to upload) are not transient.
    #     upload_try_count = 1
    #     while r.status_code in [502, 504] and upload_try_count < self.__retry_times:
    #         LOGGER.error(f'502 or 504 while downloading {upload_try_count}. attempt: {upload_try_count}')
    #         time.sleep(self.__retry_wait_time_sec)
    #         upload_try_count += 1
    #     return

    def execute_job(self, each_child, lock) -> bool:
        current_granule_stac = self.__gc.get_granules_item(each_child)
        try:
            current_granules_dir = os.path.dirname(each_child)
            current_assets = self.__gc.extract_assets_href(current_granule_stac, current_granules_dir)
            if 'data' not in current_assets:  # this is still ok .coz extract_assets_href is {'data': [url1, url2], ...}
                LOGGER.warning(f'skipping {each_child}. no data in {current_assets}')
                current_granule_stac.properties['upload_error'] = f'missing "data" in assets'
                self.__error_list.put(current_granule_stac.to_dict(False, False))
                return True
            current_granule_id = str(current_granule_stac.id)
            if current_granule_id in ['', 'NA', None]:
                raise ValueError(f'invalid current_granule_id in granule {each_child}: {current_granule_id} ...')
            updating_assets = {}
            uploading_current_granule_stac = None
            for asset_type, asset_hrefs in current_assets.items():
                for each_asset_href in asset_hrefs:
                    LOGGER.debug(f'uploading {asset_type}, {each_asset_href}')
                    s3_url = self.__s3.upload(each_asset_href, self.__staging_bucket,
                                              f'{self.__collection_id}/{self.__collection_id}:{current_granule_id}',
                                              self.__delete_files)
                    if each_asset_href == each_child:
                        uploading_current_granule_stac = s3_url
                    updating_assets[os.path.basename(s3_url)] = s3_url
            self.__gc.update_assets_href(current_granule_stac, updating_assets)
            current_granule_stac.id = current_granule_id
            current_granule_stac.collection_id = self.__collection_id
            if uploading_current_granule_stac is not None:  # upload metadata file again
                self.__s3.set_s3_url(uploading_current_granule_stac)
                self.__s3.upload_bytes(json.dumps(current_granule_stac.to_dict(False, False)).encode())
            current_granule_stac.id = f'{self.__collection_id}:{current_granule_id}'
            self.__result_list.put(current_granule_stac.to_dict(False, False))
        except Exception as e:
            current_granule_stac.properties['upload_error'] = str(e)
            LOGGER.exception(f'error while processing: {each_child}')
            self.__error_list.put(current_granule_stac.to_dict(False, False))
        return True


class UploadGranulesByCompleteCatalogS3(UploadGranulesAbstract):
    CATALOG_FILE = 'CATALOG_FILE'

    def __init__(self) -> None:
        super().__init__()
        self.__gc = GranulesCatalog()
        self.__s3 = AwsS3()

    def upload(self, **kwargs) -> str:
        self._set_props_from_env()
        output_dir = os.environ.get(self.OUTPUT_DIRECTORY)
        if not FileUtils.dir_exist(output_dir):
            raise ValueError(f'OUTPUT_DIRECTORY: {output_dir} does not exist')
        missing_keys = [k for k in [self.CATALOG_FILE] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        catalog_file_path = os.environ.get(self.CATALOG_FILE)
        child_links = self.__gc.get_child_link_hrefs(catalog_file_path)
        local_items = Manager().Queue()
        error_list = Manager().Queue()
        job_manager_props = JobManagerProps()
        for each_child in child_links:
            job_manager_props.memory_job_dict[each_child] = each_child

        # https://www.infoworld.com/article/3542595/6-python-libraries-for-parallel-processing.html
        multithread_processor_props = MultiThreadProcessorProps(self._parallel_count)
        multithread_processor_props.job_manager = JobManagerMemory(job_manager_props)
        multithread_processor_props.job_executor = UploadItemExecutor(local_items, error_list, self._collection_id, self._staging_bucket, self._retry_wait_time_sec, self._retry_times, self._delete_files)
        multithread_processor = MultiThreadProcessor(multithread_processor_props)
        multithread_processor.start()

        LOGGER.debug(f'finished uploading all granules')
        dapa_body_granules = []
        while not local_items.empty():
            dapa_body_granules.append(local_items.get())

        errors = []
        while not error_list.empty():
            errors.append(error_list.get())
        LOGGER.debug(f'successful count: {len(dapa_body_granules)}. failed count: {len(errors)}')
        successful_item_collections = ItemCollection(items=dapa_body_granules)
        failed_item_collections = ItemCollection(items=errors)
        successful_features_file = os.path.join(output_dir, 'successful_features.json')



        failed_features_file = os.path.join(output_dir, 'failed_features.json')
        LOGGER.debug(f'writing results: {successful_features_file} && {failed_features_file}')
        FileUtils.write_json(successful_features_file, successful_item_collections.to_dict(False))
        FileUtils.write_json(failed_features_file, failed_item_collections.to_dict(False))
        s3_url = self.__s3.upload(successful_features_file, self._staging_bucket,
                                  self._result_path_prefix,
                                  s3_name=f'successful_features_{TimeUtils.get_current_time()}.json',
                                  delete_files=self._delete_files)
        LOGGER.debug(f'uploaded successful features to S3: {s3_url}')
        LOGGER.debug(f'creating response catalog')
        catalog_json = GranulesCatalog().update_catalog(catalog_file_path, [successful_features_file, failed_features_file])
        LOGGER.debug(f'catalog_json: {catalog_json}')
        return json.dumps(catalog_json)
