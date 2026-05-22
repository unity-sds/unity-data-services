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

    # Extract the authorization token from the event
    # API Gateway TOKEN authorizer passes the token value in 'authorizationToken' field
    token = event.get('authorizationToken', 'Fake')
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
    arn_parts = method_arn.split('/')
    resource_arn = f"{arn_parts[0]}/{arn_parts[1]}/*/*"

    # API Gateway requires all context values to be strings
    # Convert user_details to ensure all values are strings (avoid double conversion)
    context = {}
    for key, value in user_details.items():
        if key == 'groups':
            # Handle groups specially - convert list to comma-separated string
            context[key] = ','.join(value) if isinstance(value, list) else str(value)
        elif isinstance(value, str):
            # Already a string, use as-is
            context[key] = value
        else:
            # Convert non-string values (int, bool, etc.) to string
            context[key] = str(value)

    policy = {
        "principalId": user_details["username"],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": resource_arn
                }
            ]
        },
        "context": context
    }
    print(policy)
    return policy
