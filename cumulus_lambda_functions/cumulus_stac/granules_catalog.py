import logging
import os
from collections import defaultdict

from pystac import Catalog, Item, Asset, Link

from cumulus_lambda_functions.lib.utils.file_utils import FileUtils
LOGGER = logging.getLogger(__name__)


class GranulesCatalog:
    def update_catalog(self, catalog_file_path: str, file_paths: list, rel_name: str = 'item'):
        if not FileUtils.file_exist(catalog_file_path):
            raise ValueError(f'missing file: {catalog_file_path}')
        catalog = FileUtils.read_json(catalog_file_path)
        catalog = Catalog.from_dict(catalog)
        catalog.clear_links(rel_name)
        for each_path in file_paths:
            catalog.add_link(Link('item', each_path, 'application/json'))
        return catalog.to_dict(False, False)

    def get_child_link_hrefs(self, catalog_file_path: str, rel_name: str = 'item'):
        if not FileUtils.file_exist(catalog_file_path):
            raise ValueError(f'missing file: {catalog_file_path}')
        catalog = FileUtils.read_json(catalog_file_path)
        catalog = Catalog.from_dict(catalog)
        child_links = [k.href for k in catalog.get_links(rel=rel_name)]
        catalog_dir = os.path.dirname(catalog_file_path)
        new_child_links = []
        for each_link in child_links:
            if not FileUtils.is_relative_path(each_link):
                new_child_links.append(each_link)
                continue
            new_child_links.append(os.path.join(catalog_dir, each_link))
        return new_child_links

    def get_granules_item(self, granule_stac_json) -> Item:
        if not FileUtils.file_exist(granule_stac_json):
            raise ValueError(f'missing file: {granule_stac_json}')
        granules_stac = FileUtils.read_json(granule_stac_json)
        granules_stac = Item.from_dict(granules_stac)
        return granules_stac

    def extract_assets_href(self, granules_stac: Item, dir_name: str = '') -> dict:
        try:
            self_dir = os.path.dirname(granules_stac.self_href)
        except:
            self_dir = None
        assets = defaultdict(list)
        for k, v in granules_stac.get_assets().items():
            href = v.href
            if v.roles is None or len(v.roles) < 1:
                LOGGER.warning(f'asset do not have roles: {v}')
                continue
            k = v.roles[0]
            if not FileUtils.is_relative_path(href):
                assets[k].append(href)
                continue
            if dir_name is not None and len(dir_name) > 0:
                assets[k].append(os.path.join(dir_name, href))
                continue
            if self_dir is not None and len(self_dir) > 0:
                assets[k].append(os.path.join(self_dir, href))
                continue
            assets[k].append(href)
        return assets

    def update_assets_href(self, granules_stac: Item,  new_assets: dict):
        for k, v in new_assets.items():
            if k in granules_stac.assets:
                existing_asset = granules_stac.assets.get(k)
                existing_asset.href = v
            else:
                existing_asset = Asset(v, k)
            granules_stac.add_asset(k, existing_asset)
        return self
