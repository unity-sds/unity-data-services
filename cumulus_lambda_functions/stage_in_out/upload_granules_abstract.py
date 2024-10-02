import os
from abc import ABC, abstractmethod

from cumulus_lambda_functions.lib.constants import Constants


class UploadGranulesAbstract(ABC):
    RESULT_PATH_PREFIX = 'RESULT_PATH_PREFIX'  # s3 prefix
    DEFAULT_RESULT_PATH_PREFIX = 'stage_out'  # default s3 prefix
    OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'  # To store successful & failed features json
    COLLECTION_ID_KEY = 'COLLECTION_ID'  # Need this
    STAGING_BUCKET_KEY = 'STAGING_BUCKET'  # S3 Bucket
    VERIFY_SSL_KEY = 'VERIFY_SSL'
    DELETE_FILES_KEY = 'DELETE_FILES'

    def __init__(self) -> None:
        super().__init__()
        self._collection_id = ''
        self._staging_bucket = ''
        self._result_path_prefix = ''
        self._parallel_count = int(os.environ.get(Constants.PARALLEL_COUNT, '-1'))
        self._retry_wait_time_sec = int(os.environ.get('UPLOAD_RETRY_WAIT_TIME', '30'))
        self._retry_times = int(os.environ.get('UPLOAD_RETRY_TIMES', '5'))
        self._verify_ssl = True
        self._delete_files = False

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.COLLECTION_ID_KEY, self.STAGING_BUCKET_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self._collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        self._staging_bucket = os.environ.get(self.STAGING_BUCKET_KEY)
        self._result_path_prefix = os.environ.get(self.RESULT_PATH_PREFIX, self.DEFAULT_RESULT_PATH_PREFIX)
        self._result_path_prefix = self._result_path_prefix[:-1] if self._result_path_prefix.endswith('/') else self._result_path_prefix
        self._result_path_prefix = self._result_path_prefix[1:] if self._result_path_prefix.startswith('/') else self._result_path_prefix

        self._verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        self._delete_files = os.environ.get(self.DELETE_FILES_KEY, 'FALSE').strip().upper() == 'TRUE'
        return self

    @abstractmethod
    def upload(self, **kwargs) -> str:
        raise NotImplementedError()
