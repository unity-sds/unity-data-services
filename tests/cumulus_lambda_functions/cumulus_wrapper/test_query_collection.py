import json
import logging
from datetime import datetime
from unittest import TestCase

from cumulus_lambda_functions.cumulus_wrapper.query_collections import CollectionsQuery
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator


class TestQueryCollection(TestCase):
    def test_01(self):
        lambda_prefix = 'uds-dev-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_version = int(datetime.utcnow().timestamp())
        sample_collection = {
            # "dataType": "MOD09GQ",
            # "provider_path": "cumulus-test-data/pdrs",
            "name": "UNITY_CUMULUS_DEV_UNIT_TEST",
            "version": str(collection_version),
            # "process": "modis",
            # "duplicateHandling": "skip",
            "granuleId": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$",
            "granuleIdExtraction": "(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+",
            # "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}",
            "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
            "files": [
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS\\.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS.xml",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00.PDS.cmr.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml",
                    "reportToEms": True,
                    "type": "metadata"
                }
            ],
        }
        # sample_collection = {
        #     "createdAt": 1647992847582,
        #     "reportToEms": True,
        #     "updatedAt": 1647992847582,
        #     "timestamp": 1647992849273
        # }
        response = collection_query.create_collection(sample_collection, lambda_prefix)
        self.assertTrue('status' in response, f'status not in response: {response}')
        self.assertEqual('Record saved', response['status'], f'wrong status: {response}')

        delete_response = collection_query.delete_collection(lambda_prefix, 'UNITY_CUMULUS_DEV_UNIT_TEST', str(collection_version))
        self.assertTrue('status' in delete_response, f'status not in response: {response}')
        self.assertEqual('Record deleted', delete_response['status'], f'wrong status: {response}')

        return

    def test_02(self):
        lambda_prefix = 'uds-dev-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_query.with_limit(2)
        collections = collection_query.query_direct_to_private_api(lambda_prefix, 's3://abcd')
        self.assertTrue('results' in collections, f'results not in collections: {collections}')
        # self.assertEqual(2, len(collections['results']), f'wrong length: {collections}')
        return

    def test_03(self):
        lambda_prefix = 'uds-dev-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_query.with_limit(2)
        collection_query.with_collection_id('CUMULUS_DAPA_UNIT_TEST___1663627653')
        collections = collection_query.query_direct_to_private_api(lambda_prefix, 's3://abcd')
        self.assertTrue('results' in collections, f'results not in collections: {collections}')
        # self.assertEqual(1, len(collections['results']), f'wrong length: {collections}')
        # self.assertEqual('CUMULUS_DAPA_UNIT_TEST___1663627653', collections['results'][0]['id'], f'wrong id (DAPA style)')
        return

    def test_04(self):
        lambda_prefix = 'uds-dev-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_query.with_limit(2)
        collection_query.with_collection_id('CUMULUS_DAPA_UNIT_TEST___1663627653')
        collections = collection_query.get_size(lambda_prefix)
        self.assertTrue('total_size' in collections, f'total_size not in collections: {collections}')
        # self.assertEqual(1, collections['total_size'], f'wrong size: {collections}')
        return


    def test_rules_03(self):
        LambdaLoggerGenerator.remove_default_handlers()
        # logging.basicConfig(level=20,
        #                     format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")

        lambda_prefix = 'uds-dev-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_version = int(datetime.utcnow().timestamp())
        sample_collection = {
            # "dataType": "MOD09GQ",
            # "provider_path": "cumulus-test-data/pdrs",
            "name": "UNITY_CUMULUS_DEV_UNIT_TEST",
            "version": str(collection_version),
            # "process": "modis",
            # "duplicateHandling": "skip",
            "granuleId": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$",
            "granuleIdExtraction": "(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+",
            # "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}",
            "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
            "files": [
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS\\.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS.xml",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00.PDS.cmr.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml",
                    "reportToEms": True,
                    "type": "metadata"
                }
            ],
        }
        # sample_collection = {
        #     "createdAt": 1647992847582,
        #     "reportToEms": True,
        #     "updatedAt": 1647992847582,
        #     "timestamp": 1647992849273
        # }
        response = collection_query.create_collection(sample_collection, lambda_prefix)
        self.assertTrue('status' in response, f'status not in response: {response}')
        self.assertEqual('Record saved', response['status'], f'wrong status: {response}')

        response = collection_query.create_sqs_rules(
            sample_collection,
            lambda_prefix,
            'https://sqs.us-west-2.amazonaws.com/884500545225/uds-dev-cumulus-cnm-submission-queue',
            'SNPP',
            'CatalogGranule'
        )
        self.assertTrue('status' in response, f'status not in response: {response}')
        self.assertEqual('Record saved', response['status'], f'wrong status: {response}')
        return

    def test_rules_04(self):
        lambda_prefix = 'uds-sbx-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        collection_query.with_limit(200)
        rules = collection_query.query_rules(lambda_prefix)
        print(json.dumps(rules, indent=4))
        # self.assertTrue(False, rules)
        return

    def test_create_provider(self):
        lambda_prefix = 'uds-sbx-cumulus'
        collection_query = CollectionsQuery('NA', 'NA')
        result = collection_query.create_provider('unity', lambda_prefix)
        print(result)
        return
