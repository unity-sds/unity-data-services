import os
from abc import ABC, abstractmethod
from typing import List
import requests
from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract

from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class CentralAuthAbstract(ABC):
    @abstractmethod
    def request_authorization_info(self, user_token: str, delegated_username: str) -> List[str]:
        return []


class DummyImpl(CentralAuthAbstract):
    def request_authorization_info(self, user_token: str, delegated_username: str) -> List[str]:
        return ["admin", "developers", "readers"]


class KeycloakImpl(CentralAuthAbstract):
    def request_authorization_info(self, user_token: str, delegated_username: str) -> List[str]:
        """
        Query Keycloak server to retrieve user groups for a given username.
        Uses the authenticated user's JWT token to make the API call.

        Required environment variables:
        - KEYCLOAK_BASE_URL: Base URL of Keycloak server (e.g., https://keycloak.example.com)
        - KEYCLOAK_REALM: Keycloak realm name

        :param user_token: JWT bearer token of the authenticated user (with or without 'Bearer ' prefix)
        :param delegated_username: Username to query groups for
        :return: List of group names the user belongs to
        """
        keycloak_base_url = os.environ.get('KEYCLOAK_BASE_URL', '').strip()
        keycloak_realm = os.environ.get('KEYCLOAK_REALM', '').strip()

        # If Keycloak is not configured, return empty list
        if not all([keycloak_base_url, keycloak_realm]):
            LOGGER.warning('Keycloak configuration incomplete. Required: KEYCLOAK_BASE_URL, KEYCLOAK_REALM')
            return []

        try:
            # Remove 'Bearer ' prefix if present
            token = user_token.replace('Bearer ', '').replace('bearer ', '').strip()

            # Step 1: Get user ID by username using the authenticated user's token
            users_url = f'{keycloak_base_url}/admin/realms/{keycloak_realm}/users'
            headers = {'Authorization': f'Bearer {token}'}
            params = {'username': delegated_username, 'exact': 'true'}

            LOGGER.debug(f'Querying Keycloak users: {users_url}?username={delegated_username}')
            users_response = requests.get(users_url, headers=headers, params=params, timeout=10)
            users_response.raise_for_status()
            users = users_response.json()

            if not users or len(users) == 0:
                LOGGER.warning(f'User not found in Keycloak: {delegated_username}')
                return []

            user_id = users[0]['id']
            LOGGER.debug(f'Found user ID: {user_id} for username: {delegated_username}')

            # Step 2: Get user groups using the authenticated user's token
            groups_url = f'{keycloak_base_url}/admin/realms/{keycloak_realm}/users/{user_id}/groups'

            LOGGER.debug(f'Querying user groups: {groups_url}')
            groups_response = requests.get(groups_url, headers=headers, timeout=10)
            groups_response.raise_for_status()
            groups = groups_response.json()

            # Extract group names (or paths, depending on your needs)
            group_names = [group.get('name', group.get('path', '')) for group in groups]
            LOGGER.info(f'Retrieved {len(group_names)} groups for user {delegated_username}: {group_names}')

            return group_names

        except requests.exceptions.Timeout:
            LOGGER.error(f'Timeout while querying Keycloak for user: {delegated_username}')
            return []
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f'HTTP error querying Keycloak for user {delegated_username}: {e.response.status_code} - {e.response.text}')
            return []
        except requests.exceptions.RequestException as e:
            LOGGER.error(f'Error querying Keycloak for user {delegated_username}: {str(e)}')
            return []
        except Exception as e:
            LOGGER.error(f'Unexpected error querying Keycloak for user {delegated_username}: {str(e)}')
            return []


class CentralAuthFactory(FactoryAbstract):
    KEYCLOAK = 'KEYCLOAK'
    DUMMY = 'DUMMY'

    def get_instance_from_dict(self, env_dict: dict, **kwargs):
        raise NotImplementedError('not a need yet')

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError(f'not yet')

    def get_instance(self, class_type, **kwargs):
        ct = class_type.upper()
        if ct == self.KEYCLOAK:
            return KeycloakImpl()
        if ct == self.DUMMY:
            return DummyImpl()
        raise ModuleNotFoundError(f'cannot find CentralAuth class for {ct}')
