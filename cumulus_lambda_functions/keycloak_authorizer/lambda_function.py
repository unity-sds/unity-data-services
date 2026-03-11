"""
Placeholder Keycloak Lambda Authorizer
This is a temporary authorizer that allows all requests and adds fake Keycloak JWT token data.
Replace with actual Keycloak integration once available.
"""

import json
import base64

from cumulus_lambda_functions.daac_archiver.services.maap_api_client import MaapApiClient


def lambda_handler(event, context):
    """
    Placeholder Lambda authorizer that allows all requests.
    Adds fake context similar to what Keycloak would provide from a JWT token.

    :param event: API Gateway authorizer event
    :param context: Lambda context
    :return: IAM policy document allowing the request with fake user context
    """

    # Extract the authorization token (even though we're not validating it)
    token = event.get('proxy-ticket', 'Fake')
    method_arn = event.get('methodArn', '')

    user_details = MaapApiClient().get_user_details(token)
    # Create a fake JWT token payload similar to what Keycloak would provide
    # fake_jwt_payload = {
    #     "sub": "test-user-123",
    #     "preferred_username": "test-user",
    #     "email": "test-user@example.com",
    #     "name": "Test User",
    #     "given_name": "Test",
    #     "family_name": "User",
    #     "realm_access": {
    #         "roles": ["user", "admin", "developer"]
    #     },
    #     "resource_access": {
    #         "unity-api": {
    #             "roles": ["read", "write"]
    #         }
    #     },
    #     "groups": ["/unity/developers", "/unity/users"],
    #     "iat": 1642000000,
    #     "exp": 1642003600,
    #     "iss": "https://keycloak.example.com/auth/realms/unity",
    #     "aud": "unity-api"
    # }

    # Encode as base64 to simulate a JWT token in context
    # fake_jwt_string = base64.b64encode(json.dumps(fake_jwt_payload).encode()).decode()

    # Generate the IAM policy document that allows all actions
    policy = {
        "principalId": user_details["username"],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": method_arn.split('/')[0] + '/*' if method_arn else '*'
                }
            ]
        },
        "context": user_details
    }
    print(policy)
    return policy
