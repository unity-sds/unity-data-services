"""
SQL (SQLAlchemy) based re-implementation of
cumulus_lambda_functions/daac_archiver/ddb_mws/catalia_status_db.py

DynamoDB is difficult to run ad-hoc/small analytics queries against, so this module
moves the same "status per archiving identifier" data into a relational table instead.

The public API (class-level column-name constants + `get`/`add` method signatures) is
kept identical to the DynamoDB version so existing callers (daac_receiver.py,
services/status_update_svc.py, catalya_uds_api/granules_archive_api.py) can swap the
import without any other code changes.

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

    CREATE TABLE uds_ctla_daac_status (
        id                SERIAL PRIMARY KEY,
        identifier        VARCHAR(255) NOT NULL,
        datetime          VARCHAR(64)  NOT NULL,
        collection        VARCHAR(255),
        target_collection VARCHAR(255),
        name              VARCHAR(255),
        status            VARCHAR(64),
        "errorCode"       VARCHAR(255),
        "errorMessage"    VARCHAR(2048),
        href              VARCHAR(2048),
        CONSTRAINT uq_uds_ctla_daac_status_identifier_datetime UNIQUE (identifier, datetime)
    );
    CREATE INDEX ix_uds_ctla_daac_status_identifier ON uds_ctla_daac_status (identifier);

Note: `errorCode`/`errorMessage` are quoted above because they're camelCase --
Postgres folds unquoted identifiers to lowercase. The SQLAlchemy `Table` defined in
this module manages that quoting automatically.
--------------------------------------------------------------------------------------
"""
import logging
import os
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    insert,
    select,
)
from sqlalchemy.engine import Engine
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

    def __init__(self, table_name: str, db_url: Optional[str] = None):
        """
        :param table_name: name of the SQL table to read/write, analogous to the DDB table name.
        :param db_url: SQLAlchemy connection URL. Falls back to the CATALYA_SQL_DB_URL
            env var, then to a local sqlite file if neither is provided (useful for
            local development/tests without a real database provisioned).
        """
        self.__engine: Engine = create_engine(
            db_url or os.getenv('CATALYA_SQL_DB_URL', 'sqlite:///catalia_status.db'),
            pool_pre_ping=True,
        )
        self.__metadata = MetaData()
        self.__data_columns = [
            self.identifier, self.datetime_str, self.collection, self.target_collection,
            self.name_str, self.status, self.error_code, self.error_message, self.href_str,
        ]
        self.__table = self.__build_table(table_name)

    def __build_table(self, table_name: str) -> Table:
        return Table(
            table_name, self.__metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column(self.identifier, String(255), nullable=False, index=True),
            Column(self.datetime_str, String(64), nullable=False),
            Column(self.collection, String(255)),
            Column(self.target_collection, String(255)),
            Column(self.name_str, String(255)),
            Column(self.status, String(64)),
            Column(self.error_code, String(255)),
            Column(self.error_message, String(2048)),
            Column(self.href_str, String(2048)),
            UniqueConstraint(self.identifier, self.datetime_str, name=f'uq_{table_name}_{self.identifier}_{self.datetime_str}'),
        )

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
        columns = [self.__table.c[col_name] for col_name in self.__data_columns]
        stmt = select(*columns).where(
            self.__table.c[self.identifier] == identifier
        ).order_by(self.__table.c[self.datetime_str])
        with self.__engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
        return [dict(row) for row in rows]

    def add(self, identifier: str, collection: str, name_str: str, status: str, datetime_str: str, error_code: str=None, error_message: str=None, href_str: str=None, target_collection: str=None):
        item1 = {
            self.identifier: identifier,
            self.datetime_str: datetime_str,
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
