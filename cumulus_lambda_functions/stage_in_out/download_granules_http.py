import shutil

import requests

from cumulus_lambda_functions.stage_in_out.download_granules_abstract import DownloadGranulesAbstract
import json
import logging
import os

LOGGER = logging.getLogger(__name__)


class DownloadGranulesHttp(DownloadGranulesAbstract):

    def __init__(self) -> None:
        super().__init__()

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.STAC_JSON, self.DOWNLOAD_DIR_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        self._retrieve_stac_json()
        self._setup_download_dir()
        return self

    def _download_one_item(self, downloading_url):
        downloading_response = requests.get(downloading_url)
        downloading_response.raise_for_status()
        downloading_response.raw.decode_content = True
        local_file_path = os.path.join(self._download_dir, os.path.basename(downloading_url))
        with open(local_file_path, 'wb') as f:
            shutil.copyfileobj(downloading_response.raw, f)
        return local_file_path
