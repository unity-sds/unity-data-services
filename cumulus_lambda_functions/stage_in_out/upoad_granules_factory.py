

class UploadGranulesFactory:
    UPLOAD_S3_BY_STAC_CATALOG = 'UPLOAD_S3_BY_STAC_CATALOG'
    UPLOAD_AUXILIARY_FILE_AS_GRANULE = 'UPLOAD_AUXILIARY_FILE_AS_GRANULE'

    def get_class(self, upload_type):
        if upload_type == UploadGranulesFactory.UPLOAD_S3_BY_STAC_CATALOG:
            from cumulus_lambda_functions.stage_in_out.upload_granules_by_complete_catalog_s3 import UploadGranulesByCompleteCatalogS3
            return UploadGranulesByCompleteCatalogS3()
        if upload_type == UploadGranulesFactory.UPLOAD_AUXILIARY_FILE_AS_GRANULE:
            from cumulus_lambda_functions.stage_in_out.upload_arbitrary_files_as_granules import UploadArbitraryFilesAsGranules
            return UploadArbitraryFilesAsGranules()
        raise ValueError(f'unknown search_type: {upload_type}')
