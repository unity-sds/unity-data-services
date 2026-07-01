from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract

from cumulus_lambda_functions.daac_archiver.raw_cnm_storage.raw_cnm_storage_abstract import RawCnmStorageAbstract


class RawCnmStorageFactory(FactoryAbstract):
    AWS = 'S3'
    POSTGRES = 'POSTGRES'
    OPENSEARCH = 'OPENSEARCH'

    def get_instance_from_dict(self, env_dict: dict, **kwargs):
        raise NotImplementedError('not a need yet')

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError('Not Yet')

    def get_instance(self, file_repo, **kwargs) -> RawCnmStorageAbstract:
        fr = file_repo.upper()
        if fr == self.AWS:
            from cumulus_lambda_functions.daac_archiver.raw_cnm_storage.raw_cnm_storage_s3 import RawCnmStorageS3
            return RawCnmStorageS3()
        raise ModuleNotFoundError(f'cannot find RawCnmStorage class for {fr}')