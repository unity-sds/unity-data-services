

class DownloadGranulesFactory:
    S3 = 'S3'
    HTTP = 'HTTP'
    DAAC = 'DAAC'

    def get_class(self, search_type):
        if search_type == DownloadGranulesFactory.S3:
            from cumulus_lambda_functions.stage_in_out.download_granules_s3 import DownloadGranulesS3
            return DownloadGranulesS3()
        elif search_type == DownloadGranulesFactory.DAAC:
            from cumulus_lambda_functions.stage_in_out.download_granules_daac import DownloadGranulesDAAC
            return DownloadGranulesDAAC()
        elif search_type == DownloadGranulesFactory.HTTP:
            from cumulus_lambda_functions.stage_in_out.download_granules_http import DownloadGranulesHttp
            return DownloadGranulesHttp()
        raise ValueError(f'unknown search_type: {search_type}')
