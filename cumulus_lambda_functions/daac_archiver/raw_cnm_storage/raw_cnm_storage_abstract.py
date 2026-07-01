from abc import ABC, abstractmethod


class RawCnmStorageAbstract(ABC):
    @abstractmethod
    def load_metadata(self, sending_id, collection_id, granule_id, target_collection_id):
        return self

    @abstractmethod
    def store_data(self, cnm_msg: dict):
        return self
