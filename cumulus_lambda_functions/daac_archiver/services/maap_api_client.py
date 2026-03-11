import json
import os

import requests
from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore


class MaapApiClient:
    def __init__(self):
        """
        API_BASE_URL = var.UDS_API_BASE_URL
        MAAP_API_HOST = var.MAAP_API_HOST
        DPS_MACHINE_TOKEN = var.DPS_MACHINE_TOKEN
        """
        self.__uds_api_param_key_path = os.getenv('UDS_API_CREDS', 'NA')
        if self.__uds_api_param_key_path == 'NA':
            raise ValueError(f'missing UDS_API_CREDS env')
        self.__uds_api_creds = json.loads(AwsParamStore().get_param(self.__uds_api_param_key_path))

    def get_user_jwt_token(self, username: str):
        url = f"{self.__uds_api_creds['MAAP_API_HOST']}/api/members/{username}"
        headers = {"dps-token": self.__uds_api_creds['DPS_MACHINE_TOKEN']}
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise ValueError(f"User '{username}' not found or invalid API endpoint: {url}. Details: {response.text}")
        elif response.status_code == 401:
            raise ValueError(f"Unauthorized: Invalid DPS_MACHINE_TOKEN")
        elif response.status_code == 403:
            raise ValueError(f"Forbidden: Access denied for user '{username}'")
        elif response.status_code >= 500:
            raise ValueError(f"Server error ({response.status_code}): {response.text}")
        elif response.status_code != 200:
            raise ValueError(f"Unexpected response ({response.status_code}): {response.text}")

        try:
            response_data = response.json()
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from MAAP API: {e}")

        if "session_key" not in response_data:
            raise ValueError(f"Missing 'session_key' in MAAP API response: {response_data}")

        maap_pgt_token = response_data["session_key"]
        return maap_pgt_token

    def get_user_details(self, user_token: str):
        url = f"{self.__uds_api_creds['MAAP_API_HOST']}/api/members/self"
        headers = {
            "accept": 'application/json',
            'proxy-ticket': user_token
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            response_body = response.text if response.text else "null body"
            raise ValueError(f"Failed to get user groups ({response.status_code}): {response_body}")

        try:
            response_data = response.json()
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from MAAP API: {e}")

        return {
            # Add fake user context that would normally come from Keycloak JWT
            "userId": response_data["id"],
            "username": response_data["username"],
            "email": response_data["email"],
            "name": f'{response_data["last_name"]},{response_data["first_name"]}',
            "roles": 'NA',
            "groups": [org["name"] for org in response_data["organizations"] if "name" in org],
            # Fake JWT token (base64 encoded) - simulating what Keycloak would provide
            "jwtToken": response_data['session_key'],  # TODO It's PGT though, not JWT
            # Add a flag to indicate this is a placeholder
            "authType": "PLACEHOLDER_KEYCLOAK"
        }


