from abc import ABC, abstractmethod
from typing import Any, Union, Callable

DEFAULT_TYPE = '_doc'


class ESAbstract(ABC):
    @abstractmethod
    def migrate_index_data(self, old_index, new_index):
        return
    @abstractmethod
    def create_index(self, index_name, index_body):
        return

    @abstractmethod
    def get_index_mapping(self, index_name):
        return {}

    @abstractmethod
    def has_index(self, index_name):
        return

    @abstractmethod
    def swap_index_for_alias(self, alias_name, old_index_name, new_index_name):
        return

    @abstractmethod
    def get_alias(self, alias_name):
        return

    @abstractmethod
    def create_alias(self, index_name, alias_name):
        return

    @abstractmethod
    def delete_index(self, index_name):
        return

    @abstractmethod
    def index_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        return

    @abstractmethod
    def index_one(self, doc, doc_id, index=None):
        return

    @abstractmethod
    def update_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        return

    @abstractmethod
    def update_one(self, doc, doc_id, index=None):
        return

    @staticmethod
    @abstractmethod
    def get_result_size(result):
        return

    @abstractmethod
    def query_with_scroll(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query(self, dsl, querying_index=None):
        return

    @abstractmethod
    def delete_by_query(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query_pages(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query_by_id(self, doc_id, querying_index=None):
        return
