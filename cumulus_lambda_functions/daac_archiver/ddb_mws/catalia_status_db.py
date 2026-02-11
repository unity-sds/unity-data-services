from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlProps
from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
from mdps_ds_lib.lib.aws.no_sql_factory import NoSqlFactory


class CataliaStatusDb:
    identifier = 'identifier'
    collection = 'collection'
    name_str = 'name'
    status = 'status'
    error_code = 'errorCode'
    error_message = 'errorMessage'
    href_str = 'href'
    datetime_str = 'datetime'

    def __init__(self, table_name: str):
        ddb_props = NoSqlProps()
        ddb_props.table = table_name
        ddb_props.primary_key = self.identifier
        ddb_props.secondary_key = self.datetime_str

        param = ddb_props.to_json()
        param['file_repo'] = 'AWS_DDB'

        self.__ddb: NoSqlDdb = NoSqlFactory().get_instance(**param)

    def get(self, identifier: str):
        results = self.__ddb.get(identifier, secondary_key=None)
        return results

    def add(self, identifier: str, collection: dict, name_str: str, status: str, datetime_str: str, error_code: str=None, error_message: str=None, href_str: str=None):
        item1 = {
            self.name_str: name_str,
            self.collection: collection,
            self.status: status,
            self.error_code: error_code,
            self.error_message: error_message,
            self.href_str: href_str,
        }
        item1 = {k: v for k, v in item1.items() if v is not None}
        self.__ddb.add(identifier, datetime_str, item1, replace=False)
        return
