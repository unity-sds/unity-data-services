import re
from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlProps
from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
from mdps_ds_lib.lib.aws.no_sql_factory import NoSqlFactory


class CataliaAuthDb:
    def __init__(self, table_name: str):
        ddb_props = NoSqlProps()
        ddb_props.table = table_name
        ddb_props.primary_key = 'userGroup'
        ddb_props.secondary_key = 'projectMap'

        param = ddb_props.to_json()
        param['file_repo'] = 'AWS_DDB'

        self.__ddb: NoSqlDdb = NoSqlFactory().get_instance(**param)

    def add(self, user_group, collection, daac_collection, access: bool):
        item1 = {
            'userGroup': user_group,
            'projectMap': '',
            'sourceProject': collection,
            'targetProject': daac_collection,
            'access': access,
        }
        sk1 = f'{item1["sourceProject"]}->{item1["targetProject"]}'
        self.__ddb.add(item1['userGroup'], sk1, item1, replace=True)
        return

    def authorize(self, user_group, catalia_collection, daac_collection):
        """
        This will retrieve entries from DDB with user_group as PK. (This is done).
        If results is None or empty array, return False. Not Authorized.
        For each result, check sourceProject REGEX against catalia_collection input name.
        If results is None or empty array, return False. Not Authorized.
        For each result, check targetProject REGEX against daac_collection input name.
        If results is None or empty array, return False. Not Authorized.
        If only 1 row exists, return its "access" key.
        If two or more rows exist, pick the one closest to the daac_collection in the targetProject name.
        If only 1 row exists, return its "access" key.
        If two or more rows exist, pick the one closest to the catalia_collection in the sourceProject.
        If only 1 row exists, return its "access" key.
        :param user_group:
        :param catalia_collection:
        :param daac_collection:
        :return:
        """
        results = self.__ddb.get(user_group, secondary_key=None)

        if not results or len(results) == 0:
            return False

        source_matches = []
        for result in results:
            source_pattern = result.get('sourceProject', '')
            try:
                if re.match(source_pattern, catalia_collection, re.IGNORECASE):
                    source_matches.append(result)
            except re.error:
                if source_pattern == catalia_collection:
                    source_matches.append(result)

        if not source_matches or len(source_matches) == 0:
            return False

        target_matches = []
        for result in source_matches:
            target_pattern = result.get('targetProject', '')
            try:
                if re.match(target_pattern, daac_collection, re.IGNORECASE):
                    target_matches.append(result)
            except re.error:
                if target_pattern == daac_collection:
                    target_matches.append(result)

        if not target_matches or len(target_matches) == 0:
            return False

        if len(target_matches) == 1:
            return target_matches[0].get('access', False)

        closest_target = min(target_matches, key=lambda x: self._string_distance(x.get('targetProject', ''), daac_collection))

        final_matches = [r for r in target_matches if r.get('targetProject') == closest_target.get('targetProject')]

        if len(final_matches) == 1:
            return final_matches[0].get('access', False)

        closest_source = min(final_matches, key=lambda x: self._string_distance(x.get('sourceProject', ''), catalia_collection))

        return closest_source.get('access', False)

    def _string_distance(self, s1, s2):
        """
        Calculate the negative of the maximum common prefix length (case insensitive).
        Returns negative value so that longer prefixes result in smaller distances for min() selection.
        """
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        common_prefix_length = 0
        for i in range(min(len(s1_lower), len(s2_lower))):
            if s1_lower[i] == s2_lower[i]:
                common_prefix_length += 1
            else:
                break
        return -common_prefix_length
