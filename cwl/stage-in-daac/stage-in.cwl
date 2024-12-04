cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["DOWNLOAD"]

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/unity-sds/unity-data-services:9.1.0
  EnvVarRequirement:
    envDef:
      DOWNLOAD_DIR: $(runtime.outdir)/$(inputs.download_dir)
      STAC_JSON: $(inputs.stac_json)
      LOG_LEVEL: '10'
      PARALLEL_COUNT: '-1'
      DOWNLOAD_RETRY_WAIT_TIME: '30'
      DOWNLOAD_RETRY_TIMES: '5'
      DOWNLOADING_ROLES: 'data'

      EDL_BASE_URL: 'https://urs.earthdata.nasa.gov/'
      EDL_USERNAME: '/sps/processing/workflows/edl_username'
      EDL_PASSWORD: '/sps/processing/workflows/edl_password'
      EDL_PASSWORD_TYPE: 'PARAM_STORE'

      VERIFY_SSL: 'TRUE'
      STAC_AUTH_TYPE: 'NONE'

inputs:
  download_dir:
    type: string
  stac_json:
    type: string

outputs:
  download_dir:
    type: Directory
    outputBinding:
      glob: "$(inputs.download_dir)"
