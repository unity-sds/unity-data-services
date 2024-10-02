import json
import logging
import os.path
from glob import glob
from multiprocessing import Manager

from cumulus_lambda_functions.cumulus_stac.granules_catalog import GranulesCatalog

from cumulus_lambda_functions.lib.aws.aws_s3 import AwsS3
from cumulus_lambda_functions.lib.processing_jobs.job_manager_memory import JobManagerMemory
from cumulus_lambda_functions.lib.processing_jobs.multithread_processor import MultiThreadProcessorProps, MultiThreadProcessor
from cumulus_lambda_functions.lib.processing_jobs.job_manager_abstract import JobManagerProps
from cumulus_lambda_functions.lib.utils.file_utils import FileUtils
from cumulus_lambda_functions.lib.processing_jobs.job_executor_abstract import JobExecutorAbstract
from cumulus_lambda_functions.lib.time_utils import TimeUtils
from cumulus_lambda_functions.stage_in_out.upload_granules_abstract import UploadGranulesAbstract
from pystac import Item, Asset, ItemCollection, Catalog, Link

LOGGER = logging.getLogger(__name__)


class UploadItemExecutor(JobExecutorAbstract):
    def __init__(self, result_list, error_list, collection_id, staging_bucket, retry_wait_time_sec, retry_times, delete_files: bool) -> None:
        super().__init__()
        self.__collection_id = collection_id
        self.__staging_bucket = staging_bucket
        self.__delete_files = delete_files

        self.__gc = GranulesCatalog()
        self.__result_list = result_list
        self.__error_list = error_list
        # self.__gc = GranulesCatalog()
        self.__s3 = AwsS3()
        self.__retry_wait_time_sec = retry_wait_time_sec
        self.__retry_times = retry_times

    def validate_job(self, job_obj):
        return True

    def generate_sample_stac(self, filepath: str):
        filename = os.path.basename(filepath)
        file_checksum = FileUtils.get_checksum(filepath, True)
        # https://github.com/stac-extensions/file
        # https://github.com/stac-extensions/file/blob/main/examples/item.json
        sample_stac_item = Item(
                         id=f'{self.__collection_id}:{os.path.splitext(filename)[0]}',
                         stac_extensions=["https://stac-extensions.github.io/file/v2.1.0/schema.json"],
                         geometry={
                             "type": "Point",
                             "coordinates": [0.0, 0.0]
                         },
                         bbox=[0.0, 0.0, 0.0, 0.0],
                         datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                         properties={
                             "start_datetime": TimeUtils.get_current_time(),
                             "end_datetime": TimeUtils.get_current_time(),
                             "created": TimeUtils.get_current_time(),
                             "updated": TimeUtils.get_current_time(),
                         },
                         collection=self.__collection_id,
                         assets={
                             filename: Asset(
                                 href=filepath,
                                 roles=['data'],
                                 title=os.path.basename(filename),
                                 extra_fields={
                                     'file:size': FileUtils.get_size(filepath),
                                     'file:checksum': file_checksum,
                                 },
                                 description=f'size={FileUtils.get_size(filepath)};checksumType=md5;checksum={file_checksum}'),
                             f'{filename}.stac.json': Asset(href=f'{filepath}.stac.json', roles=['metadata'], description='desc=metadata stac;size=-1;checksumType=md5;checksum=unknown'),  # How to update this? It's a circular dependency
                         })

        return sample_stac_item

    def execute_job(self, job_obj, lock) -> bool:
        sample_stac_item = self.generate_sample_stac(job_obj)
        updating_assets = {}
        try:
            s3_url = self.__s3.upload(job_obj, self.__staging_bucket, f'{self.__collection_id}/{self.__collection_id}:{sample_stac_item.id}', self.__delete_files)
            updating_assets[os.path.basename(s3_url)] = s3_url
            uploading_current_granule_stac = f'{s3_url}.stac.json'
            self.__s3.set_s3_url(uploading_current_granule_stac)
            self.__s3.upload_bytes(json.dumps(sample_stac_item.to_dict(False, False),indent=4).encode())
            updating_assets[os.path.basename(uploading_current_granule_stac)] = uploading_current_granule_stac
            self.__gc.update_assets_href(sample_stac_item, updating_assets)
            self.__result_list.put(sample_stac_item.to_dict(False, False))
        except Exception as e:
            sample_stac_item.properties['upload_error'] = str(e)
            LOGGER.exception(f'error while processing: {job_obj}')
            self.__error_list.put(sample_stac_item.to_dict(False, False))
        return True


class UploadArbitraryFilesAsGranules(UploadGranulesAbstract):
    BASE_DIRECTORY = 'BASE_DIRECTORY'

    def __init__(self):
        super().__init__()
        self.__s3 = AwsS3()

    def upload(self, **kwargs) -> str:

        """
        1. Use Glob to find files
        2. Create stac.json for each file.
        3. Need collection ID which has tenant + venue.
        4. Create successful features.json
        :param kwargs:
        :return:
        """
        self._set_props_from_env()
        output_dir = os.environ.get(self.OUTPUT_DIRECTORY)
        if not FileUtils.dir_exist(output_dir):
            raise ValueError(f'OUTPUT_DIRECTORY: {output_dir} does not exist')
        missing_keys = [k for k in [self.BASE_DIRECTORY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        base_dir = os.environ.get(self.BASE_DIRECTORY)
        possible_files = [k for k in glob(os.path.join(base_dir, '**'), recursive=True) if os.path.isfile(k)]

        local_items = Manager().Queue()
        error_list = Manager().Queue()

        if self._parallel_count == 1:
            for each_child in possible_files:
                temp_job = UploadItemExecutor(local_items, error_list, self._collection_id, self._staging_bucket, self._retry_wait_time_sec, self._retry_times, self._delete_files)
                temp_job.execute_job(each_child, None)
        else:
            job_manager_props = JobManagerProps()
            for each_child in possible_files:
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
        catalog = Catalog(
            id='NA',
            description='NA')
        catalog.add_link(Link('item', successful_features_file, 'application/json'))
        catalog.add_link(Link('item', failed_features_file, 'application/json'))
        catalog_json = catalog.to_dict(False, False)
        LOGGER.debug(f'catalog_json: {catalog_json}')
        return json.dumps(catalog_json)
