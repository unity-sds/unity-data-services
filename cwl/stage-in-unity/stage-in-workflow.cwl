#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: Workflow
label: Workflow that executes the Sounder SIPS end-to-end chirp rebinngin workflow

$namespaces:
  cwltool: http://commonwl.org/cwltool#

requirements:
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  NetworkAccess:
    networkAccess: true

inputs:
  download_dir: string
  stac_json: string
  unity_client_id: string

outputs:
  data:
    type: Directory
    outputSource: stage-in/download_dir

steps:
    stage-in:
      run: "stage-in.cwl"
      in:
        stac_json: stac_json
        download_dir: download_dir
        unity_client_id: unity_client_id
      out: [download_dir]
