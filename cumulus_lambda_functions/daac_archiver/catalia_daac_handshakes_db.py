from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlProps
from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
from mdps_ds_lib.lib.aws.no_sql_factory import NoSqlFactory


class CataliaDaacHandshakesDb:
    user_group = 'userGroup'
    user = 'user'
    source_project = 'sourceProject'
    target_project = 'targetProject'

    def __init__(self, table_name: str):
        ddb_props = NoSqlProps()
        ddb_props.table = table_name
        ddb_props.primary_key = self.source_project
        ddb_props.secondary_key = self.target_project

        param = ddb_props.to_json()
        param['file_repo'] = 'AWS_DDB'

        self.__ddb: NoSqlDdb = NoSqlFactory().get_instance(**param)

    def add(self, catalia_collection, daac_collection, api_key, provider, data_version, sns_topic_arn, role_arn, role_session_name, archiving_types, user, user_group):
        item1 = {
            self.user_group: user_group,
            self.user: user,
            'provider': provider,
            'data_version': data_version,
            'sns_topic_arn': sns_topic_arn,
            'role_arn': role_arn,
            'role_session_name': role_session_name,
            'archiving_types': archiving_types,
            'api_key': api_key,
        }
        self.__ddb.add(catalia_collection, daac_collection, item1, replace=True)
        return

    def search(self, catalia_collection):
        results = self.__ddb.get(catalia_collection, secondary_key=None)
        return results
