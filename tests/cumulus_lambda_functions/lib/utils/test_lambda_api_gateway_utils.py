import unittest

from cumulus_lambda_functions.lib.utils.lambda_api_gateway_utils import LambdaApiGatewayUtils


class TestCognitoLogin(unittest.TestCase):
    def test_01(self):
        sample_event = {
            'resource': '/am-uds-dapa/collections/{collectionId}/items',
            'path': '/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items', 'httpMethod': 'GET',
            'headers': {'accept': '*/*',
                        'Authorization': 'Bearer eyJraWQiOiJzdE42WWl0eGxWZmJnY1ByRnJLWVQ1MEdjVWRIZWNBaWFKQ09peUxLVHNZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwMGRkYTdmNy1mNjE4LTRmNDMtYWFmNC1iYmM4YmExNDc2ODAiLCJjb2duaXRvOmdyb3VwcyI6WyJVbml0eV9WaWV3ZXIiLCJVbml0eV9BZG1pbiJdLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9GTER5WEUybU8iLCJjbGllbnRfaWQiOiI3YTFmZ2xtMmQ1NGVvZ2dqMTNsY2NpdnAyNSIsIm9yaWdpbl9qdGkiOiI3MDcyZjQ2NC1mMWFjLTQzYjMtOTQ5Yy1iM2JjZTA1YWExOGEiLCJldmVudF9pZCI6IjUxMjk3NTA3LTdkMGMtNDcyYi1hNjM1LTY4YWJmNzJiZTZlMiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTk3MTUxNzMsImV4cCI6MTY1OTcxODc3MywiaWF0IjoxNjU5NzE1MTczLCJqdGkiOiJiZmU2ZWY2OS1mNTc0LTQ1OTMtYjFlZi1iYmRhNzQ0NjFkMTciLCJ1c2VybmFtZSI6IndwaHlvIn0.X1K9NeZ661nCbD4PoNe_ZsjZITrs_OEzQ0ZjbsYGAQXCFwQmCaGiHhj0klb9xs8ByJ4VG7il8p_nu96QG0nkuv-HQXjG6YDxcA72rIvxK7w4LVF6_SxacDLHGsr3669Ptz6mzG5ql5AhDgiwCAYVgvlDyqtMNrbOEIe6HZDz6Hn12DUkk_7pgbZA77mtzikDrsSdJlT3RknuAooeZZGRwqnLsRZ7l4dw25uhPKjYDBSF6Psbc9IfzqvE-rTnloQ5atS6E5XL_Ig4YACBVDMqVqfiX11Uj5hxe2oI3t7o9JeePSwfwG-Z13zeI0XeldkaZW2E30qAzpob3EeQzuw_OQ',
                        'Host': 'k3a3qmarxh.execute-api.us-west-2.amazonaws.com', 'User-Agent': 'curl/7.64.1',
                        'X-Amzn-Trace-Id': 'Root=1-62ed40e1-6302916f16a2262c4f6012cf',
                        'X-Forwarded-For': '128.149.247.57',
                        'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'},
            'multiValueHeaders': {'accept': ['*/*'],
                                  'Authorization': [
                                      'Bearer eyJraWQiOiJzdE42WWl0eGxWZmJnY1ByRnJLWVQ1MEdjVWRIZWNBaWFKQ09peUxLVHNZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwMGRkYTdmNy1mNjE4LTRmNDMtYWFmNC1iYmM4YmExNDc2ODAiLCJjb2duaXRvOmdyb3VwcyI6WyJVbml0eV9WaWV3ZXIiLCJVbml0eV9BZG1pbiJdLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9GTER5WEUybU8iLCJjbGllbnRfaWQiOiI3YTFmZ2xtMmQ1NGVvZ2dqMTNsY2NpdnAyNSIsIm9yaWdpbl9qdGkiOiI3MDcyZjQ2NC1mMWFjLTQzYjMtOTQ5Yy1iM2JjZTA1YWExOGEiLCJldmVudF9pZCI6IjUxMjk3NTA3LTdkMGMtNDcyYi1hNjM1LTY4YWJmNzJiZTZlMiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTk3MTUxNzMsImV4cCI6MTY1OTcxODc3MywiaWF0IjoxNjU5NzE1MTczLCJqdGkiOiJiZmU2ZWY2OS1mNTc0LTQ1OTMtYjFlZi1iYmRhNzQ0NjFkMTciLCJ1c2VybmFtZSI6IndwaHlvIn0.X1K9NeZ661nCbD4PoNe_ZsjZITrs_OEzQ0ZjbsYGAQXCFwQmCaGiHhj0klb9xs8ByJ4VG7il8p_nu96QG0nkuv-HQXjG6YDxcA72rIvxK7w4LVF6_SxacDLHGsr3669Ptz6mzG5ql5AhDgiwCAYVgvlDyqtMNrbOEIe6HZDz6Hn12DUkk_7pgbZA77mtzikDrsSdJlT3RknuAooeZZGRwqnLsRZ7l4dw25uhPKjYDBSF6Psbc9IfzqvE-rTnloQ5atS6E5XL_Ig4YACBVDMqVqfiX11Uj5hxe2oI3t7o9JeePSwfwG-Z13zeI0XeldkaZW2E30qAzpob3EeQzuw_OQ'],
                                  'Host': [
                                      'k3a3qmarxh.execute-api.us-west-2.amazonaws.com'],
                                  'User-Agent': [
                                      'curl/7.64.1'],
                                  'X-Amzn-Trace-Id': [
                                      'Root=1-62ed40e1-6302916f16a2262c4f6012cf'],
                                  'X-Forwarded-For': [
                                      '128.149.247.57'],
                                  'X-Forwarded-Port': [
                                      '443'],
                                  'X-Forwarded-Proto': [
                                      'https']},
            'queryStringParameters': {'datetime': '1990-01-01T00:00:00Z/2021-01-03T00:00:00Z'},
            'multiValueQueryStringParameters': {'datetime': ['1990-01-01T00:00:00Z/2021-01-03T00:00:00Z']},
            'pathParameters': {'collectionId': 'L0_SNPP_ATMS_SCIENCE___1'}, 'stageVariables': {'VPCLINK': 'czcxgk'},
            'requestContext': {'resourceId': 'pm8zuj',
                               'authorizer': {'numberKey': '123', 'booleanKey': 'true', 'stringKey': 'stringval',
                                              'principalId': 'user', 'integrationLatency': 70},
                               'resourcePath': '/am-uds-dapa/collections/{collectionId}/items', 'httpMethod': 'GET',
                               'extendedRequestId': 'WZcTREQqvHcFztw=', 'requestTime': '05/Aug/2022:16:10:09 +0000',
                               'path': '/dev/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items',
                               'accountId': '884500545225', 'protocol': 'HTTP/1.1', 'stage': 'dev',
                               'domainPrefix': 'k3a3qmarxh', 'requestTimeEpoch': 1659715809560,
                               'requestId': '240ae2fb-c5cc-4e83-9040-d44ed127c889',
                               'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None,
                                            'caller': None, 'sourceIp': '128.149.247.57', 'principalOrgId': None,
                                            'accessKey': None, 'cognitoAuthenticationType': None,
                                            'cognitoAuthenticationProvider': None, 'userArn': None,
                                            'userAgent': 'curl/7.64.1',
                                            'user': None},
                               'domainName': 'k3a3qmarxh.execute-api.us-west-2.amazonaws.com',
                               'apiId': 'k3a3qmarxh'},
            'body': None,
            'isBase64Encoded': False
        }
        next_url = 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items?datetime=1990-01-01T00:00:00Z/2021-01-03T00:00:00Z&limit=10&offset=10'
        prev_url = 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items?datetime=1990-01-01T00:00:00Z/2021-01-03T00:00:00Z&limit=10&offset=0'
        self.assertEqual(sorted(next_url), sorted(LambdaApiGatewayUtils.generate_next_url(sample_event, 10)), f'wrong next url')
        self.assertEqual(sorted(prev_url), sorted(LambdaApiGatewayUtils.generate_prev_url(sample_event, 10)), f'wrong prev url')
        self.assertEqual('', LambdaApiGatewayUtils.generate_next_url(sample_event, 0), f'wrong next empty url')
        self.assertEqual('', LambdaApiGatewayUtils.generate_prev_url(sample_event, 0), f'wrong next empty url')
        sample_event['queryStringParameters']['offset'] = 10
        next_url = 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items?datetime=1990-01-01T00:00:00Z/2021-01-03T00:00:00Z&limit=5&offset=15'
        prev_url = 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev/am-uds-dapa/collections/L0_SNPP_ATMS_SCIENCE___1/items?datetime=1990-01-01T00:00:00Z/2021-01-03T00:00:00Z&limit=5&offset=5'
        self.assertEqual(sorted(next_url), sorted(LambdaApiGatewayUtils.generate_next_url(sample_event, 5)), f'wrong next url 2')
        self.assertEqual(sorted(prev_url), sorted(LambdaApiGatewayUtils.generate_prev_url(sample_event, 5)), f'wrong prev url 2')
        return
