import os

from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_plugin_factory import CnmPluginFactory
from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_plugin_abstract import CnmPluginAbstract


class CnmPluginProcessor(CnmPluginAbstract):
    def __init__(self, params: dict):
        super().__init__(params)
        plug_in_array = [k.strip() for k in os.environ.get(CnmPluginAbstract.CNM_PLUG_IN_NAMES, '').split(',')]
        self.__plugins = [CnmPluginFactory().get_instance(k, params=params) for k in plug_in_array]

    def run(self):
        for each in self.__plugins:
            each.run()
        return self
