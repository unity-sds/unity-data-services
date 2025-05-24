# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [9.12.0] - 2025-05-24
### Changed
- [#585](https://github.com/unity-sds/unity-data-services/pull/585) feat: add ram size in lambdas

## [9.11.9] - 2025-05-23
### Fixed
- [#582](https://github.com/unity-sds/unity-data-services/pull/582) fix: use correct schema

## [9.11.8] - 2025-05-21
### Fixed
- [#580](https://github.com/unity-sds/unity-data-services/pull/580) fix: update-archival-index-mapping

## [9.11.7] - 2025-05-21
### Fixed
- [#578](https://github.com/unity-sds/unity-data-services/pull/578) fix: sending sns to daac

## [9.11.6] - 2025-05-14
### Fixed
- [#575](https://github.com/unity-sds/unity-data-services/pull/575) fix: lib version bump

## [9.11.5] - 2025-04-24
### Fixed
- [#568](https://github.com/unity-sds/unity-data-services/pull/568) fix: case insensitive

## [9.11.4] - 2025-04-23
### Fixed
- [#569](https://github.com/unity-sds/unity-data-services/pull/569) fix: healthcheck update

## [9.11.3] - 2025-04-21
### Fixed
- [#565](https://github.com/unity-sds/unity-data-services/pull/565) fix: data service version endpoint

## [9.11.2] - 2025-04-15
### Fixed
- [#564](https://github.com/unity-sds/unity-data-services/pull/564) fix: check collection when querying single granule

## [9.11.1] - 2025-04-10
### Fixed
- [#561](https://github.com/unity-sds/unity-data-services/pull/561) fix: docker error

## [9.11.0] - 2025-04-09
### Changed
- [#556](https://github.com/unity-sds/unity-data-services/pull/556) feat: bump uds-lib version

## [9.10.1] - 2025-04-09
### Fixed
- [#554](https://github.com/unity-sds/unity-data-services/pull/554) fix: configurable dapa url

## [9.10.0] - 2025-03-25
### Changed
- [#547](https://github.com/unity-sds/unity-data-services/pull/547) feat: stac browser from terraform

## [9.9.0] - 2025-03-11
### Changed
- [#536](https://github.com/unity-sds/unity-data-services/pull/536) feat: push image to ecr

## [9.8.1] - 2025-02-19
### Fixed
- [#535](https://github.com/unity-sds/unity-data-services/pull/535) fix: sorting key order was not kept previously

## [9.8.0] - 2025-02-10
### Changed
- [#532](https://github.com/unity-sds/unity-data-services/pull/532) feat: granules sort by time or other properties

## [9.7.0] - 2025-02-10
### Changed
- [#521](https://github.com/unity-sds/unity-data-services/pull/521) feat: gemx branch

## [9.6.0] - 2025-02-03
### Changed
- [#517](https://github.com/unity-sds/unity-data-services/pull/517) feat: stac browser oidc cookie

## [9.5.2] - 2025-01-31
### Fixed
- [#524](https://github.com/unity-sds/unity-data-services/pull/524) fix: default boto3 from aws already has s3transfer library

## [9.5.1] - 2025-01-17
### Fixed
- [#502](https://github.com/unity-sds/unity-data-services/pull/502) fix: get granules pagination

## [9.5.0] - 2025-01-17
### Changed
- [#499](https://github.com/unity-sds/unity-data-services/pull/499) feat: duplicate granules diff index

## [9.4.2] - 2025-01-17
### Fixed
- [#498](https://github.com/unity-sds/unity-data-services/pull/498) fix: restructure bbox for geoshape

## [9.4.1] - 2024-12-18
### Fixed
- [#489](https://github.com/unity-sds/unity-data-services/pull/489) fix: delete bug

## [9.4.0] - 2024-12-16
### Changed
- [#485](https://github.com/unity-sds/unity-data-services/pull/485) feat: delete granule endpoint

## [9.3.0] - 2024-12-11
### Changed
- [#482](https://github.com/unity-sds/unity-data-services/pull/482) feat: updated name spaces and naming of resources

## [9.2.0] - 2024-12-09
### Changed
- [#478](https://github.com/unity-sds/unity-data-services/pull/478) feat: uds lib update

## [9.1.2] - 2024-12-09
### Fixed
- [#448](https://github.com/unity-sds/unity-data-services/pull/448) fix: wrong location archive keys

## [9.1.1] - 2024-12-09
### Fixed
- [#475](https://github.com/unity-sds/unity-data-services/pull/475) fix: index to es is not setting bbox correctly

## [9.1.0] - 2024-12-03
### Changed
- [#472](https://github.com/unity-sds/unity-data-services/pull/472) feat: amalgamation download type

## [9.0.1] - 2024-12-03
### Fixed
- [#459](https://github.com/unity-sds/unity-data-services/pull/459) fix: single catalog multiple collections

## [9.0.0] - 2024-11-04
### Added
- [#457](https://github.com/unity-sds/unity-data-services/pull/457) breaking change : update uds lib

## [8.1.2] - 2024-10-30
### Fixed
- [#455](https://github.com/unity-sds/unity-data-services/pull/455) fix: updated marketplace bucket policy to require ssl

## [8.1.1] - 2024-10-16
### Fixed
- [#449](https://github.com/unity-sds/unity-data-services/pull/449) fix: use dlq to avoid sqs bottleneck + ignore both none & empty array in validation

## [8.1.0] - 2024-10-10
### Changed
- [#438](https://github.com/unity-sds/unity-data-services/pull/438) feat: import uds lib for core logic

## [8.0.0] - 2024-09-09
### Added
- [#415](https://github.com/unity-sds/unity-data-services/pull/415) breaking change : auxiliary files stage out

## [7.14.0] - 2024-09-09
### Changed
- [#419](https://github.com/unity-sds/unity-data-services/pull/419) feat: trying to get docs page working

## [7.13.1] - 2024-08-13
### Fixed
- [#411](https://github.com/unity-sds/unity-data-services/pull/411) fix: check by id first to see if the granule exists before updating it

## [7.13.0] - 2024-08-12
### Changed
- [#402](https://github.com/unity-sds/unity-data-services/pull/402) feat: daac sender + receiver logic

## [7.12.2] - 2024-08-06
### Fixed
- [#407](https://github.com/unity-sds/unity-data-services/pull/407) fix: download from http with stream enabled

## [7.12.1] - 2024-07-23
### Fixed
- [#399](https://github.com/unity-sds/unity-data-services/pull/399) fix: replace health check ssm

## [7.12.0] - 2024-07-23
### Changed
- [#398](https://github.com/unity-sds/unity-data-services/pull/398) feat: add mock daac lambda logic

## [7.11.0] - 2024-07-22
### Changed
- [#396](https://github.com/unity-sds/unity-data-services/pull/396) feat: adding daac archive config

## [7.10.1] - 2024-07-10
### Fixed
- [#393](https://github.com/unity-sds/unity-data-services/pull/393) fix: less than 200 is ok. not error

## [7.10.0] - 2024-07-09
### Changed
- [#390](https://github.com/unity-sds/unity-data-services/pull/390) feat: add additional role to s3 bucket policy

## [7.9.0] - 2024-07-01
### Changed
- [#385](https://github.com/unity-sds/unity-data-services/pull/385) feat: different web service for stac browser

## [7.8.1] - 2024-06-27
### Fixed
- [#373](https://github.com/unity-sds/unity-data-services/pull/373) fix: updating path for httpd testing

## [7.8.0] - 2024-06-27
### Changed
- [#372](https://github.com/unity-sds/unity-data-services/pull/372) feat: market place bucket

## [7.7.0] - 2024-05-13
### Changed
- [#369](https://github.com/unity-sds/unity-data-services/pull/369) feat: add cnm response archival lambda

## [7.6.0] - 2024-05-13
### Changed
- [#368](https://github.com/unity-sds/unity-data-services/pull/368) feat: adding automated ingestion lambda

## [7.5.0] - 2024-04-24
### Changed
- [#365](https://github.com/unity-sds/unity-data-services/pull/365) feat: add granuile cnm ingester tf

## [7.4.0] - 2024-04-15
### Changed
- [#361](https://github.com/unity-sds/unity-data-services/pull/361) feat: uploading successful feature collection to s3

## [7.3.0] - 2024-04-15
### Changed
- [#362](https://github.com/unity-sds/unity-data-services/pull/362) feat: add health check ssm

# [Unity Release 24.1] - 2024-04-09

### Repository Tags
- [unity-data-services](https://github.com/unity-sds/unity-data-services/) : [7.2.1](https://github.com/unity-sds/unity-data-services/releases/tag/v7.2.1)

### Added
- [#254](https://github.com/unity-sds/unity-data-services/pull/254) breaking: allow custom-metadata in granules dapa query
- [#333](https://github.com/unity-sds/unity-data-services/pull/333) breaking: catalog & collection endpoint + items link
### Changed
- [#295](https://github.com/unity-sds/unity-data-services/pull/295) feat: download granule json is public url
- [#297](https://github.com/unity-sds/unity-data-services/pull/297) feat: granule stac asset with "roles" logic
- [#303](https://github.com/unity-sds/unity-data-services/pull/303) feat: find stac metadata file
- [#312](https://github.com/unity-sds/unity-data-services/pull/312) feat: stage in step to use dapa url to get the queries.
- [#339](https://github.com/unity-sds/unity-data-services/pull/339) feat: testing stac browser ui
- [#344](https://github.com/unity-sds/unity-data-services/pull/344) feat: update stac catalog list
### Fixed
- [#316](https://github.com/unity-sds/unity-data-services/pull/316) fix: granules cnm bug fixes
- [#320](https://github.com/unity-sds/unity-data-services/pull/320) fix: stage out result file in a different directory
- [#325](https://github.com/unity-sds/unity-data-services/pull/325) fix: replace anything not alphanumeric to 3 underscores
- [#335](https://github.com/unity-sds/unity-data-services/pull/335) fix: split into different catalog base url
- [#337](https://github.com/unity-sds/unity-data-services/pull/337) fix: add cors to fast api
- [#342](https://github.com/unity-sds/unity-data-services/pull/342) fix: no filename in main data.stac.json file
- [#347](https://github.com/unity-sds/unity-data-services/pull/347) fix: downgrade pystac to 1.9

## [7.2.1] - 2024-04-08
### Fixed
- [#347](https://github.com/unity-sds/unity-data-services/pull/347) fix: downgrade pystac to 1.9

## [7.2.0] - 2024-04-03
### Changed
- [#344](https://github.com/unity-sds/unity-data-services/pull/344) feat: update stac catalog list

## [7.1.1] - 2024-04-02
### Fixed
- [#342](https://github.com/unity-sds/unity-data-services/pull/342) fix: no filename in main data.stac.json file

## [7.1.0] - 2024-03-28
### Changed
- [#339](https://github.com/unity-sds/unity-data-services/pull/339) feat: testing stac browser ui

## [7.0.2] - 2024-03-11
### Fixed
- [#337](https://github.com/unity-sds/unity-data-services/pull/337) fix: add cors to fast api

## [7.0.1] - 2024-03-01
### Fixed
- [#335](https://github.com/unity-sds/unity-data-services/pull/335) fix: split into different catalog base url

## [7.0.0] - 2024-02-29
### Added
- [#333](https://github.com/unity-sds/unity-data-services/pull/333) breaking: catalog & collection endpoint + items link

## [6.4.3] - 2024-02-06
### Fixed
- [#325](https://github.com/unity-sds/unity-data-services/pull/325) fix: replace anything not alphanumeric to 3 underscores

## [6.4.2] - 2024-02-05
### Fixed
- [#320](https://github.com/unity-sds/unity-data-services/pull/320) fix: stage out result file in a different directory

## [6.4.1] - 2024-02-01
### Fixed
- [#316](https://github.com/unity-sds/unity-data-services/pull/316) fix: granules cnm bug fixes

## [6.4.0] - 2024-02-01
### Changed
- [#312](https://github.com/unity-sds/unity-data-services/pull/312) feat: stage in step to use dapa url to get the queries.

## [6.3.0] - 2024-01-29
### Changed
- [#303](https://github.com/unity-sds/unity-data-services/pull/303) feat: find stac metadata file

## [6.2.0] - 2024-01-25
### Changed
- [#297](https://github.com/unity-sds/unity-data-services/pull/297) feat: granule stac asset with "roles" logic

## [6.1.0] - 2024-01-23
### Changed
- [#295](https://github.com/unity-sds/unity-data-services/pull/295) feat: download granule json is public url

## [6.0.0] - 2024-01-10
### Added
- [#254](https://github.com/unity-sds/unity-data-services/pull/254) breaking: allow custom-metadata in granules dapa query

## [5.7.2] - 2024-01-04
### Fixed
- [#282](https://github.com/unity-sds/unity-data-services/pull/282) fix: no double version update pr - tested

## [5.7.1] - 2024-01-04
### Fixed
- [#263](https://github.com/unity-sds/unity-data-services/pull/263) fix: metadata stac generate cmr  file postfix

## [5.7.0] - 2024-01-04
### Changed
- [#264](https://github.com/unity-sds/unity-data-services/pull/264) feat: collection validation in catalog

## [5.6.1] - 2024-01-03
### Fixed
- [#270](https://github.com/unity-sds/unity-data-services/pull/270) fix: pr creationg to update version failed

## [5.6.0] - 2023-10-31
### Fixed
- [#253](https://github.com/unity-sds/unity-data-services/pull/253) fix: Stage out succeeded when there is an error

## [5.5.5] - 2023-10-09
### Fixed
- [#252](https://github.com/unity-sds/unity-data-services/pull/252) fix: version update + changelog via pr

## [5.5.4] - 2023-10-03
### Fixed
- [#249](https://github.com/unity-sds/unity-data-services/pull/249) chore: update version + change log

## [5.5.3] - 2023-10-03
### Fixed
- [#248](https://github.com/unity-sds/unity-data-services/pull/248) fix: github action write protected branch 15

## [5.5.2] - 2023-10-02
### Fixed
- [#233](https://github.com/unity-sds/unity-data-services/pull/233) fix: github action write protected branch 7

## [5.5.1] - 2023-09-21
### Changed
- [#207](https://github.com/unity-sds/unity-data-services/pull/207) feat: upper limit = 50 for collections

## [5.5.0] - 2023-09-28
### Added
- [#201](https://github.com/unity-sds/unity-data-services/pull/201) feat: Custom metadata mechanism

## [5.4.0] - 2023-08-16
### Added
- [#95](https://github.com/unity-sds/unity-data-services/pull/95) feat: elasticsearch branch

## [5.3.3] - 2023-09-18
### Changed
- [#204](https://github.com/unity-sds/unity-data-services/pull/204) chore: clean.up - remove old codes

## [5.3.2] - 2023-08-28
### Changed
- [#200](https://github.com/unity-sds/unity-data-services/pull/200) fix: parallelize upload

## [5.3.1] - 2023-08-16
### Changed
- [#194](https://github.com/unity-sds/unity-data-services/pull/194) fix: Cataloging large number asynchronously by batch + download is stuck when there are large number of files

## [5.3.0] - 2023-08-07
### Changed
- [#190](https://github.com/unity-sds/unity-data-services/pull/190) feat: Using Fastapi for all API endpoints

## [5.2.3] - 2023-08-07
### Changed
- [#193](https://github.com/unity-sds/unity-data-services/pull/193) fix: add collection folder in s3 upload

## [5.2.2] - 2023-07-21
### Changed
- [#188](https://github.com/unity-sds/unity-data-services/pull/188) fix: Update stage out task to read STAC items from STAC catalog


# [Unity Release 23.2] - 2023-07-20

### Repository Tags
- [unity-data-services](https://github.com/unity-sds/unity-data-services/) : [5.2.1](https://github.com/unity-sds/unity-data-services/releases/tag/v5.2.1)

### Added
- [#119](https://github.com/unity-sds/unity-data-services/issues/119) Update data download task to allow staging data from DAAC HTTPS to local work directory
- [#123](https://github.com/unity-sds/unity-data-services/issues/123) Update metadata reader to parse metadata from CHIRP xml files
- [#157](https://github.com/unity-sds/unity-data-services/issues/157) Update stage-in to support HTTP/HTTPS download that doesn't require EDL
- [#170](https://github.com/unity-sds/unity-data-services/issues/170) Parallelize data download in stage in task
### Changed
- [#125](https://github.com/unity-sds/unity-data-services/issues/125) Update metadata parser/transformer names to reflect metadata format instead of data processing level
- [#128](https://github.com/unity-sds/unity-data-services/issues/128) UDS search docker image to perform CMR search + pagination 
- [#129](https://github.com/unity-sds/unity-data-services/issues/129) UDS search docker image to perform UDS search + pagination
- [#130](https://github.com/unity-sds/unity-data-services/issues/130) Update stage out (upload data to S3) to read catalog.json 
- [#133](https://github.com/unity-sds/unity-data-services/issues/133) Update stage in task to take as input STAC input file
- [#141](https://github.com/unity-sds/unity-data-services/issues/141) Update stage in to modify input STAC JSON to point to local urls
- [#147](https://github.com/unity-sds/unity-data-services/issues/147) UDS tasks to support optional output file parameter
- [#151](https://github.com/unity-sds/unity-data-services/issues/151) Update catalog task to take stac input file
- [#155](https://github.com/unity-sds/unity-data-services/issues/155) Update UDS catalog task to wait for granules to be registered 
- [#158](https://github.com/unity-sds/unity-data-services/issues/158) Update stage in task to use relative path for href in STAC 
- [#159](https://github.com/unity-sds/unity-data-services/issues/159) Update stage out task to not require integration with UDS DAPA
- [#160](https://github.com/unity-sds/unity-data-services/issues/160) Update stage in to require FeatureCollection STAC as input and only download specific assets
### Fixed
- [#167](https://github.com/unity-sds/unity-data-services/issues/167) Add retry logic for temporary failure in name resolution in Earth Data Login
- [#181](https://github.com/unity-sds/unity-data-services/issues/181) Update stage in task to auto retry upon 502 errors

## [5.2.1] - 2023-07-10
### Added
- [#182](https://github.com/unity-sds/unity-data-services/pull/182) fix: Retry if Download Error in DAAC

## [5.2.0] - 2023-07-05
### Added
- [#169](https://github.com/unity-sds/unity-data-services/pull/169) feat: parallelize download

## [5.1.0] - 2023-06-08
### Added
- [#156](https://github.com/unity-sds/unity-data-services/pull/156) feat: added filter keyword in granules endpoint + repeatedly checking with time boundary for cataloging result

## [5.0.1] - 2023-06-21
### Added
- [#165](https://github.com/unity-sds/unity-data-services/pull/165) fix: convert all outputs into json str

## [5.0.0] - 2023-06-13
### Added
- [#163](https://github.com/unity-sds/unity-data-services/pull/163) breaking: new upload implementation for complete catalog (no connection to DAPA)

## [4.0.0] - 2023-06-13
### Changed
- [#161](https://github.com/unity-sds/unity-data-services/pull/161) breaking: search to return feature-collection. download to read feature-collection + return localized feature-collection w/ relative paths

## [3.8.2] - 2023-05-23
### Added
- [#154](https://github.com/unity-sds/unity-data-services/pull/154) fix: production datetime not in +00:00 format

## [3.8.1] - 2023-05-22
### Added
- [#152](https://github.com/unity-sds/unity-data-services/pull/152) fix: allow catalog stage input from file

## [3.8.0] - 2023-05-04
### Added
- [#149](https://github.com/unity-sds/unity-data-services/pull/149) feat: writing output content to a file if ENV is provided

## [3.7.1] - 2023-05-04
### Changed
- [#148](https://github.com/unity-sds/unity-data-services/pull/148) fix: use cas structure to generate metadata for stac

## [3.7.0] - 2023-04-25
### Added
- [#146](https://github.com/unity-sds/unity-data-services/pull/146) feat: Stac metadata extraction 

## [3.6.1] - 2023-04-24
### Changed
- [#144](https://github.com/unity-sds/unity-data-services/pull/144) fix: downloaded stac to return local absolute path

## [3.6.0] - 2023-04-24
### Added
- [#142](https://github.com/unity-sds/unity-data-services/pull/142) feat: Support DAAC download files stac file, not just direct json text

## [3.5.0] - 2023-04-18
### Added
- [#138](https://github.com/unity-sds/unity-data-services/pull/138) feat: Checkout stage with STAC catalog json

## [3.4.0] - 2023-04-17
### Added
- [#132](https://github.com/unity-sds/unity-data-services/pull/132) feat: add DAAC download logic

## [3.3.1] - 2023-04-13
### Changed
- [#136](https://github.com/unity-sds/unity-data-services/pull/136) fix: uncomment temporal in CMR granules search

## [3.3.0] - 2023-04-11
### Added
- [#134](https://github.com/unity-sds/unity-data-services/pull/134) feat: add option to parse downloading stac from file

## [3.2.0] - 2023-04-11
### Added
- [#131](https://github.com/unity-sds/unity-data-services/pull/131) granules query pagination 

## [3.1.0] - 2023-04-11
### Added
- [#126](https://github.com/unity-sds/unity-data-services/pull/126) reduce pystac length by keeping only data asset

## [3.0.0] - 2023-03-27
### Breaking
- [#124](https://github.com/unity-sds/unity-data-services/pull/124) configurable file postfixes for PDS metadata extraction + rename function names which will break previous terraforms

## [2.0.0] - 2023-01-23
### Breaking
- [#120](https://github.com/unity-sds/unity-data-services/pull/120) breakup upload and download dockers into search + download & upload + catalog

## [1.10.1] - 2023-01-23
### Fixed
- [#112](https://github.com/unity-sds/unity-data-services/pull/112) update dockerfile base images

## [1.10.0] - 2022-12-19
### Added
- [#104](https://github.com/unity-sds/unity-data-services/pull/104) added Updated time in collection & item STAC dictionaries
### Changed
- [#104](https://github.com/unity-sds/unity-data-services/pull/104) use pystac library objects to create collection and item STAC dictionaries

## [1.9.3] - 2022-12-19
### Added
- [#103](https://github.com/unity-sds/unity-data-services/pull/103) return a dictionary including HREFs instead of a string REGISTERED
## [1.9.2] - 2022-11-16
### Fixed
- [#100](https://github.com/unity-sds/unity-data-services/pull/100) status=completed is only for granules, not for collections
## [1.9.1] - 2022-11-15
### Added
- [#94](https://github.com/unity-sds/unity-data-services/issues/94) Added DAPA lambdas function name to parameter store for UCS API Gateway integration
### Fixed
- [#98](https://github.com/unity-sds/unity-data-services/issues/98) accept provider from ENV or optionally from user call

## [1.8.1] - 2022-09-27
### Added
- [#79](https://github.com/unity-sds/unity-data-services/pull/79) Collection Creation endpoint with DAPA format
### Changed
- [#80](https://github.com/unity-sds/unity-data-services/pull/80) level.1.a.missing.filename
- [#82](https://github.com/unity-sds/unity-data-services/pull/82) not honoring offset and limit in Collection query
- [#89](https://github.com/unity-sds/unity-data-services/pull/89) check pathParameters is None
### Fixed


## [1.7.0] - 2022-09-06
### Added
- [#62](https://github.com/unity-sds/unity-data-services/issues/66) Added OpenAPI spec for DAPA endpoints
- [#66](https://github.com/unity-sds/unity-data-services/issues/66) Added pagination links to STAC response of DAPA endpoints
- [#64](https://github.com/unity-sds/unity-data-services/issues/64) Added temporal coverage to DAPA collection endpoint
### Changed
- [#67](https://github.com/unity-sds/unity-data-services/issues/67) Updated STAC collection schema to be compatible with PySTAC library
### Fixed

## [1.6.17] - 2022-07-28
### Added
### Fixed
- l1A granule id is `<collection-id>___<collection-version>:<granule-id>` not to duplicate re-runs

## [1.6.16] - 2022-07-25
### Added
- Added: use username & password to login to cognito to get the token 
### Fixed

## [0.1.0] - 2022-04-14
### Added
- Added lambda for parsing metadata from Sounder SIPS L0 metadata files [#14](https://github.com/unity-sds/unity-data-services/issues/14)
### Fixed
- Pushed docker image to ghcr.io