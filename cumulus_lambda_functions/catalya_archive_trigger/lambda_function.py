import json

from cumulus_lambda_functions.catalya_archive_trigger.catalya_archive_trigger import CatalyaArchiveTrigger
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator


def lambda_handler(event, context):
    """
    :param event:
    :param context:
    :return:
    """
    LambdaLoggerGenerator.remove_default_handlers()
    return CatalyaArchiveTrigger().start_with_event(event)
