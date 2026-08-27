# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unity Data Services ("Catalia UDS") is a NASA Unity/Cumulus-adjacent Python service. It provides AWS Lambda functions and a FastAPI web service for data ingest, cataloging, search, and access, complying with OGC DAPA and STAC specifications, plus a subsystem ("Catalia") for archiving granules out to external DAACs (Distributed Active Archive Centers) via CNM (Cloud Notification Message).

Python version is pinned to **3.10** (see `setup.py`).

## Common Commands

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run all tests (there is no pytest.ini/tox.ini/setup.cfg — tests are plain
# unittest.TestCase classes discovered under tests/, mirroring the
# cumulus_lambda_functions/ package structure 1:1)
python -m pytest tests/cumulus_lambda_functions

# Run a single test file / test case / test method
python -m pytest tests/cumulus_lambda_functions/lib/test_cql_parser.py
python -m pytest tests/cumulus_lambda_functions/lib/test_cql_parser.py::TestCqlParser::test_01

# Run the FastAPI web service locally (loads .env via python-dotenv)
python -m cumulus_lambda_functions.catalya_uds_api.web_service
# or, with auto-reload:
uvicorn cumulus_lambda_functions.catalya_uds_api.web_service:app --port 8005 --reload

# Run the stage-in/stage-out Docker CLI entrypoint locally
python -m cumulus_lambda_functions.docker_entrypoint <SEARCH|DOWNLOAD|UPLOAD|CATALOG|CATALYA_COLLECTION_ARCHIVE>
```

There is no lint command configured in CI. CI (`.github/workflows/makefile.yml`) does **not** run tests — it only installs deps, strips `boto3`/`botocore`/`s3transfer` (provided by the Lambda runtime), and packages Lambda deployment zips via `ci.cd/create_aws_lambda_zip.sh`. Testing is manual/local via pytest.

`tests/integration_tests/` (top-level, separate from `tests/cumulus_lambda_functions/`) contains live end-to-end tests that hit a real deployed stack and require their own `.env` (see `.env.tpl` there); these are not run in CI.

## Architecture

### Layering: `mdps_ds_lib` vs `cumulus_lambda_functions`

This repo is the **application layer**. Nearly all low-level AWS/data plumbing (boto3 S3/SNS/SQS/DynamoDB/Lambda/Parameter Store clients, stage-in/out granule search/download/upload/catalog logic, shared `Constants`, JSON/time/file utils) lives in the external pip dependency **`mdps_ds_lib`** (`mdps-ds-lib` on PyPI). Code in `cumulus_lambda_functions/` builds on top of it — e.g. `daac_archiver/ddb_mws/*.py` wraps `mdps_ds_lib.lib.aws.no_sql_ddb.NoSqlDdb` with table-specific access patterns; `docker_entrypoint/__main__.py` just dispatches to `mdps_ds_lib.stage_in_out.*Factory` classes. When behavior seems missing from this repo, check whether it's implemented in `mdps_ds_lib` instead.

### Module map (`cumulus_lambda_functions/`)

- **`catalya_uds_api/`** — FastAPI app (`web_service.py`) exposing the Catalia REST API, wrapped with `Mangum` as the Lambda handler. Routers: `auth_admin_api.py` (user-group ↔ source/target collection authorization admin CRUD), `granules_archive_api.py` (trigger/track granule archiving to a DAAC), `daac_archive_config_api.py` (DAAC archive config CRUD). `granules_archive_api.py`'s archive route asynchronously re-invokes another Lambda (via `mdps_ds_lib`'s `AwsLambda`) to dodge API Gateway timeouts, unless `IS_API_IN_DOCKER=TRUE`, in which case it runs inline.
- **`catalya_archive_trigger/`** — Lambda (`lambda_function.py`) that validates HYSDS metadata, resolves relative S3 URLs, and kicks off DAAC archiving.
- **`daac_archiver/`** — Core DAAC-archiving business logic:
  - `daac_archiver_catalia_2.py` — main archiver.
  - `daac_receiver.py` — SQS/SNS CNM status-callback handler, validates against PODAAC's `cumulus_sns_schema.json`.
  - `cnm_plugins/` — pluggable post-processing on CNM status via a factory (status updates, storage, etc.).
  - `raw_cnm_storage/` — S3-backed storage of raw CNM messages.
  - `services/` — MAAP API client, SFA client middleware, staging service, status update service.
  - `ddb_mws/` — DynamoDB access classes (auth, status, DAAC handshake config, archiving traces). `catalia_auth_db.py` resolves user-group → source/target collection auth using regex + longest-common-prefix matching.
  - `sql_mws/` — a **parallel SQLAlchemy/Postgres re-implementation** of the status table (`catalia_status_db.py`, SQLAlchemy Core, not ORM) with the same public API as its DDB counterpart, intended as a drop-in swap for analytics/ad-hoc queries that are hard to do against DynamoDB. Connects to an Aurora Postgres instance (see `tf-module/daac_delivery_analysis`) via AWS Parameter Store JSON (`URL/PORT/USERNAME/PASSWORD/DBNAME`).
- (Deprecated, DO NOT USE) **`docker_entrypoint/`** — `__main__.py`, the CLI for the standalone stage-in/stage-out Docker image; dispatches on `argv[1]` to `mdps_ds_lib` factories.
- **`keycloak_authorizer/`** — a placeholder API Gateway TOKEN authorizer that currently allows all requests (real Keycloak integration is pending).
- **`lib/`** — shared internal helpers: `uds_fast_api/` (CORS config, API Gateway/Mangum auth-header extraction, STAC browser static assets), `uds_db/` (DynamoDB-backed collection/archive-index models), `authorization/` (pluggable authorizer abstraction + factory, ES-identity-pool impl), `metadata_extraction/` (ECHO metadata parsing), `lambda_logger_generator.py` (standardized Lambda logger setup, used by every handler to strip default log handlers).
- **`mock_daac/`** — a Lambda simulating a DAAC's CNM response, for local/integration testing of the archiving pipeline.

There is no dedicated `models/` directory — DynamoDB/SQL table schemas are defined inline within each `*_db.py` file in `ddb_mws/`, `sql_mws/`, and `uds_db/`.

### Entry point patterns

- **FastAPI + Mangum**: `catalya_uds_api/web_service.py` exposes `handler = Mangum(app=app)` for Lambda, and runs via `uvicorn` locally under `if __name__ == '__main__'`.
- **Plain Lambda handlers**: `def lambda_handler(event, context)` (or `lambda_handler_response` in `daac_archiver`) in each `lambda_function.py`, generally triggered by SQS/SNS wrapping S3 event notifications. Each strips default log handlers via `LambdaLoggerGenerator.remove_default_handlers()` before delegating to a logic class.
- (Deprecated, DO NOT USE) **Docker CLI**: `docker_entrypoint/__main__.py`, invoked as `python -m cumulus_lambda_functions.docker_entrypoint <VERB>`, backing the images built from `docker/Dockerfile_download_granules.public` / `.jpl` and the sample compose files under `docker/stage-in-stage-out/`.

### Config / environment

`python-dotenv`'s `load_dotenv()` is called once at the top of `catalya_uds_api/web_service.py` before other imports; after that, config is read via `os.environ`/`os.getenv`, often referencing shared key names from `mdps_ds_lib.lib.constants.Constants` or the locally defined `WebServiceConstants`. Lambda handlers rely on the Lambda runtime's own env vars (no `load_dotenv()` call there). `.env` at repo root is a real local-dev config file (git-tracked historically; do not put new secrets in it) — see it for the expected variable names (`ES_URL`, `SNS_TOPIC_ARN`, `DAPA_API_URL_BASE`, etc.).

### Infra (`docker/`, `tf-module/`)

- `docker/` — `Dockerfile.public`/`.jpl` (main service image, public vs JPL-internal registry), `Dockerfile_download_granules.public`/`.jpl` (stage-in/out image), `docker-compose-web-service*.yml` / `docker-compose-dapa.yml` for running the FastAPI service locally, `docker/stage-in-stage-out/` sample compose files per CLI verb (`dc-001-search`, `dc-002-download`, `dc-003-upload[_auxiliary]`, `dc-004-catalog`).
- `tf-module/` — deployment order per `Deploying-Catalia-UDS.md`: `unity_vpc` → `uds_catalia_iam` → (optional) `uds_catalia_bucket` → (optional) `daac_delivery_analysis` (Aurora Postgres v2) → `uds_catalia` (Lambda + API Gateway + SNS/SQS, the main Catalia deployment). Other modules: `unity-cumulus` (broader Cumulus lambda infra), `marketplace`, `ds_img_to_ecr[_back]`, `stac_browser`, `mock_daac`, `sqs--sns-lambda-connector`.

### Onboarding a new DAAC partner

See `handshake-daac.md`: grant auth via the admin API, collect the DAAC's SNS topic ARN/role ARN/data version/API key, configure via the archive-config API, update the target S3 bucket policy for the DAAC's IAM role, and update `DAAC_LAMBDA_2_SNS_ROLE` in terraform so SNS accepts inbound CNM messages from that DAAC.

### Other reference docs

- `Deploying-Catalia-UDS.md` — full deployment runbook tying the `tf-module/*` modules together in order, including how to fetch the released Lambda zip artifact.
