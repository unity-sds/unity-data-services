import json
from urllib.parse import unquote

from cumulus_lambda_functions.lib.json_validator import JsonValidator


class AwsMessageTransformers:
    SQS_SCHEMA = {
        'type': 'object',
        'properties': {
            'Records': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 1,
                'items': {
                    'type': 'object',
                    'properties': {
                        'body': {'type': 'string', 'minLength': 1}
                    },
                    'required': ['body']
                }
            }
        },
        'required': ['Records']
    }
    SNS_EVENT_SCHEMA = {
        'type': 'object',
        'properties': {
            'Records': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 1,
                'items': {
                    'type': 'object',
                    'properties': {
                        'Sns': {'type': 'object'}
                    },
                    'required': ['Sns']
                }
            }
        },
        'required': ['Records']
    }

    SNS_SCHEMA = {
        "type": "object",
        "properties": {
            "Type": {"type": "string"},
            "MessageId": {"type": "string"},
            "TopicArn": {"type": "string"},
            # "Subject": {"type": "string"},
            "Timestamp": {"type": "string"},
            "SignatureVersion": {"type": "string"},
            "Signature": {"type": "string"},
            "SigningCertURL": {"type": "string"},
            "UnsubscribeURL": {"type": "string"},
            "Message": {"type": "string"},
        },
        "required": ["Message"]
    }

    S3_RECORD_SCHEMA = {
        'type': 'object',
        'properties': {'Records': {
            'type': 'array',
            'minItems': 1,
            'maxItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'eventName': {'type': 'string'},
                    's3': {
                        'type': 'object',
                        'properties': {
                            'bucket': {
                                'type': 'object',
                                'properties': {'name': {'type': 'string', 'minLength': 1}},
                                'required': ['name']
                            },
                            'object': {
                                'type': 'object',
                                'properties': {'key': {'type': 'string', 'minLength': 1}},
                                'required': ['key']
                            }},
                        'required': ['bucket', 'object']
                    }
                },
                'required': ['eventName', 's3']
            }
        }},
        'required': ['Records']
    }

    def sqs_sns(self, raw_msg: json):
        result = JsonValidator(self.SQS_SCHEMA).validate(raw_msg)
        if result is not None:
            raise ValueError(f'input json has SQS validation errors: {result}')
        sqs_msg_body = raw_msg['Records'][0]['body']
        sqs_msg_body = json.loads(sqs_msg_body)
        result = JsonValidator(self.SNS_SCHEMA).validate(sqs_msg_body)
        if result is not None:
            raise ValueError(f'input json has SNS validation errors: {result}')
        sns_msg_body = sqs_msg_body['Message']
        sns_msg_body = json.loads(sns_msg_body)
        return sns_msg_body

    def get_message_from_sns_event(self, raw_msg: json):
        result = JsonValidator(self.SNS_EVENT_SCHEMA).validate(raw_msg)
        if result is not None:
            raise ValueError(f'input json has SNS_EVENT_SCHEMA validation errors: {result}')
        sns_msg = raw_msg['Records'][0]['Sns']
        result = JsonValidator(self.SNS_SCHEMA).validate(sns_msg)
        if result is not None:
            raise ValueError(f'input json has SNS validation errors: {result}')
        sns_msg_body = sns_msg['Message']
        sns_msg_body = json.loads(sns_msg_body)
        return sns_msg_body

    def get_s3_from_sns(self, sns_msg_body):
        result = JsonValidator(self.S3_RECORD_SCHEMA).validate(sns_msg_body)
        if result is not None:
            raise ValueError(f'sns_msg_body did not pass S3_RECORD_SCHEMA: {result}')
        s3_summary = {
            'eventName': sns_msg_body['Records'][0]['eventName'],
            'bucket': sns_msg_body['Records'][0]['s3']['bucket']['name'],
            'key': unquote(sns_msg_body['Records'][0]['s3']['object']['key'].replace('+', ' ')),
        }
        return s3_summary