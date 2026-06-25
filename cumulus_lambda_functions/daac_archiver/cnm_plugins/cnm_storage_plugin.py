import os

from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_plugin_abstract import CnmPluginAbstract
from cumulus_lambda_functions.daac_archiver.raw_cnm_storage.raw_cnm_storage_factory import RawCnmStorageFactory


class CnmStoragePlugin(CnmPluginAbstract):
    def __init__(self, params: dict):
        super().__init__(params)
        required_params = [self.sending_id, self.collection_id, self.granule_id, self.target_collection_id, self.cnm_msg]
        if not all([k in self._params for k in required_params]):
            raise ValueError(f'missing required params: {required_params} v. {self._params}')

    def run(self):
        (RawCnmStorageFactory().get_instance(os.environ.get('CNM_STORAGE_CLASS'))
         .load_metadata(self._params[self.sending_id],
                        self._params[self.collection_id],
                        self._params[self.granule_id],
                        self._params[self.target_collection_id]).store_data(self._params[self.cnm_msg]))
        return self
