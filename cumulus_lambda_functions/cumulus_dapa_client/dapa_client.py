import json
import logging
import os

import requests

from cumulus_lambda_functions.lib.cognito_login.cognito_token_retriever import CognitoTokenRetriever
from cumulus_lambda_functions.lib.constants import Constants

LOGGER = logging.getLogger(__name__)


class DapaClient:
    def __init__(self):
        self.__token_retriever = CognitoTokenRetriever()
        self.__token = None
        self.__dapa_base_api = None
        self.__get_dapa_base_api()
        self.__verify_ssl = True

    def with_verify_ssl(self, verify_ssl: bool):
        self.__verify_ssl = verify_ssl
        return self

    def __get_dapa_base_api(self):
        if Constants.DAPA_API_KEY not in os.environ:
            raise ValueError(f'missing key: {Constants.DAPA_API_KEY}')
        self.__dapa_base_api = os.environ.get(Constants.DAPA_API_KEY)
        self.__dapa_base_api = self.__dapa_base_api[:-1] if self.__dapa_base_api.endswith('/') else self.__dapa_base_api
        return self

    def __get_token(self):
        if self.__token is None:
            self.__token = self.__token_retriever.start()
        if self.__token is None:
            raise ValueError('unable to retrieve DAPA token')
        return self

    def get_collection(self, collection_id: str):
        """
        TODO need better endpoint to get exactly 1 collection
        TODO pagination?
        :param collection_id:
        :return:
        """
        LOGGER.debug(f'getting collection details for: {collection_id}')
        self.__get_token()
        header = {'Authorization': f'Bearer {self.__token}'}
        dapa_collection_url = f'{self.__dapa_base_api}/am-uds-dapa/collections?limit=1000'
        response = requests.get(url=dapa_collection_url, headers=header, verify=self.__verify_ssl)
        if response.status_code > 400:
            raise RuntimeError(
                f'querying collections ends in error. status_code: {response.status_code}. url: {dapa_collection_url}. details: {response.text}')
        collections_result = json.loads(response.text)
        if 'features' not in collections_result:
            raise RuntimeError(f'missing features in response. invalid response: response: {collections_result}')
        collection_details = [each_collection for each_collection in collections_result['features'] if
                              collection_id == each_collection["id"]]
        if len(collection_details) < 1:
            raise RuntimeError(f'unable to find collection in DAPA')
        return collection_details[0]

    def get_granules(self, collection_id='*', limit=1000, offset=0, date_from='', date_to=''):
        """
        TODO: pagination. getting only 1st 1k item
        :param collection_id:
        :param limit:
        :param offset:
        :param date_from:
        :param date_to:
        :return:
        """
        dapa_granules_api = f'{self.__dapa_base_api}/am-uds-dapa/collections/{collection_id}/items?limit={limit}&offset={offset}'
        if date_from != '' or date_to != '':
            dapa_granules_api = f"{dapa_granules_api}&datetime={date_from if date_from != '' else '..'}/{date_to if date_to != '' else '..'}"
        LOGGER.debug(f'dapa_granules_api: {dapa_granules_api}')
        LOGGER.debug(f'getting granules for: {dapa_granules_api}')
        self.__get_token()
        header = {'Authorization': f'Bearer {self.__token}'}
        response = requests.get(url=dapa_granules_api, headers=header, verify=self.__verify_ssl)
        if response.status_code > 400:
            raise RuntimeError(
                f'querying granules ends in error. status_code: {response.status_code}. url: {dapa_granules_api}. details: {response.text}')
        granules_result = json.loads(response.text)
        if 'features' not in granules_result:
            raise RuntimeError(f'missing features in response. invalid response: response: {granules_result}')
        return granules_result['features']

    def ingest_granules_w_cnm(self, cnm_ingest_body: dict) -> str:
        dapa_ingest_cnm_api = f'{self.__dapa_base_api}/am-uds-dapa/collections/'
        LOGGER.debug(f'getting granules for: {dapa_ingest_cnm_api}')
        self.__get_token()
        header = {
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json',
        }
        response = requests.put(url=dapa_ingest_cnm_api, headers=header, verify=self.__verify_ssl,
                                data=json.dumps(cnm_ingest_body))
        if response.status_code > 400:
            raise RuntimeError(
                f'querying granules ingestion ends in error. status_code: {response.status_code}. url: {dapa_ingest_cnm_api}. details: {response.text}')
        granules_result = response.text
        return granules_result
