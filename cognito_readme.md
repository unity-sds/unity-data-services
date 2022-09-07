- create a text file: `cognito.jpl.aws.json`

        {
           "AuthParameters" : {
              "USERNAME" : "username",
              "PASSWORD" : "password"
           },
           "AuthFlow" : "USER_PASSWORD_AUTH",
           "ClientId" : "7a1fglm2d54eoggj13lccivp25"
        }
- ask U-CS to create credentials and change password the first time
- run this command (JPL AWS):

        curl -X POST --data @cognito.jpl.aws.json -H 'X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth' -H 'Content-Type: application/x-amz-json-1.1' https://cognito-idp.us-west-2.amazonaws.com/|jq
        curl -X POST --data @cognito.mcp.test.aws.json -H 'X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth' -H 'Content-Type: application/x-amz-json-1.1' https://cognito-idp.us-west-2.amazonaws.com/|jq
        curl -X POST --data @cognito.mcp.dev.aws.json -H 'X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth' -H 'Content-Type: application/x-amz-json-1.1' https://cognito-idp.us-west-2.amazonaws.com/|jq
- successful response:

        {
          "AuthenticationResult": {
            "AccessToken": "token",
            "ExpiresIn": 3600,
            "IdToken": "token",
            "RefreshToken": "token",
            "TokenType": "Bearer"
          },
          "ChallengeParameters": {}
        } 
- store `AccessToken` in environment variable: `export unity_token=<token>`
- start calling API gateway endpoints

        curl -k -H "Authorization: Bearer $unity_token" 'https://k3a3qmarxh.execute-api.us-west-2.amazonaws.com/dev/am-uds-dapa/collections'
