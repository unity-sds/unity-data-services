cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["DOWNLOAD"]

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/unity-sds/unity-data-services:9.0.0
  EnvVarRequirement:
    envDef:
      DOWNLOAD_DIR: $(runtime.outdir)/$(inputs.download_dir)
      STAC_JSON: $(inputs.stac_json)
      GRANULES_DOWNLOAD_TYPE: 'S3'
      LOG_LEVEL: '10'
      PARALLEL_COUNT: '-1'
      DOWNLOAD_RETRY_WAIT_TIME: '30'
      DOWNLOAD_RETRY_TIMES: '5'
      DOWNLOADING_ROLES: 'data'

      CLIENT_ID: $(inputs.unity_client_id)
      COGNITO_URL: $(inputs.unity_cognito_url)
      USERNAME: '/sps/processing/workflows/unity_username'
      PASSWORD: '/sps/processing/workflows/unity_password'
      PASSWORD_TYPE: 'PARAM_STORE'

      VERIFY_SSL: 'TRUE'
      STAC_AUTH_TYPE: 'UNITY'

inputs:
  download_dir:
    type: string
  stac_json:
    type: string
  unity_client_id:
    type: string
  unity_cognito_url:
    type: string
    default: https://cognito-idp.us-west-2.amazonaws.com

outputs:
  download_dir:
    type: Directory
    outputBinding:
      glob: "$(inputs.download_dir)"
