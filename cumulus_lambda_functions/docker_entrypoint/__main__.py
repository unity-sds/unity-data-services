import logging
import os
from sys import argv

from mdps_ds_lib.stage_in_out.catalog_granules_factory import CatalogGranulesFactory
from mdps_ds_lib.stage_in_out.download_granules_factory import DownloadGranulesFactory
from mdps_ds_lib.stage_in_out.search_granules_factory import SearchGranulesFactory
from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils
from mdps_ds_lib.stage_in_out.upoad_granules_factory import UploadGranulesFactory


def choose_process():
    if argv[1].strip().upper() == 'SEARCH':
        logging.info('starting SEARCH script')
        result_str = SearchGranulesFactory().get_class(os.getenv('GRANULES_SEARCH_DOMAIN', 'MISSING_GRANULES_SEARCH_DOMAIN')).search()
        StageInOutUtils.write_output_to_file(result_str)
        return result_str
    if argv[1].strip().upper() == 'DOWNLOAD':
        logging.info('starting DOWNLOAD script')
        result_str = DownloadGranulesFactory().get_class(os.getenv('GRANULES_DOWNLOAD_TYPE', DownloadGranulesFactory.AMALGAMATION)).download()
        StageInOutUtils.write_output_to_file(result_str)
        return result_str
    if argv[1].strip().upper() == 'UPLOAD':
        logging.info('starting UPLOAD script')
        result_str = UploadGranulesFactory().get_class(os.getenv('GRANULES_UPLOAD_TYPE', UploadGranulesFactory.UPLOAD_S3_BY_STAC_CATALOG)).upload()
        StageInOutUtils.write_output_to_file(result_str)
        return result_str
    if argv[1].strip().upper() == 'CATALOG':
        logging.info('starting CATALOG script')
        result_str = CatalogGranulesFactory().get_class(os.getenv('GRANULES_CATALOG_TYPE', 'MISSING_GRANULES_CATALOG_TYPE')).catalog()
        StageInOutUtils.write_output_to_file(result_str)
        return result_str
    raise ValueError(f'invalid argument: {argv}')


if __name__ == '__main__':
    logging.basicConfig(level=int(os.environ.get('LOG_LEVEL', '10')),
                        format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")
    print(choose_process())
