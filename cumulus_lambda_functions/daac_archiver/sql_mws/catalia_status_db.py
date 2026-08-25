"""
SQL (SQLAlchemy) based re-implementation of
cumulus_lambda_functions/daac_archiver/ddb_mws/catalia_status_db.py

DynamoDB is difficult to run ad-hoc/small analytics queries against, so this module
moves the same "status per archiving identifier" data into a relational table instead.

The public API (class-level column-name constants + `get`/`add` method signatures) is
kept identical to the DynamoDB version so existing callers (daac_receiver.py,
services/status_update_svc.py, catalya_uds_api/granules_archive_api.py) can swap the
import without any other code changes. A `search()` method is added on top for
time-range + collection/target_collection/status filtering to support analytics/report
use cases (funnel counts, success/failure rates, etc.) -- it returns raw matching rows
and leaves any aggregation to the caller.

--------------------------------------------------------------------------------------
Suggested DDL (PostgreSQL dialect) for the table this class reads/writes. Replace
``uds_ctla_daac_status`` below with whatever ``table_name`` is passed into
``CataliaStatusDb()``.

The DynamoDB table used ``identifier`` as its partition/primary key and ``datetime``
as its sort/secondary key. A relational table needs a single-column primary key, so a
surrogate auto-increment ``id`` column is used instead, and the original
``(identifier, datetime)`` pairing is preserved as a UNIQUE constraint -- this keeps
the same "one row per status update, no silent overwrites" behavior that the DynamoDB
version got from `replace=False` + a ConditionExpression.

``datetime`` is stored as epoch-milliseconds (UTC, BIGINT) rather than a formatted
string -- cheap to index/compare and unambiguous across timezones -- instead of the
RFC3339 string used on the DynamoDB side. Values passed into `add()`/`search()` may
still be given as RFC3339 strings (e.g. what `TimeUtils.get_current_time()` produces);
they're converted to epoch-milliseconds internally.

    CREATE TABLE uds_ctla_daac_status (
        id                SERIAL PRIMARY KEY,
        identifier        VARCHAR(255) NOT NULL,
        datetime          BIGINT       NOT NULL,  -- epoch milliseconds, UTC
        collection        VARCHAR(255),
        target_collection VARCHAR(255),
        name              VARCHAR(255),
        status            VARCHAR(64),
        "errorCode"       VARCHAR(255),
        "errorMessage"    VARCHAR(2048),
        href              VARCHAR(2048),
        CONSTRAINT uq_uds_ctla_daac_status_identifier_datetime UNIQUE (identifier, datetime)
    );
    CREATE INDEX ix_uds_ctla_daac_status_identifier        ON uds_ctla_daac_status (identifier);
    CREATE INDEX ix_uds_ctla_daac_status_datetime           ON uds_ctla_daac_status (datetime);
    CREATE INDEX ix_uds_ctla_daac_status_collection         ON uds_ctla_daac_status (collection);
    CREATE INDEX ix_uds_ctla_daac_status_target_collection  ON uds_ctla_daac_status (target_collection);
    CREATE INDEX ix_uds_ctla_daac_status_status             ON uds_ctla_daac_status (status);

Note: `errorCode`/`errorMessage` are quoted above because they're camelCase --
Postgres folds unquoted identifiers to lowercase. The SQLAlchemy `Table` defined in
this module manages that quoting automatically.
--------------------------------------------------------------------------------------
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Union

from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    and_,
    create_engine,
    inspect,
    insert,
    select,
)
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class CataliaStatusDb:
    identifier = 'identifier'
    collection = 'collection'
    target_collection = 'target_collection'
    name_str = 'name'
    status = 'status'
    error_code = 'errorCode'
    error_message = 'errorMessage'
    href_str = 'href'
    datetime_str = 'datetime'

    db_host_key = 'URL'
    db_port_key = 'PORT'
    db_user_key = 'USERNAME'
    db_password_key = 'PASSWORD'
    db_name_key = 'DBNAME'

    def __init__(self, table_name: str, db_config: dict):
        """
        :param table_name: name of the SQL table to read/write, analogous to the DDB table name.
        :param db_config: dict used to build a PostgreSQL connection URL, matching the JSON
            shape stored in the `/${prefix}/daac-delivery-analysis/rds_credentials` SSM
            parameter (see tf-module/daac_delivery_analysis/rds.tf). Must contain all of the
            following keys: `URL`, `PORT`, `USERNAME`, `PASSWORD`, `DBNAME`.
        """
        self.__engine: Engine = create_engine(
            self.__build_db_url(db_config),
            pool_pre_ping=True,
        )
        self.__metadata = MetaData()
        self.__data_columns = [
            self.identifier, self.datetime_str, self.collection, self.target_collection,
            self.name_str, self.status, self.error_code, self.error_message, self.href_str,
        ]
        self.__table = self.__build_table(table_name)

    def __build_db_url(self, db_config: dict) -> URL:
        missing_keys = [k for k in (self.db_host_key, self.db_port_key, self.db_user_key, self.db_password_key, self.db_name_key) if k not in db_config]
        if missing_keys:
            raise ValueError(f'db_config is missing required key(s): {missing_keys}')
        return URL.create(
            drivername='postgresql',
            username=db_config[self.db_user_key],
            password=db_config[self.db_password_key],
            host=db_config[self.db_host_key],
            port=int(db_config[self.db_port_key]),
            database=db_config[self.db_name_key],
        )

    def __build_table(self, table_name: str) -> Table:
        return Table(
            table_name, self.__metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column(self.identifier, String(255), nullable=False, index=True),
            Column(self.datetime_str, BigInteger, nullable=False, index=True),
            Column(self.collection, String(255), index=True),
            Column(self.target_collection, String(255), index=True),
            Column(self.name_str, String(255)),
            Column(self.status, String(64), index=True),
            Column(self.error_code, String(255)),
            Column(self.error_message, String(2048)),
            Column(self.href_str, String(2048)),
            UniqueConstraint(self.identifier, self.datetime_str, name=f'uq_{table_name}_{self.identifier}_{self.datetime_str}'),
        )

    @staticmethod
    def _to_epoch_millis(value: Union[int, float, str]) -> int:
        """
        Accepts either an epoch-millisecond int/float, or an RFC3339 string
        (e.g. "2026-08-20T00:00:00.000000Z", as produced by
        `f'{TimeUtils.get_current_time()}Z'`), and returns the epoch-millisecond
        int representation stored in / queried from the DB. Naive strings (no
        UTC offset) are assumed to already be in UTC.
        """
        if isinstance(value, (int, float)):
            return int(value)
        normalized = value[:-1] + '+00:00' if value.endswith('Z') else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)

    def table_exists(self) -> bool:
        """
        Returns True if the underlying table already exists in the database, False
        otherwise. Useful for callers that want to know/report whether
        create_table_if_missing() is actually about to create something.
        """
        return inspect(self.__engine).has_table(self.__table.name, schema=self.__table.schema)

    def create_table_if_missing(self):
        """
        Creates the underlying table (see DDL in the module docstring) if it doesn't
        already exist. Not called automatically from __init__ so that schema creation
        stays an explicit, deliberate action (e.g. once during deployment, or from
        tests using a throwaway sqlite DB) rather than a side-effect of instantiation.
        """
        self.__metadata.create_all(self.__engine, tables=[self.__table], checkfirst=True)
        return self

    def get(self, identifier: str):
        return self.search(identifier=identifier)

    def search(self, start_datetime: Union[int, float, str] = None, end_datetime: Union[int, float, str] = None,
               collection: str = None, target_collection: str = None, status: str = None, identifier: str = None):
        """
        Returns raw rows matching the given filters, ordered by datetime ascending.
        No aggregation is done here -- callers are expected to compute
        success/failure rates, funnel counts, latency, etc. from the returned rows.

        :param start_datetime: inclusive lower bound (epoch-millis int, or RFC3339 string)
        :param end_datetime: inclusive upper bound (epoch-millis int, or RFC3339 string)
        :param collection: exact-match filter on the source collection
        :param target_collection: exact-match filter on the DAAC target collection
        :param status: exact-match filter on status (e.g. 'cnm-receive-success')
        :param identifier: exact-match filter on the archiving identifier
        """
        columns = [self.__table.c[col_name] for col_name in self.__data_columns]
        conditions = []
        if start_datetime is not None:
            conditions.append(self.__table.c[self.datetime_str] >= self._to_epoch_millis(start_datetime))
        if end_datetime is not None:
            conditions.append(self.__table.c[self.datetime_str] <= self._to_epoch_millis(end_datetime))
        if collection is not None:
            conditions.append(self.__table.c[self.collection] == collection)
        if target_collection is not None:
            conditions.append(self.__table.c[self.target_collection] == target_collection)
        if status is not None:
            conditions.append(self.__table.c[self.status] == status)
        if identifier is not None:
            conditions.append(self.__table.c[self.identifier] == identifier)

        stmt = select(*columns)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(self.__table.c[self.datetime_str])

        with self.__engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
        return [dict(row) for row in rows]

    def add(self, identifier: str, collection: str, name_str: str, status: str, datetime_str: Union[int, float, str], error_code: str=None, error_message: str=None, href_str: str=None, target_collection: str=None):
        item1 = {
            self.identifier: identifier,
            self.datetime_str: self._to_epoch_millis(datetime_str),
            self.name_str: name_str,
            self.collection: collection,
            self.status: status,
            self.error_code: error_code,
            self.error_message: error_message,
            self.href_str: href_str,
            self.target_collection: target_collection,
        }
        item1 = {k: v for k, v in item1.items() if v is not None}
        stmt = insert(self.__table).values(**item1)
        try:
            with self.__engine.begin() as conn:
                conn.execute(stmt)
        except IntegrityError as e:
            logger.warning(f'item already exists for identifier={identifier}, datetime={datetime_str}')
            raise RuntimeError('Item exists. Unable to overwrite') from e
        return
