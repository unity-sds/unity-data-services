import os
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
os.environ['no_proxy'] = '*'
import logging

import requests

logging.basicConfig(level=10, format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")

import math
from unittest.mock import patch, MagicMock
import json
import tempfile
from glob import glob
from sys import argv
from unittest import TestCase

from pystac import Item, Asset, Catalog, Link, ItemCollection

from mdps_ds_lib.lib.constants import Constants

from cumulus_lambda_functions.docker_entrypoint.__main__ import choose_process
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.lib.utils.file_utils import FileUtils


class TestDockerStageIn(TestCase):
    def test_02_download(self):
        granule_json = '{"numberMatched": 20, "numberReturned": 20, "stac_version": "1.0.0", "type": "FeatureCollection", "links": [{"rel": "self", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"}, {"rel": "root", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com"}, {"rel": "next", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=100"}, {"rel": "prev", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"}], "features": [{"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.01", "properties": {"start_datetime": "2016-01-14T09:54:00Z", "end_datetime": "2016-01-14T10:00:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:39.830000Z", "datetime": "2022-08-15T06:26:37.029000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.08", "properties": {"start_datetime": "2016-01-14T10:36:00Z", "end_datetime": "2016-01-14T10:42:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.078000Z", "datetime": "2022-08-15T06:26:19.333000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.06", "properties": {"start_datetime": "2016-01-14T10:24:00Z", "end_datetime": "2016-01-14T10:30:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.068000Z", "datetime": "2022-08-15T06:26:18.641000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.18", "properties": {"start_datetime": "2016-01-14T11:36:00Z", "end_datetime": "2016-01-14T11:42:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.060000Z", "datetime": "2022-08-15T06:26:19.698000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.04", "properties": {"start_datetime": "2016-01-14T10:12:00Z", "end_datetime": "2016-01-14T10:18:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.050000Z", "datetime": "2022-08-15T06:26:19.491000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.16", "properties": {"start_datetime": "2016-01-14T11:24:00Z", "end_datetime": "2016-01-14T11:30:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:25.917000Z", "datetime": "2022-08-15T06:26:19.027000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.16.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.16.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.16.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.16.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.16.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.16.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.16.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.16.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.16.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.17", "properties": {"start_datetime": "2016-01-14T11:30:00Z", "end_datetime": "2016-01-14T11:36:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:25.907000Z", "datetime": "2022-08-15T06:26:19.042000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.17.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.17.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.17.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.17.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.17.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.17.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.17.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.17.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.17.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.10", "properties": {"start_datetime": "2016-01-14T10:48:00Z", "end_datetime": "2016-01-14T10:54:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:25.446000Z", "datetime": "2022-08-15T06:26:18.730000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.10.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.10.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.10.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.10.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.10.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.10.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.10.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.10.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.10.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.14", "properties": {"start_datetime": "2016-01-14T11:12:00Z", "end_datetime": "2016-01-14T11:18:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:25.354000Z", "datetime": "2022-08-15T06:26:17.758000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.14.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.14.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.14.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.14.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.14.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.14.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.14.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.14.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.14.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.12", "properties": {"start_datetime": "2016-01-14T11:00:00Z", "end_datetime": "2016-01-14T11:06:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:25.344000Z", "datetime": "2022-08-15T06:26:17.938000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.12.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.12.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.12.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.12.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.12.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.12.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.12.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.12.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.12.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.09", "properties": {"start_datetime": "2016-01-14T10:42:00Z", "end_datetime": "2016-01-14T10:48:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:24.910000Z", "datetime": "2022-08-15T06:26:20.688000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.09.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.09.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.09.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.09.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.09.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.09.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.09.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.09.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.09.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.20", "properties": {"start_datetime": "2016-01-14T11:48:00Z", "end_datetime": "2016-01-14T11:54:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:23.929000Z", "datetime": "2022-08-15T06:26:19.091000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.20.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.20.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.20.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.20.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.20.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.20.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.20.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.20.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.20.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.15", "properties": {"start_datetime": "2016-01-14T11:18:00Z", "end_datetime": "2016-01-14T11:24:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:23.732000Z", "datetime": "2022-08-15T06:26:19.282000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.15.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.15.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.15.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.15.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.15.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.15.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.15.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.15.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.15.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.07", "properties": {"start_datetime": "2016-01-14T10:30:00Z", "end_datetime": "2016-01-14T10:36:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:23.371000Z", "datetime": "2022-08-15T06:26:19.047000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.07.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.07.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.07.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.07.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.07.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.07.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.07.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.07.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.07.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.19", "properties": {"start_datetime": "2016-01-14T11:42:00Z", "end_datetime": "2016-01-14T11:48:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:23.268000Z", "datetime": "2022-08-15T06:26:18.576000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.19.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.19.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.19.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.19.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.19.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.19.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.19.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.19.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.19.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.03", "properties": {"start_datetime": "2016-01-14T10:06:00Z", "end_datetime": "2016-01-14T10:12:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:22.930000Z", "datetime": "2022-08-15T06:26:17.714000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.03.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.03.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.03.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.03.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.03.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.03.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.03.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.03.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.03.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.11", "properties": {"start_datetime": "2016-01-14T10:54:00Z", "end_datetime": "2016-01-14T11:00:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:22.863000Z", "datetime": "2022-08-15T06:26:17.648000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.11.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.11.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.11.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.11.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.11.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.11.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.11.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.11.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.11.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.05", "properties": {"start_datetime": "2016-01-14T10:18:00Z", "end_datetime": "2016-01-14T10:24:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:22.649000Z", "datetime": "2022-08-15T06:26:18.060000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.05.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.05.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.05.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.05.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.05.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.05.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.05.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.05.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.05.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.13", "properties": {"start_datetime": "2016-01-14T11:06:00Z", "end_datetime": "2016-01-14T11:12:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:22.277000Z", "datetime": "2022-08-15T06:26:18.090000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.13.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.13.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.13.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.13.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.13.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.13.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.13.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.13.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.13.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.02", "properties": {"start_datetime": "2016-01-14T10:00:00Z", "end_datetime": "2016-01-14T10:06:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:22.169000Z", "datetime": "2022-08-15T06:26:17.466000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.02.nc", "title": "SNDR.SNPP.ATMS.L1A.nominal2.02.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.02.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.02.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.02.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.02.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.02.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.02.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.02.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}]}'
        granule_json = json.loads(granule_json)
        os.environ['STAC_JSON'] = json.dumps(granule_json)
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'S3'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['DOWNLOAD_DIR'] = tmp_dir_name
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 2, len(glob(os.path.join(tmp_dir_name, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__daac(self):
        granule_json = '{"type": "FeatureCollection", "stac_version": "1.0.0", "numberMatched": 3413, "numberReturned": 23, "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac?collection_concept_id=C1996881146-POCLOUD&page_size=23&temporal%5B%5D=2002-06-01T12%3A06%3A00.000Z%2C2011-10-04T06%3A51%3A45.000Z&page_num=1"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "next", "body": {"collection_concept_id": "C1996881146-POCLOUD", "page_num": "2", "page_size": "23", "temporal": ["2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"], "temporal[]": "2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"}, "method": "POST", "merge": true, "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac"}], "context": {"returned": 23, "limit": 1000000, "matched": 3413}, "features": [{"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-01T21:00:00.000Z", "start_datetime": "2002-06-01T21:00:00.000Z", "end_datetime": "2002-06-02T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106835-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-02T21:00:00.000Z", "start_datetime": "2002-06-02T21:00:00.000Z", "end_datetime": "2002-06-03T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106890-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-03T21:00:00.000Z", "start_datetime": "2002-06-03T21:00:00.000Z", "end_datetime": "2002-06-04T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106962-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-04T21:00:00.000Z", "start_datetime": "2002-06-04T21:00:00.000Z", "end_datetime": "2002-06-05T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106862-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.umm_json"}]}]}'
        granule_json = json.loads(granule_json)
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        os.environ['STAC_JSON'] = json.dumps(granule_json)
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        os.environ['DOWNLOADING_KEYS'] = 'metadata'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['DOWNLOAD_DIR'] = tmp_dir_name
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 2, len(glob(os.path.join(tmp_dir_name, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['metadata']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['metadata']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__daac_from_url(self):
        os.environ['STAC_JSON'] = 'https://cmr.earthdata.nasa.gov/search/granules.stac?collection_concept_id=C2011289787-GES_DISC&page_num=1&page_size=1'
        granule_json = requests.get(os.environ['STAC_JSON'])
        granule_json = json.loads(granule_json.text)
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        # os.environ['STAC_JSON'] = json.dumps(granule_json)

        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        os.environ['DOWNLOADING_KEYS'] = 'data,metadata'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            os.environ['DOWNLOAD_DIR'] = tmp_dir_name
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            print(download_result)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) * len(os.environ['DOWNLOADING_KEYS'].split(',')) + 2, len(glob(os.path.join(tmp_dir_name, '*'))),
                             f'downloaded file does not match: {glob(os.path.join(tmp_dir_name, "*"))} v. {download_result["features"]}')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            print(download_result)
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__daac__from_file(self):
        granule_json = '{"type": "FeatureCollection", "stac_version": "1.0.0", "numberMatched": 3413, "numberReturned": 23, "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac?collection_concept_id=C1996881146-POCLOUD&page_size=23&temporal%5B%5D=2002-06-01T12%3A06%3A00.000Z%2C2011-10-04T06%3A51%3A45.000Z&page_num=1"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "next", "body": {"collection_concept_id": "C1996881146-POCLOUD", "page_num": "2", "page_size": "23", "temporal": ["2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"], "temporal[]": "2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"}, "method": "POST", "merge": true, "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac"}], "context": {"returned": 23, "limit": 1000000, "matched": 3413}, "features": [{"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020601090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-01T21:00:00.000Z", "start_datetime": "2002-06-01T21:00:00.000Z", "end_datetime": "2002-06-02T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020602090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106835-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106835-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-02T21:00:00.000Z", "start_datetime": "2002-06-02T21:00:00.000Z", "end_datetime": "2002-06-03T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020603090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106890-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106890-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-03T21:00:00.000Z", "start_datetime": "2002-06-03T21:00:00.000Z", "end_datetime": "2002-06-04T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020604090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106962-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106962-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-06-04T21:00:00.000Z", "start_datetime": "2002-06-04T21:00:00.000Z", "end_datetime": "2002-06-05T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"metadata": {"href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.xml", "type": "application/xml"}, "opendap": {"title": "OPeNDAP request URL", "href": "https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%204%20MUR%20Global%20Foundation%20Sea%20Surface%20Temperature%20Analysis%20(v4.1)/granules/20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"}, "data": {"title": "Download 20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc", "href": "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/20020605090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2028106862-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2028106862-POCLOUD.umm_json"}]}]}'
        granule_json = json.loads(granule_json)
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        os.environ['DOWNLOADING_KEYS'] = 'metadata'

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['metadata']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['metadata']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__daac_502__from_file(self):
        granule_json = '''{
      "type": "FeatureCollection",
      "stac_version": "1.0.0",
      "numberMatched": 242,
      "numberReturned": 10,
      "links": [
        {
          "rel": "self",
          "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac?collection_concept_id=C2011289787-GES_DISC&page_size=10&temporal%5B%5D=2021-02-01T00%3A00%3A00Z%2C2021-02-02T00%3A00%3A00Z&page_num=1"
        },
        {
          "rel": "root",
          "href": "https://cmr.earthdata.nasa.gov:443/search/"
        },
        {
          "rel": "next",
          "body": {
            "collection_concept_id": "C2011289787-GES_DISC",
            "page_num": "2",
            "page_size": "10",
            "temporal": [
              "2021-02-01T00:00:00Z,2021-02-02T00:00:00Z"
            ],
            "temporal[]": "2021-02-01T00:00:00Z,2021-02-02T00:00:00Z"
          },
          "method": "POST",
          "merge": true,
          "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac"
        }
      ],
      "context": {
        "returned": 10,
        "limit": 1000000,
        "matched": 242
      },
      "features": [
        {
          "properties": {
            "datetime": "2021-01-31T23:54:00.000Z",
            "start_datetime": "2021-01-31T23:54:00.000Z",
            "end_datetime": "2021-02-01T00:00:00.000Z"
          },
          "bbox": [
            -164.22,
            -59.19,
            -127.42,
            -34.4
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327589-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/031/SNDR.SS1330.CHIRP.20210131T2354.m06.g240.L1_J1.std.v02_48.G.200408101645.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210131T2354.m06.g240.L1_J1.std.v02_48.G.200408101645.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/031/SNDR.SS1330.CHIRP.20210131T2354.m06.g240.L1_J1.std.v02_48.G.200408101645.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -127.42,
                  -53.49
                ],
                [
                  -140.59,
                  -34.4
                ],
                [
                  -164.22,
                  -38.4
                ],
                [
                  -161.84,
                  -59.19
                ],
                [
                  -127.42,
                  -53.49
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327589-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327589-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327589-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327589-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:00:00.000Z",
            "start_datetime": "2021-02-01T00:00:00.000Z",
            "end_datetime": "2021-02-01T00:06:00.000Z"
          },
          "bbox": [
            -167.61,
            -38.28,
            -140.62,
            -14.06
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327600-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0000.m06.g001.L1_J1.std.v02_48.G.200408101657.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0000.m06.g001.L1_J1.std.v02_48.G.200408101657.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0000.m06.g001.L1_J1.std.v02_48.G.200408101657.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -140.62,
                  -34.28
                ],
                [
                  -147.98,
                  -14.06
                ],
                [
                  -167.61,
                  -17.44
                ],
                [
                  -164.31,
                  -38.28
                ],
                [
                  -140.62,
                  -34.28
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327600-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327600-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327600-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327600-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:06:00.000Z",
            "start_datetime": "2021-02-01T00:06:00.000Z",
            "end_datetime": "2021-02-01T00:12:00.000Z"
          },
          "bbox": [
            -171.93,
            -17.31,
            -148.0,
            6.74
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327624-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0006.m06.g002.L1_J1.std.v02_48.G.200408101655.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0006.m06.g002.L1_J1.std.v02_48.G.200408101655.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0006.m06.g002.L1_J1.std.v02_48.G.200408101655.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -148.0,
                  -13.93
                ],
                [
                  -153.06,
                  6.74
                ],
                [
                  -171.93,
                  3.48
                ],
                [
                  -167.7,
                  -17.31
                ],
                [
                  -148.0,
                  -13.93
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327624-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327624-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327624-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327624-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:12:00.000Z",
            "start_datetime": "2021-02-01T00:12:00.000Z",
            "end_datetime": "2021-02-01T00:18:00.000Z"
          },
          "bbox": [
            -177.83,
            3.6,
            -153.07,
            27.71
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327611-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0012.m06.g003.L1_J1.std.v02_48.G.200408101705.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0012.m06.g003.L1_J1.std.v02_48.G.200408101705.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0012.m06.g003.L1_J1.std.v02_48.G.200408101705.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -153.07,
                  6.87
                ],
                [
                  -156.97,
                  27.71
                ],
                [
                  -177.83,
                  24.15
                ],
                [
                  -172.02,
                  3.6
                ],
                [
                  -153.07,
                  6.87
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327611-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327611-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327611-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327611-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:18:00.000Z",
            "start_datetime": "2021-02-01T00:18:00.000Z",
            "end_datetime": "2021-02-01T00:24:00.000Z"
          },
          "bbox": [
            172.75,
            24.27,
            -156.97,
            48.71
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327811-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0018.m06.g004.L1_J1.std.v02_48.G.200408101716.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0018.m06.g004.L1_J1.std.v02_48.G.200408101716.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0018.m06.g004.L1_J1.std.v02_48.G.200408101716.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -156.97,
                  27.84
                ],
                [
                  -160.07,
                  48.71
                ],
                [
                  172.75,
                  44.19
                ],
                [
                  -177.94,
                  24.27
                ],
                [
                  -156.97,
                  27.84
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327811-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327811-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327811-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327811-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:24:00.000Z",
            "start_datetime": "2021-02-01T00:24:00.000Z",
            "end_datetime": "2021-02-01T00:30:00.000Z"
          },
          "bbox": [
            152.97,
            44.29,
            -160.05,
            69.67
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327763-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0024.m06.g005.L1_J1.std.v02_48.G.200408101749.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0024.m06.g005.L1_J1.std.v02_48.G.200408101749.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0024.m06.g005.L1_J1.std.v02_48.G.200408101749.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -160.05,
                  48.84
                ],
                [
                  -161.92,
                  69.67
                ],
                [
                  152.97,
                  62.28
                ],
                [
                  172.6,
                  44.29
                ],
                [
                  -160.05,
                  48.84
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327763-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327763-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327763-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327763-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:30:00.000Z",
            "start_datetime": "2021-02-01T00:30:00.000Z",
            "end_datetime": "2021-02-01T00:36:00.000Z"
          },
          "bbox": [
            -180.0,
            62.35,
            180.0,
            90.0
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327782-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0030.m06.g006.L1_J1.std.v02_48.G.200408101747.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0030.m06.g006.L1_J1.std.v02_48.G.200408101747.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0030.m06.g006.L1_J1.std.v02_48.G.200408101747.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -161.83,
                  69.79
                ],
                [
                  -45.22,
                  88.83
                ],
                [
                  101.33,
                  71.69
                ],
                [
                  152.69,
                  62.35
                ],
                [
                  -161.83,
                  69.79
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327782-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327782-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327782-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327782-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:36:00.000Z",
            "start_datetime": "2021-02-01T00:36:00.000Z",
            "end_datetime": "2021-02-01T00:42:00.000Z"
          },
          "bbox": [
            -41.63,
            61.83,
            100.91,
            89.26695841076085
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327806-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0036.m06.g007.L1_J1.std.v02_48.G.200408101747.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0036.m06.g007.L1_J1.std.v02_48.G.200408101747.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0036.m06.g007.L1_J1.std.v02_48.G.200408101747.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  -41.63,
                  88.73
                ],
                [
                  6.42,
                  68.41
                ],
                [
                  50.76,
                  61.83
                ],
                [
                  100.91,
                  71.65
                ],
                [
                  -41.63,
                  88.73
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327806-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327806-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327806-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327806-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:42:00.000Z",
            "start_datetime": "2021-02-01T00:42:00.000Z",
            "end_datetime": "2021-02-01T00:48:00.000Z"
          },
          "bbox": [
            4.45,
            43.65,
            50.62,
            68.30202151196218
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327773-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0042.m06.g008.L1_J1.std.v02_48.G.200408101807.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0042.m06.g008.L1_J1.std.v02_48.G.200408101807.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0042.m06.g008.L1_J1.std.v02_48.G.200408101807.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  6.29,
                  68.29
                ],
                [
                  4.45,
                  47.46
                ],
                [
                  31.46,
                  43.65
                ],
                [
                  50.62,
                  61.71
                ],
                [
                  6.29,
                  68.29
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327773-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327773-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327773-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327773-GES_DISC.umm_json"
            }
          ]
        },
        {
          "properties": {
            "datetime": "2021-02-01T00:48:00.000Z",
            "start_datetime": "2021-02-01T00:48:00.000Z",
            "end_datetime": "2021-02-01T00:54:00.000Z"
          },
          "bbox": [
            1.29,
            23.6,
            31.41,
            47.33
          ],
          "assets": {
            "metadata": {
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327751-GES_DISC.xml",
              "type": "application/xml"
            },
            "opendap": {
              "title": "The OPENDAP location for the granule. (GET DATA : OPENDAP DATA)",
              "href": "https://sounder.gesdisc.eosdis.nasa.gov/opendap/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0048.m06.g009.L1_J1.std.v02_48.G.200408101736.nc",
              "type": "application/x-netcdf"
            },
            "data": {
              "title": "Download SNDR.SS1330.CHIRP.20210201T0048.m06.g009.L1_J1.std.v02_48.G.200408101736.nc",
              "href": "https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2021/032/SNDR.SS1330.CHIRP.20210201T0048.m06.g009.L1_J1.std.v02_48.G.200408101736.nc"
            }
          },
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  4.35,
                  47.33
                ],
                [
                  1.29,
                  26.46
                ],
                [
                  22.18,
                  23.6
                ],
                [
                  31.41,
                  43.52
                ],
                [
                  4.35,
                  47.33
                ]
              ]
            ]
          },
          "stac_extensions": [],
          "id": "G2031327751-GES_DISC",
          "stac_version": "1.0.0",
          "collection": "C2011289787-GES_DISC",
          "links": [
            {
              "rel": "self",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327751-GES_DISC.stac"
            },
            {
              "rel": "parent",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "collection",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C2011289787-GES_DISC.stac"
            },
            {
              "rel": "root",
              "href": "https://cmr.earthdata.nasa.gov:443/search/"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327751-GES_DISC.json"
            },
            {
              "rel": "via",
              "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2031327751-GES_DISC.umm_json"
            }
          ]
        }
      ]
    }'''
        granule_json = json.loads(granule_json)
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        os.environ['DOWNLOADING_KEYS'] = 'data'

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__daac_error(self):  # TODO update this later
        granule_json = '{"type": "FeatureCollection", "stac_version": "1.0.0", "numberMatched": 3413, "numberReturned": 23, "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac?collection_concept_id=C1996881146-POCLOUD&page_size=23&temporal%5B%5D=2002-06-01T12%3A06%3A00.000Z%2C2011-10-04T06%3A51%3A45.000Z&page_num=1"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "next", "body": {"collection_concept_id": "C1996881146-POCLOUD", "page_num": "2", "page_size": "23", "temporal": ["2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"], "temporal[]": "2002-06-01T12:06:00.000Z,2011-10-04T06:51:45.000Z"}, "method": "POST", "merge": true, "href": "https://cmr.earthdata.nasa.gov:443/search/granules.stac"}], "context": {"returned": 23, "limit": 1000000, "matched": 3413}, "features": [{"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601161248-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00414.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601172624-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00415.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601190536-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00416.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601204344-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00417.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601222152-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00418.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602000000-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00419.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602013912-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00420.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602031720-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00421.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602045528-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00422.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602063440-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00423.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602081248-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00424.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602095056-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00425.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602112904-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00426.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602130816-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00427.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602144624-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00428.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602162432-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00429.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602180240-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00430.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602194152-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00431.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602212000-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00432.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602225808-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00433.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603003616-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00434.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603021528-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00435.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}, {"properties": {"datetime": "2002-05-31T21:00:00.000Z", "start_datetime": "2002-05-31T21:00:00.000Z", "end_datetime": "2002-06-01T21:00:00.000Z"}, "bbox": [-180.0, -90.0, 180.0, 90.0], "assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603035336-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00436.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-180.0, -90.0], [180.0, -90.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, -90.0]]]}, "stac_extensions": [], "id": "G2030963432-POCLOUD", "stac_version": "1.0.0", "collection": "C1996881146-POCLOUD", "links": [{"rel": "self", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.stac"}, {"rel": "parent", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "collection", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/C1996881146-POCLOUD.stac"}, {"rel": "root", "href": "https://cmr.earthdata.nasa.gov:443/search/"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.json"}, {"rel": "via", "href": "https://cmr.earthdata.nasa.gov:443/search/concepts/G2030963432-POCLOUD.umm_json"}]}]}'
        # granule_json = [{"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601161248-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00414.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601172624-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00415.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601190536-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00416.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601204344-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00417.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/152/20020601222152-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00418.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602000000-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00419.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602013912-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00420.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602031720-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00421.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602045528-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00422.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602063440-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00423.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602081248-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00424.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602095056-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00425.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602112904-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00426.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602130816-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00427.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602144624-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00428.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602162432-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00429.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602180240-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00430.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602194152-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00431.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602212000-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00432.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/153/20020602225808-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00433.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603003616-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00434.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603021528-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00435.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}, {"assets": {"data": {"href": "https://podaac-tools.jpl.nasa.gov/drive/files/allData/ghrsst/data/GDS2/L2P/AMSRE/REMSS/v7/2002/154/20020603035336-REMSS-L2P_GHRSST-SSTsubskin-AMSRE-l2b_v07a_r00436.dat-v02.0-fv01.0.nc", "title": "The HTTP location for the granule."}}}]
        granule_json = json.loads(granule_json)
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        os.environ['STAC_JSON'] = json.dumps(granule_json)
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            # TODO this is downloading a login page HTML
            os.environ['DOWNLOAD_DIR'] = tmp_dir_name
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            print(glob(os.path.join(tmp_dir_name, '*')))
            self.assertEqual(len(download_result['features']) + 2, len(glob(os.path.join(tmp_dir_name, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_dapa_url(self):
        dapa_url = 'https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev/sbx-uds-2-dapa/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2401310000/items?limit=37&offset=0&datetime=1990-01-14T08:00:00Z/2024-01-14T11:59:59Z'
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ[Constants.USERNAME] = '/unity/uds/user/wphyo/username'
        os.environ[Constants.PASSWORD] = '/unity/uds/user/wphyo/dwssap'
        os.environ['API_PREFIX'] = 'sbx-uds-2-dapa'
        os.environ['PASSWORD_TYPE'] = 'PARAM_STORE'
        os.environ['CLIENT_ID'] = '71g0c73jl77gsqhtlfg2ht388c'
        os.environ['COGNITO_URL'] = 'https://cognito-idp.us-west-2.amazonaws.com'
        os.environ['DAPA_API'] = 'https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev'
        os.environ['VERIFY_SSL'] = 'FALSE'
        os.environ['STAC_AUTH_TYPE'] = 'UNITY'

        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'S3'
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            os.environ['STAC_JSON'] = dapa_url
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) * 4 + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {download_result["features"]}')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            print(download_result)
            expected_downloaded_feature = [{'type': 'Feature', 'stac_version': '1.0.0',
                                            'id': 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2401310000:test_file05',
                                            'properties': {'tag': '#sample', 'c_data1': [1, 10, 100, 1000],
                                                           'c_data2': [False, True, True, False, True],
                                                           'c_data3': ['Bellman Ford'],
                                                           'datetime': '2024-01-31T22:34:06.556000Z',
                                                           'start_datetime': '2016-01-31T18:00:00.009000Z',
                                                           'end_datetime': '2016-01-31T19:59:59.991000Z',
                                                           'created': '1970-01-01T00:00:00Z',
                                                           'updated': '2024-01-31T22:34:49.583000Z',
                                                           'status': 'completed', 'provider': 'unity'},
                                            'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
                                            'links': [{'rel': 'collection', 'href': '.'}], 'assets': {
                    'test_file05.cmr.xml': {'href': './test_file05.cmr.xml', 'title': 'test_file05.cmr.xml',
                                            'description': 'size=1768;checksumType=md5;checksum=29d1b69df5587d7ee0a945250adfd16f;',
                                            'roles': ['metadata']},
                    'test_file05.nc.stac.json': {'href': './test_file05.nc.stac.json',
                                                 'title': 'test_file05.nc.stac.json',
                                                 'description': 'size=-1;checksumType=md5;checksum=unknown;',
                                                 'roles': ['metadata']},
                    'test_file05.nc.cas': {'href': './test_file05.nc.cas', 'title': 'test_file05.nc.cas',
                                           'description': 'size=-1;checksumType=md5;checksum=unknown;',
                                           'roles': ['metadata']},
                    'test_file05.data.stac.json': {'href': './test_file05.data.stac.json',
                                                   'title': 'test_file05.data.stac.json',
                                                   'description': 'size=-1;checksumType=md5;checksum=unknown;',
                                                   'roles': ['data']}}, 'bbox': [-180.0, -90.0, 180.0, 90.0],
                                            'stac_extensions': [],
                                            'collection': 'URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2401310000'}]

            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['test_file05.data.stac.json']['href'] for k in download_result])
            for each_granule in zip(expected_downloaded_feature, download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['test_file05.data.stac.json']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_file(self):
        granule_json = '{"numberMatched": {"total_size": 5}, "numberReturned": 6, "stac_version": "1.0.0", "type": "FeatureCollection", ' \
                       '"links": [{"rel": "self", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev/sbx-uds-2-dapa/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items/?limit=10"}, {"rel": "root", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev"}], ' \
                       '"features": [' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:21:04.234000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:21:47.477000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.cmr.xml", "title": "test_file01.cmr.xml", "description": "size=1768;checksumType=md5;checksum=4d1935f25f3b508ca1e1a0368eeda10c;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.stac.json", "title": "test_file01.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.cas", "title": "test_file01.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc", "title": "test_file01.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:44:56.784000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:45:40.118000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.stac.json", "title": "test_file02.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.cmr.xml", "title": "test_file02.cmr.xml", "description": "size=1768;checksumType=md5;checksum=88b82e1824d51713d0bc897d970f3b0a;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.cas", "title": "test_file02.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc", "title": "test_file02.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:01.078000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:54:42.272000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.cmr.xml", "title": "test_file03.cmr.xml", "description": "size=1768;checksumType=md5;checksum=cd84e6a6138b3aad77d013ca4fb3ded4;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.stac.json", "title": "test_file03.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.cas", "title": "test_file03.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc", "title": "test_file03.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:33.221000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:55:12.198000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.cmr.xml", "title": "test_file04.cmr.xml", "description": "size=1768;checksumType=md5;checksum=47574084df6d14bbe9df60a2d40617ef;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.stac.json", "title": "test_file04.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.cas", "title": "test_file04.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc", "title": "test_file04.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:58:31.381000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:58:42.027000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.stac.json", "title": "test_file05.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.cmr.xml", "title": "test_file05.cmr.xml", "description": "size=1768;checksumType=md5;checksum=03e639becc6c74ad5128ccd438fc35ae;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.cas", "title": "test_file05.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc", "title": "test_file05.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"} ' \
                       ']}'
        granule_json = json.loads(granule_json)
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'S3'
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) * 4 + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {download_result["features"]}')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            print(downloaded_file_hrefs)
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
                self.assertTrue(FileUtils.get_size(os.path.join(downloading_dir, remote_filename)) > 0, f'empty file: {remote_filename}')
                print()
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_file_large_github_data_file(self):
        granule_json = '''
        {
            "numberMatched": 20,
            "numberReturned": 20,
            "stac_version": "1.0.0",
            "type": "FeatureCollection",
            "links": [
                {
                    "rel": "self",
                    "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"
                },
                {
                    "rel": "root",
                    "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com"
                },
                {
                    "rel": "next",
                    "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=100"
                },
                {
                    "rel": "prev",
                    "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"
                }
            ],
            "features": [
                {
                    "type": "Feature",
                    "stac_version": "1.0.0",
                    "id": "SNDR.SNPP.ATMS.L1A.nominal2.01",
                    "properties": {
                        "start_datetime": "2016-01-14T09:54:00Z",
                        "end_datetime": "2016-01-14T10:00:00Z",
                        "created": "2020-12-14T13:50:00Z",
                        "updated": "2022-08-15T06:26:39.830000Z",
                        "datetime": "2022-08-15T06:26:37.029000Z"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            0.0,
                            0.0
                        ]
                    },
                    "links": [
                        {
                            "rel": "collection",
                            "href": "."
                        }
                    ],
                    "assets": {
                        "data": {
                            "href": "https://raw.githubusercontent.com/unity-sds/unity-tutorial-application/main/test/stage_in/SNDR.SS1330.CHIRP.20160822T0005.m06.g001.L1_AQ.std.v02_48.G.200425095850.nc",
                            "title": "SNDR.SS1330.CHIRP.20160822T0005.m06.g001.L1_AQ.std.v02_48.G.200425095850.nc",
                            "description": "SNDR.SS1330.CHIRP.20160822T0005.m06.g001.L1_AQ.std.v02_48.G.200425095850.nc"
                        }
                    },
                    "bbox": [
                        0.0,
                        0.0,
                        0.0,
                        0.0
                    ],
                    "stac_extensions": [],
                    "collection": "SNDR_SNPP_ATMS_L1A___1"
                },
                {
                    "type": "Feature",
                    "stac_version": "1.0.0",
                    "id": "SNDR.SNPP.ATMS.L1A.nominal2.08",
                    "properties": {
                        "start_datetime": "2016-01-14T10:36:00Z",
                        "end_datetime": "2016-01-14T10:42:00Z",
                        "created": "2020-12-14T13:50:00Z",
                        "updated": "2022-08-15T06:26:26.078000Z",
                        "datetime": "2022-08-15T06:26:19.333000Z"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            0.0,
                            0.0
                        ]
                    },
                    "links": [
                        {
                            "rel": "collection",
                            "href": "."
                        }
                    ],
                    "assets": {
                        "data": {
                            "href": "https://raw.githubusercontent.com/unity-sds/unity-tutorial-application/main/test/stage_in/SNDR.SS1330.CHIRP.20160822T0011.m06.g002.L1_AQ.std.v02_48.G.200425095901.nc",
                            "title": "SNDR.SS1330.CHIRP.20160822T0011.m06.g002.L1_AQ.std.v02_48.G.200425095901.nc",
                            "description": "SNDR.SS1330.CHIRP.20160822T0011.m06.g002.L1_AQ.std.v02_48.G.200425095901.nc"
                        }
                    },
                    "bbox": [
                        0.0,
                        0.0,
                        0.0,
                        0.0
                    ],
                    "stac_extensions": [],
                    "collection": "SNDR_SNPP_ATMS_L1A___1"
                }
            ]
        }
        '''
        granule_json = json.loads(granule_json)
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'HTTP'
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            # tmp_dir_name = '/tmp/unity-ds'
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {download_result["features"]}')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
                self.assertTrue(FileUtils.get_size(os.path.join(downloading_dir, remote_filename)) > 40 * 2**20, f'empty file: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    @patch('requests.get')
    def test_02_download__from_file_with_http(self, mock_requests):
        granule_json = '{"numberMatched": {"total_size": 5}, "numberReturned": 6, "stac_version": "1.0.0", "type": "FeatureCollection", ' \
                       '"links": [{"rel": "self", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev/sbx-uds-2-dapa/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items/?limit=10"}, {"rel": "root", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev"}], ' \
                       '"features": [' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:21:04.234000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:21:47.477000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.cmr.xml", "title": "test_file01.cmr.xml", "description": "size=1768;checksumType=md5;checksum=4d1935f25f3b508ca1e1a0368eeda10c;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.stac.json", "title": "test_file01.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.cas", "title": "test_file01.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc", "title": "test_file01.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:44:56.784000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:45:40.118000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.stac.json", "title": "test_file02.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.cmr.xml", "title": "test_file02.cmr.xml", "description": "size=1768;checksumType=md5;checksum=88b82e1824d51713d0bc897d970f3b0a;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.cas", "title": "test_file02.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc", "title": "test_file02.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:01.078000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:54:42.272000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.cmr.xml", "title": "test_file03.cmr.xml", "description": "size=1768;checksumType=md5;checksum=cd84e6a6138b3aad77d013ca4fb3ded4;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.stac.json", "title": "test_file03.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.cas", "title": "test_file03.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc", "title": "test_file03.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:33.221000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:55:12.198000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.cmr.xml", "title": "test_file04.cmr.xml", "description": "size=1768;checksumType=md5;checksum=47574084df6d14bbe9df60a2d40617ef;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.stac.json", "title": "test_file04.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.cas", "title": "test_file04.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc", "title": "test_file04.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:58:31.381000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:58:42.027000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.stac.json", "title": "test_file05.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.cmr.xml", "title": "test_file05.cmr.xml", "description": "size=1768;checksumType=md5;checksum=03e639becc6c74ad5128ccd438fc35ae;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.cas", "title": "test_file05.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc", "title": "test_file05.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"} ' \
                       ']}'
        # granule_json = json.loads(granule_json)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.return_value.content.decode.return_value = granule_json

        # mock_response.content = granule_json.encode()
        # mock_response.content.return_value = granule_json.encode()
        # mock_response.json.return_value = json.loads(granule_json)
        # specify the return value of the get() method
        mock_requests.return_value.get.return_value = mock_response
        mock_requests.return_value.content.decode.return_value = granule_json

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'S3'
        os.environ['STAC_JSON'] = 'https://example.com/get_feature_collection'

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            granule_json = json.loads(granule_json)
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    @patch('requests.get')
    def test_02_download__from_file_with_http(self, mock_requests):
        granule_json = '{"numberMatched": {"total_size": 5}, "numberReturned": 6, "stac_version": "1.0.0", "type": "FeatureCollection", ' \
                       '"links": [{"rel": "self", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev/sbx-uds-2-dapa/collections/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/items/?limit=10"}, {"rel": "root", "href": "https://1gp9st60gd.execute-api.us-west-2.amazonaws.com/dev"}], ' \
                       '"features": [' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:21:04.234000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:21:47.477000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.cmr.xml", "title": "test_file01.cmr.xml", "description": "size=1768;checksumType=md5;checksum=4d1935f25f3b508ca1e1a0368eeda10c;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.stac.json", "title": "test_file01.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc.cas", "title": "test_file01.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file01/test_file01.nc", "title": "test_file01.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:44:56.784000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:45:40.118000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.stac.json", "title": "test_file02.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.cmr.xml", "title": "test_file02.cmr.xml", "description": "size=1768;checksumType=md5;checksum=88b82e1824d51713d0bc897d970f3b0a;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc.cas", "title": "test_file02.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file02/test_file02.nc", "title": "test_file02.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:01.078000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:54:42.272000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.cmr.xml", "title": "test_file03.cmr.xml", "description": "size=1768;checksumType=md5;checksum=cd84e6a6138b3aad77d013ca4fb3ded4;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.stac.json", "title": "test_file03.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc.cas", "title": "test_file03.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file03/test_file03.nc", "title": "test_file03.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:54:33.221000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:55:12.198000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.cmr.xml", "title": "test_file04.cmr.xml", "description": "size=1768;checksumType=md5;checksum=47574084df6d14bbe9df60a2d40617ef;"}, "metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.stac.json", "title": "test_file04.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc.cas", "title": "test_file04.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file04/test_file04.nc", "title": "test_file04.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"}, ' \
                       '{"type": "Feature", "stac_version": "1.0.0", "id": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05", "properties": {"tag": "#sample", "c_data1": [1, 10, 100, 1000], "c_data2": [false, true, true, false, true], "c_data3": ["Bellman Ford"], "datetime": "2023-12-04T18:58:31.381000Z", "start_datetime": "2016-01-31T18:00:00.009000Z", "end_datetime": "2016-01-31T19:59:59.991000Z", "created": "1970-01-01T00:00:00Z", "updated": "2023-12-04T18:58:42.027000Z", "status": "completed", "provider": "unity"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"metadata__stac": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.stac.json", "title": "test_file05.nc.stac.json", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "metadata__cmr": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.cmr.xml", "title": "test_file05.cmr.xml", "description": "size=1768;checksumType=md5;checksum=03e639becc6c74ad5128ccd438fc35ae;"}, "metadata__cas": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc.cas", "title": "test_file05.nc.cas", "description": "size=-1;checksumType=md5;checksum=unknown;"}, "data": {"href": "s3://uds-sbx-cumulus-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030:test_file05/test_file05.nc", "title": "test_file05.nc", "description": "size=-1;checksumType=md5;checksum=unknown;"}}, "bbox": [-180.0, -90.0, 180.0, 90.0], "stac_extensions": [], "collection": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2312041030"} ' \
                       ']}'
        # granule_json = json.loads(granule_json)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.return_value.content.decode.return_value = granule_json

        # mock_response.content = granule_json.encode()
        # mock_response.content.return_value = granule_json.encode()
        # mock_response.json.return_value = json.loads(granule_json)
        # specify the return value of the get() method
        mock_requests.return_value.get.return_value = mock_response
        mock_requests.return_value.content.decode.return_value = granule_json

        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'S3'
        os.environ['STAC_JSON'] = 'https://example.com/get_feature_collection'

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) * 4 + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {glob(os.path.join(downloading_dir, "*"))}')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            granule_json = json.loads(granule_json)
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_file_large(self):
        granule_json = FileUtils.read_json('./stage-in.json')
        # granule_json['features'] = granule_json['features'][0:5]
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ[Constants.EDL_USERNAME] = '/unity/uds/user/wphyo/edl_username'
        os.environ[Constants.EDL_PASSWORD] = '/unity/uds/user/wphyo/edl_dwssap'
        os.environ[Constants.EDL_PASSWORD_TYPE] = Constants.PARAM_STORE
        os.environ[Constants.EDL_BASE_URL] = 'urs.earthdata.nasa.gov'
        os.environ['STAC_JSON'] = json.dumps(granule_json)
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'DAAC'
        # os.environ['PARALLEL_COUNT'] = '5'

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            print(tmp_dir_name)
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            print(len(download_result['features']))
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match')
            error_file = os.path.join(downloading_dir, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_http(self):
        granule_json = '{"numberMatched": 20, "numberReturned": 20, "stac_version": "1.0.0", "type": "FeatureCollection", "links": [{"rel": "self", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"}, {"rel": "root", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com"}, {"rel": "next", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=100"}, {"rel": "prev", "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"}], "features": [{"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.01", "properties": {"start_datetime": "2016-01-14T09:54:00Z", "end_datetime": "2016-01-14T10:00:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:39.830000Z", "datetime": "2022-08-15T06:26:37.029000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/README.md", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.08", "properties": {"start_datetime": "2016-01-14T10:36:00Z", "end_datetime": "2016-01-14T10:42:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.078000Z", "datetime": "2022-08-15T06:26:19.333000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CHANGELOG.md", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.06", "properties": {"start_datetime": "2016-01-14T10:24:00Z", "end_datetime": "2016-01-14T10:30:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.068000Z", "datetime": "2022-08-15T06:26:18.641000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CODE_OF_CONDUCT.md", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.18", "properties": {"start_datetime": "2016-01-14T11:36:00Z", "end_datetime": "2016-01-14T11:42:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.060000Z", "datetime": "2022-08-15T06:26:19.698000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CONTRIBUTING.md", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}, {"type": "Feature", "stac_version": "1.0.0", "id": "SNDR.SNPP.ATMS.L1A.nominal2.04", "properties": {"start_datetime": "2016-01-14T10:12:00Z", "end_datetime": "2016-01-14T10:18:00Z", "created": "2020-12-14T13:50:00Z", "updated": "2022-08-15T06:26:26.050000Z", "datetime": "2022-08-15T06:26:19.491000Z"}, "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "links": [{"rel": "collection", "href": "."}], "assets": {"data": {"href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/LICENSE", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc"}, "metadata__data": {"href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas"}, "metadata__cmr": {"href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml", "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml", "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml"}}, "bbox": [0.0, 0.0, 0.0, 0.0], "stac_extensions": [], "collection": "SNDR_SNPP_ATMS_L1A___1"}]}'
        granule_json = json.loads(granule_json)
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'HTTP'
        os.environ['PARALLEL_COUNT'] = '3'
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            os.environ['DOWNLOADING_KEYS'] = 'data'
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {download_result["features"]} v. {glob(os.path.join(downloading_dir, "*"))}')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([k['assets']['data']['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = os.path.basename(each_granule[0]['assets']['data']['href'])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs,
                                f'mismatched: {remote_filename}')
                self.assertTrue(FileUtils.get_size(os.path.join(downloading_dir, remote_filename)) > 0, f'empty file: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return

    def test_02_download__from_http_with_role(self):
        granule_json = '''{
      "numberMatched": 20,
      "numberReturned": 20,
      "stac_version": "1.0.0",
      "type": "FeatureCollection",
      "links": [
        {
          "rel": "self",
          "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"
        },
        {
          "rel": "root",
          "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com"
        },
        {
          "rel": "next",
          "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=100"
        },
        {
          "rel": "prev",
          "href": "https://58nbcawrvb.execute-api.us-west-2.amazonaws.com/test/am-uds-dapa/collections/SNDR_SNPP_ATMS_L1A___1/items?datetime=2016-01-14T08:00:00Z/2016-01-14T11:59:59Z&limit=100&offset=0"
        }
      ],
      "features": [
        {
          "type": "Feature",
          "stac_version": "1.0.0",
          "id": "SNDR.SNPP.ATMS.L1A.nominal2.01",
          "properties": {
            "start_datetime": "2016-01-14T09:54:00Z",
            "end_datetime": "2016-01-14T10:00:00Z",
            "created": "2020-12-14T13:50:00Z",
            "updated": "2022-08-15T06:26:39.830000Z",
            "datetime": "2022-08-15T06:26:37.029000Z"
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              0.0,
              0.0
            ]
          },
          "links": [
            {
              "rel": "collection",
              "href": "."
            }
          ],
          "assets": {
            "SNDR.SNPP.ATMS.L1A.nominal2.01.nc": {
              "href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/README.md",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc",
              "roles": [
                "data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas": {
              "href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.nc.cas",
              "roles": [
                "metadata__data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml": {
              "href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.01.cmr.xml",
              "roles": [
                "metadata__cmr"
              ]
            }
          },
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "stac_extensions": [],
          "collection": "SNDR_SNPP_ATMS_L1A___1"
        },
        {
          "type": "Feature",
          "stac_version": "1.0.0",
          "id": "SNDR.SNPP.ATMS.L1A.nominal2.08",
          "properties": {
            "start_datetime": "2016-01-14T10:36:00Z",
            "end_datetime": "2016-01-14T10:42:00Z",
            "created": "2020-12-14T13:50:00Z",
            "updated": "2022-08-15T06:26:26.078000Z",
            "datetime": "2022-08-15T06:26:19.333000Z"
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              0.0,
              0.0
            ]
          },
          "links": [
            {
              "rel": "collection",
              "href": "."
            }
          ],
          "assets": {
            "SNDR.SNPP.ATMS.L1A.nominal2.08.nc": {
              "href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CHANGELOG.md",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc",
              "roles": [
                "data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas": {
              "href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.nc.cas",
              "roles": [
                "metadata__data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml": {
              "href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.08.cmr.xml",
              "roles": [
                "metadata__cmr"
              ]
            }
          },
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "stac_extensions": [],
          "collection": "SNDR_SNPP_ATMS_L1A___1"
        },
        {
          "type": "Feature",
          "stac_version": "1.0.0",
          "id": "SNDR.SNPP.ATMS.L1A.nominal2.06",
          "properties": {
            "start_datetime": "2016-01-14T10:24:00Z",
            "end_datetime": "2016-01-14T10:30:00Z",
            "created": "2020-12-14T13:50:00Z",
            "updated": "2022-08-15T06:26:26.068000Z",
            "datetime": "2022-08-15T06:26:18.641000Z"
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              0.0,
              0.0
            ]
          },
          "links": [
            {
              "rel": "collection",
              "href": "."
            }
          ],
          "assets": {
            "SNDR.SNPP.ATMS.L1A.nominal2.06.nc": {
              "href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CODE_OF_CONDUCT.md",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc",
              "roles": [
                "data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas": {
              "href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.nc.cas",
              "roles": [
                "metadata__data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml": {
              "href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.06.cmr.xml",
              "roles": [
                "metadata__cmr"
              ]
            }
          },
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "stac_extensions": [],
          "collection": "SNDR_SNPP_ATMS_L1A___1"
        },
        {
          "type": "Feature",
          "stac_version": "1.0.0",
          "id": "SNDR.SNPP.ATMS.L1A.nominal2.18",
          "properties": {
            "start_datetime": "2016-01-14T11:36:00Z",
            "end_datetime": "2016-01-14T11:42:00Z",
            "created": "2020-12-14T13:50:00Z",
            "updated": "2022-08-15T06:26:26.060000Z",
            "datetime": "2022-08-15T06:26:19.698000Z"
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              0.0,
              0.0
            ]
          },
          "links": [
            {
              "rel": "collection",
              "href": "."
            }
          ],
          "assets": {
            "SNDR.SNPP.ATMS.L1A.nominal2.18.nc": {
              "href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/CONTRIBUTING.md",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc",
              "roles": [
                "data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas": {
              "href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.nc.cas",
              "roles": [
                "metadata__data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml": {
              "href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.18.cmr.xml",
              "roles": [
                "metadata__cmr"
              ]
            }
          },
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "stac_extensions": [],
          "collection": "SNDR_SNPP_ATMS_L1A___1"
        },
        {
          "type": "Feature",
          "stac_version": "1.0.0",
          "id": "SNDR.SNPP.ATMS.L1A.nominal2.04",
          "properties": {
            "start_datetime": "2016-01-14T10:12:00Z",
            "end_datetime": "2016-01-14T10:18:00Z",
            "created": "2020-12-14T13:50:00Z",
            "updated": "2022-08-15T06:26:26.050000Z",
            "datetime": "2022-08-15T06:26:19.491000Z"
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              0.0,
              0.0
            ]
          },
          "links": [
            {
              "rel": "collection",
              "href": "."
            }
          ],
          "assets": {
            "SNDR.SNPP.ATMS.L1A.nominal2.04.nc": {
              "href": "https://raw.githubusercontent.com/unity-sds/unity-data-services/develop/LICENSE",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc",
              "roles": [
                "data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas": {
              "href": "s3://uds-test-cumulus-protected/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.nc.cas",
              "roles": [
                "metadata__data"
              ]
            },
            "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml": {
              "href": "s3://uds-test-cumulus-private/SNDR_SNPP_ATMS_L1A___1/SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml",
              "title": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml",
              "description": "SNDR.SNPP.ATMS.L1A.nominal2.04.cmr.xml",
              "roles": [
                "metadata__cmr"
              ]
            }
          },
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "stac_extensions": [],
          "collection": "SNDR_SNPP_ATMS_L1A___1"
        }
      ]
    }'''
        granule_json = json.loads(granule_json)
        if len(argv) > 1:
            argv.pop(-1)
        argv.append('DOWNLOAD')
        os.environ['GRANULES_DOWNLOAD_TYPE'] = 'HTTP'
        os.environ['PARALLEL_COUNT'] = '3'
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ['OUTPUT_FILE'] = os.path.join(tmp_dir_name, 'some_output', 'output.json')
            granule_json_file = os.path.join(tmp_dir_name, 'input_file.json')
            downloading_dir = os.path.join(tmp_dir_name, 'downloading_dir')
            FileUtils.mk_dir_p(downloading_dir)
            FileUtils.write_json(granule_json_file, granule_json)
            os.environ['STAC_JSON'] = granule_json_file
            os.environ['DOWNLOAD_DIR'] = downloading_dir
            os.environ['DOWNLOADING_ROLES'] = 'data'
            download_result_str = choose_process()
            download_result = json.loads(download_result_str)
            self.assertTrue('features' in download_result, f'missing features in download_result')
            self.assertEqual(len(download_result['features']) + 1, len(glob(os.path.join(downloading_dir, '*'))),
                             f'downloaded file does not match: {download_result["features"]} v. {glob(os.path.join(downloading_dir, "*"))}')
            error_file = os.path.join(tmp_dir_name, 'error.log')
            if FileUtils.file_exist(error_file):
                self.assertTrue(False, f'some downloads failed. error.log exists. {FileUtils.read_json(error_file)}')
            download_result = download_result['features']
            self.assertTrue('assets' in download_result[0], f'no assets in download_result: {download_result}')
            downloaded_file_hrefs = set([list(k['assets'].values())[0]['href'] for k in download_result])
            for each_granule in zip(granule_json['features'], download_result):
                remote_filename = [k['href'] for k in each_granule[0]['assets'].values() if 'data' in k['roles']]
                remote_filename = os.path.basename(remote_filename[0])
                self.assertTrue(os.path.join('.', remote_filename) in downloaded_file_hrefs, f'mismatched: {remote_filename}')
                self.assertTrue(FileUtils.get_size(os.path.join(downloading_dir, remote_filename)) > 0, f'empty file: {remote_filename}')
            self.assertTrue(FileUtils.file_exist(os.environ['OUTPUT_FILE']), f'missing output file')
        return
