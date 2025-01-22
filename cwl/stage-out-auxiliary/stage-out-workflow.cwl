#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
label: Workflow that executes the Sounder SIPS end-to-end chirp rebinngin workflow

$namespaces:
  cwltool: http://commonwl.org/cwltool#

requirements:
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  collection_id: string
  staging_bucket: string
  sample_output_data: Directory

outputs:
  successful_features:
    type: File
    outputSource: stage-out/successful_features
  failed_features:
    type: File
    outputSource: stage-out/failed_features

steps:
    stage-out:
      run: "stage-out.cwl"
      in:
        collection_id: collection_id
        staging_bucket: staging_bucket
        sample_output_data: sample_output_data
      out: [successful_features, failed_features]
