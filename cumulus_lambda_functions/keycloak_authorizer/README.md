# Keycloak Authorizer (Placeholder)

This is a **temporary placeholder** Lambda authorizer that allows all requests for testing purposes.

## Current Behavior

- **Allows all requests** without validation
- Adds fake JWT token context similar to what Keycloak would provide
- Returns fake user information for testing

## Fake Context Provided

The authorizer adds the following fake context to requests:

- `userId`: test-user-123
- `username`: test-user
- `email`: test-user@example.com
- `name`: Test User
- `roles`: ["user", "admin", "developer"]
- `groups`: ["/unity/developers", "/unity/users"]
- `jwtToken`: Base64-encoded fake JWT payload
- `authType`: PLACEHOLDER_KEYCLOAK (flag to indicate this is a placeholder)

## TODO

⚠️ **Replace with actual Keycloak integration** once Keycloak is connected and configured.

The actual implementation should:
1. Validate JWT tokens from Keycloak
2. Verify token signatures
3. Check token expiration
4. Extract real user claims from the token
5. Enforce proper authorization policies
