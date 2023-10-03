# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.5.3] - 2023-10-03
### Fixed
- [#242](https://github.com/unity-sds/unity-data-services/pull/242) fix: github action write protected branch 11

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