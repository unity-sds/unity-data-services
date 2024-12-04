cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["UPLOAD"]

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/unity-sds/unity-data-services:9.1.0
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.sample_output_data)
      entryname: /tmp/outputs

  EnvVarRequirement:
    envDef:
      STAGING_BUCKET: $(inputs.staging_bucket)
      CATALOG_FILE: '/tmp/outputs/catalog.json'
      LOG_LEVEL: '10'
      PARALLEL_COUNT: '-1'
      OUTPUT_DIRECTORY: $(runtime.outdir)
      PROJECT: $(inputs.project)
      VENUE: $(inputs.venue)

      GRANULES_UPLOAD_TYPE: 'UPLOAD_S3_BY_STAC_CATALOG'
      BASE_DIRECTORY: '/tmp/outputs'

inputs:
  project:
    type: string
  venue:
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

