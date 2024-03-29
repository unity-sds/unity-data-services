from abc import ABC, abstractmethod


class UDSAuthorizorAbstract(ABC):
    @abstractmethod
    def add_authorized_group(self, action: [str], resource: [str], tenant: str, venue: str, ldap_group_name: str):
        return

    @abstractmethod
    def delete_authorized_group(self, tenant: str, venue: str, ldap_group_name: str):
        return

    @abstractmethod
    def list_groups(self, tenant: str, venue: str, ldap_group_names: list):
        return

    @abstractmethod
    def list_authorized_groups_for(self, tenant: str, venue: str):
        return

    @abstractmethod
    def update_authorized_group(self, action: [str], resource: [str], tenant: str, venue: str, ldap_group_name: str):
        return

    @abstractmethod
    def is_authorized_for_collection(self, action: str, collection_id: str, ldap_groups: list, tenant: str, venue: str):
        return

    @abstractmethod
    def get_authorized_collections(self, action: str, ldap_groups: list, tenant: str = '', venue: str = ''):
        return
