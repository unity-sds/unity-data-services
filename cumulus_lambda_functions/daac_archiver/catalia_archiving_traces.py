import logging

from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlProps
from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
from mdps_ds_lib.lib.aws.no_sql_factory import NoSqlFactory

logger = logging.getLogger(__name__)


class CataliaArchivingTraces:
    identifier = 'identifier'
    s3_url = 's3Url'
    collection = 'collection'
    granule_id = 'granule'
    username = 'username'
    user_group = 'userGroup'
    datetime_str = 'datetime'

    def __init__(self, table_name: str):
        ddb_props = NoSqlProps()
        ddb_props.table = table_name
        ddb_props.primary_key = self.identifier
        # ddb_props.secondary_key = self.datetime_str

        param = ddb_props.to_json()
        param['file_repo'] = 'AWS_DDB'

        self.__ddb: NoSqlDdb = NoSqlFactory().get_instance(**param)

    def get(self, identifier: str):
        results = self.__ddb.get(identifier, secondary_key=None)
        return results

    def add(self, identifier: str, s3_url: str, username: str, user_group: list, collection: str, granule_id: str, datetime_str: str):
        item1 = {
            self.s3_url: s3_url,
            self.collection: collection,
            self.granule_id: granule_id,
            self.username: username,
            self.user_group: user_group,
            self.datetime_str: datetime_str,
        }
        item1 = {k: v for k, v in item1.items() if v is not None}
        self.__ddb.add(identifier, None, item1, replace=False)
        return