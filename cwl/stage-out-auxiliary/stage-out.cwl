cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["UPLOAD"]

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/unity-sds/unity-data-services:9.4.0
  NetworkAccess:
    networkAccess: true
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.sample_output_data)
      entryname: /tmp/outputs

  EnvVarRequirement:
    envDef:
      COLLECTION_ID: $(inputs.collection_id)
      STAGING_BUCKET: $(inputs.staging_bucket)
      LOG_LEVEL: '10'
      PARALLEL_COUNT: '-1'
      OUTPUT_DIRECTORY: $(runtime.outdir)
      RESULT_PATH_PREFIX: 'stage_out/$(inputs.collection_id)'
      GRANULES_UPLOAD_TYPE: 'UPLOAD_AUXILIARY_FILE_AS_GRANULE'
      BASE_DIRECTORY: '/tmp/outputs'

inputs:
  collection_id:
    type: string
  staging_bucket:
    type: string
  sample_output_data:
    type: Directory

outputs:
  successful_features:
    type: File
    outputBinding:
      glob: "$(runtime.outdir)/successful_features.json"
  failed_features:
    type: File
    outputBinding:
      glob: "$(runtime.outdir)/failed_features.json"

