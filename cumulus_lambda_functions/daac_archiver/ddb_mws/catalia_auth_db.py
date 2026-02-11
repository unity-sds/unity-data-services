import logging
import re
from collections import defaultdict

from mdps_ds_lib.lib.aws.no_sql_abstract import NoSqlProps
from mdps_ds_lib.lib.aws.no_sql_ddb import NoSqlDdb
from mdps_ds_lib.lib.aws.no_sql_factory import NoSqlFactory
logger = logging.getLogger(__name__)


class CataliaAuthDb:
    user_group = 'userGroup'
    access = 'access'
    project_map = 'projectMap'
    source_project = 'sourceProject'
    target_project = 'targetProject'

    def __init__(self, table_name: str):
        ddb_props = NoSqlProps()
        ddb_props.table = table_name
        ddb_props.primary_key = self.user_group
        ddb_props.secondary_key = self.project_map

        param = ddb_props.to_json()
        param['file_repo'] = 'AWS_DDB'

        self.__ddb: NoSqlDdb = NoSqlFactory().get_instance(**param)

    def add(self, user_group, collection, daac_collection, access: bool):
        item1 = {
            # 'userGroup': user_group,
            # 'projectMap': '',
            self.source_project: collection,
            self.target_project: daac_collection,
            self.access: access,
        }
        sk1 = f'{collection}->{daac_collection}'
        self.__ddb.add(user_group, sk1, item1, replace=True)
        return

    def delete(self, user_group, collection, daac_collection):
        sk1 = f'{collection}->{daac_collection}'
        self.__ddb.delete(user_group, sk1)
        return

    def get_authorized_catalia(self, user_group: list[str], catalia_collection):
        results = []
        for group in user_group:
            group_results = self.__ddb.get(group, secondary_key=None)
            if group_results:
                results.extend(group_results)

        if not results or len(results) == 0:
            return []

        source_matches = []
        for result in results:
            source_pattern = result.get('sourceProject', '')
            try:
                if re.match(source_pattern, catalia_collection, re.IGNORECASE):
                    source_matches.append(result)
            except re.error:
                if source_pattern == catalia_collection:
                    source_matches.append(result)
        return source_matches

    def get_authorized_daac(self, source_matches: list, catalia_collection, daac_collections: list[str]):
        target_matches = defaultdict(list)
        for result in source_matches:
            target_pattern = result.get('targetProject', '')
            for daac_collection in daac_collections:
                try:
                    if re.match(target_pattern, daac_collection, re.IGNORECASE):
                        target_matches[daac_collection].append(result)
                except re.error:
                    if target_pattern == daac_collection:
                        target_matches[daac_collection].append(result)
        authorized_daac_collections = []
        for k, v in target_matches.items():
            if len(v) < 1:
                continue
            if len(v) == 1 and v[0].get(self.access, False):
                authorized_daac_collections.append(k)
                continue
            closest_target = min(v, key=lambda x: self._string_distance(x.get(self.target_project, ''), k))
            final_matches = [r for r in v if r.get(self.target_project) == closest_target.get(self.target_project)]
            if len(final_matches) < 1:
                continue
            if len(final_matches) == 0 and final_matches[0].get(self.access, False):
                authorized_daac_collections.append(k)
                continue
            closest_target_1 = min(final_matches, key=lambda x: self._string_distance(x.get(self.source_project, ''), catalia_collection))
            final_matches_1 = [r for r in final_matches if r.get(self.source_project) == closest_target_1.get(self.source_project)]
            if len(final_matches_1) < 1:
                continue
            if len(final_matches_1) > 1:
                logger.warning(f'duplicated Auth rows ? :{k} = {v}')
            if final_matches_1[0].get(self.access, False):
                authorized_daac_collections.append(k)
                continue
        return authorized_daac_collections

    def get_authorized_daac_full(self, user_group: list[str], catalia_collection, daac_collections: list[str]):
        source_matches = self.get_authorized_catalia(user_group, catalia_collection)
        return self.get_authorized_daac(source_matches, catalia_collection, daac_collections)

    def authorize(self, user_group: list[str], catalia_collection, daac_collection):
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
        results = []
        for group in user_group:
            group_results = self.__ddb.get(group, secondary_key=None)
            if group_results:
                results.extend(group_results)

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

        closest_target = min(target_matches, key=lambda x: self._string_distance(x.get(self.target_project, ''), daac_collection))

        final_matches = [r for r in target_matches if r.get(self.target_project) == closest_target.get(self.target_project)]

        if len(final_matches) == 1:
            return final_matches[0].get('access', False)

        closest_source = min(final_matches, key=lambda x: self._string_distance(x.get(self.source_project, ''), catalia_collection))
        final_matches = [r for r in target_matches if r.get(self.source_project) == closest_source.get(self.source_project)]

        return final_matches[0].get('access', False)

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
