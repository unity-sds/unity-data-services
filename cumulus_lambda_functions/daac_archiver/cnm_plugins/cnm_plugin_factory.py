from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract

from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_status_update_plugin import CnmStatusUpdatePlugin
from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_storage_plugin import CnmStoragePlugin
from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_plugin_abstract import CnmPluginAbstract


class CnmPluginFactory(FactoryAbstract):
    STORAGE = 'STORAGE'
    STATUS_UPDATE = 'STATUS_UPDATE'

    def get_instance_from_dict(self, env_dict: dict, **kwargs):
        raise NotImplementedError('not a need yet')

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError('Not Yet')

    def get_instance(self, file_repo, **kwargs) -> CnmPluginAbstract:
        fr = file_repo.upper()
        if 'params' not in kwargs or not isinstance(kwargs['params'], dict):
            raise ValueError(f'missing or incorrect argument "params". Need to be a dictionary')
        dd1 = {
            self.STORAGE: CnmStoragePlugin,
            self.STATUS_UPDATE: CnmStatusUpdatePlugin,
        }
        if fr not in dd1:
            raise ModuleNotFoundError(f'cannot find Plugin class for {fr}')
        return dd1[fr](kwargs['params'])
