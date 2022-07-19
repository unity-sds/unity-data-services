- building docker file for Granules Download
        
        docker build -f ./docker/Dockerfile_download_granules.jpl -t cumulus_unity:1.0.0-t1 .
        
- running docker file for Granules Download
    - update the environment variables

        docker-compose -f docker/docker-compose-granules-download.yaml up
- Unity Token in docker-compose ENV
    - if `UNITY_BEARER_TOKEN` in ENV, that token is used. to authenticate. 
    - if not, the following ENVs are needed
    
          USERNAME: 'plain text | AWS parameter store key | base64 encoded str'
          PASSWORD: 'plain text | AWS parameter store key | base64 encoded str'
          PASSWORD_TYPE: 'PLAIN | PARAM_STORE | BASE64'
          CLIENT_ID: 'ask U-CS. ex: 7a1fglm2d54eoggj13lccivp25'
          COGNITO_URL: 'ask U-CS. ex: https://cognito-idp.us-west-2.amazonaws.com'

    - There are 3 `PASSWORD_TYPE`: `PLAIN | PARAM_STORE | BASE64`. If missing `PLAIN` is assumed. 
    - `USERNAME` and `PASSWORD` needs to be set accordingly. 
        
