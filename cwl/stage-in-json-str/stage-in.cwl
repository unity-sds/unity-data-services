cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["DOWNLOAD"]

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/unity-sds/unity-data-services:9.4.0
  NetworkAccess:
    networkAccess: true
  EnvVarRequirement:
    envDef:
      DOWNLOAD_DIR: $(runtime.outdir)/$(inputs.download_dir)
      STAC_JSON: $(inputs.stac_json)

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
