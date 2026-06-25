import os

from mdps_ds_lib.lib.utils.json_validator import JsonValidator

from cumulus_lambda_functions.daac_archiver.cnm_plugins.cnm_plugin_abstract import CnmPluginAbstract
from cumulus_lambda_functions.daac_archiver.services.status_update_svc import StatusUpdateSvc


class CnmStatusUpdatePlugin(CnmPluginAbstract):
    CNM_RESPONSE_MSG_SCHEMA = {
        'type': 'object',
        'required': ['identifier', 'response'],
        'properties': {
            'identifier': {'type': 'string'},
            'response': {
                'type': 'object',
                'required': ['status'],
                'properties': {
                    'status': {'type': 'string'},
                },
            },
        }
    }

    def __init__(self, params: dict):
        super().__init__(params)
        required_params = [self.cnm_notification_msg]
        if not all([k in self._params for k in required_params]):
            raise ValueError(f'missing required params: {required_params} v. {self._params}')

    def run(self):
        required_params = [self.sending_id, self.collection_id, self.granule_id, self.target_collection_id]
        if all([k in self._params for k in required_params]):
            update_status_svc = StatusUpdateSvc().load_manually(self._params[self.sending_id],
                                                                self._params[self.collection_id],
                                                                self._params[self.target_collection_id],
                                                                self._params[self.granule_id])

            update_status_svc.update_status(self._params[self.cnm_notification_msg])
            return self
        result = JsonValidator(self.CNM_RESPONSE_MSG_SCHEMA).validate(self._params[self.cnm_notification_msg])
        if result is not None:
            raise ValueError(f'input json has CNM_RESPONSE_MSG_SCHEMA validation errors: {result}')
        dac = StatusUpdateSvc()
        dac.update_status_wrapper(self._params[self.cnm_notification_msg])
        return self
