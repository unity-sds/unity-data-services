from cumulus_lambda_functions.lib.aws.factory_abstract import FactoryAbstract


class UDSAuthorizerFactory(FactoryAbstract):
    cognito = 'COGNITO'

    def get_instance(self, class_type, **kwargs):
        if class_type == self.cognito:
            from cumulus_lambda_functions.lib.authorization.uds_authorizer_es_identity_pool import \
                UDSAuthorizorEsIdentityPool
            return UDSAuthorizorEsIdentityPool(kwargs['es_url'], kwargs['es_port'])
        raise ValueError(f'class_type: {class_type} not implemented')
