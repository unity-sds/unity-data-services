from abc import ABC, abstractmethod


class CnmPluginAbstract(ABC):
    sending_id = 'sending_id'
    collection_id = 'collection_id'
    granule_id = 'granule_id'
    target_collection_id = 'target_collection_id'
    cnm_msg = 'cnm_msg'
    status_msg = 'status_msg'
    CNM_PLUG_IN_NAMES = 'CNM_PLUG_IN_NAMES'

    def __init__(self, params: dict):
        self._params = params

    @abstractmethod
    def run(self):
        return self
