import os

from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract


class UDSAuthorizerFactory(FactoryAbstract):
    cognito = 'COGNITO'

    def get_instance(self, class_type, **kwargs):
        if 'use_ssl' not in kwargs:
            kwargs['use_ssl'] = os.getenv('ES_USE_SSL', 'TRUE').strip() is True
        if 'es_type' not in kwargs:
            kwargs['es_type'] = os.getenv('ES_TYPE', 'AWS')
        if class_type == self.cognito:
            from cumulus_lambda_functions.lib.authorization.uds_authorizer_es_identity_pool import \
                UDSAuthorizorEsIdentityPool
            return UDSAuthorizorEsIdentityPool(kwargs['es_url'], kwargs['es_port'], kwargs['es_type'], kwargs['use_ssl'])
        raise ValueError(f'class_type: {class_type} not implemented')
