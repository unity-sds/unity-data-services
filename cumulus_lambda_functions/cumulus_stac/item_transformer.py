import json
import os

from pystac import Item, Asset, Link
from pystac.utils import datetime_to_str

from cumulus_lambda_functions.cumulus_stac.stac_transformer_abstract import StacTransformerAbstract
from cumulus_lambda_functions.lib.json_validator import JsonValidator
from cumulus_lambda_functions.lib.time_utils import TimeUtils

STAC_ITEM_SCHEMA = '''{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json#",
    "title": "STAC Item",
    "type": "object",
    "description": "This object represents the metadata for an item in a SpatioTemporal Asset Catalog.",
    "allOf": [
        {
            "$ref": "#/definitions/core"
        }
    ],
    "definitions": {
        "common_metadata": {
            "allOf": [
                {
                    "$ref": "basics.json"
                },
                {
                    "$ref": "datetime.json"
                },
                {
                    "$ref": "instrument.json"
                },
                {
                    "$ref": "licensing.json"
                },
                {
                    "$ref": "provider.json"
                }
            ]
        },
        "core": {
            "allOf": [
                {
                    "$ref": "https://geojson.org/schema/Feature.json"
                },
                {
                    "oneOf": [
                        {
                            "type": "object",
                            "required": [
                                "geometry",
                                "bbox"
                            ],
                            "properties": {
                                "geometry": {
                                    "$ref": "https://geojson.org/schema/Geometry.json"
                                },
                                "bbox": {
                                    "type": "array",
                                    "oneOf": [
                                        {
                                            "minItems": 4,
                                            "maxItems": 4
                                        },
                                        {
                                            "minItems": 6,
                                            "maxItems": 6
                                        }
                                    ],
                                    "items": {
                                        "type": "number"
                                    }
                                }
                            }
                        },
                        {
                            "type": "object",
                            "required": [
                                "geometry"
                            ],
                            "properties": {
                                "geometry": {
                                    "type": "null"
                                },
                                "bbox": {
                                    "not": {}
                                }
                            }
                        }
                    ]
                },
                {
                    "type": "object",
                    "required": [
                        "stac_version",
                        "id",
                        "links",
                        "assets",
                        "properties"
                    ],
                    "properties": {
                        "stac_version": {
                            "title": "STAC version",
                            "type": "string",
                            "const": "1.0.0"
                        },
                        "stac_extensions": {
                            "title": "STAC extensions",
                            "type": "array",
                            "uniqueItems": true,
                            "items": {
                                "title": "Reference to a JSON Schema",
                                "type": "string",
                                "format": "iri"
                            }
                        },
                        "id": {
                            "title": "Provider ID",
                            "description": "Provider item ID",
                            "type": "string",
                            "minLength": 1
                        },
                        "links": {
                            "title": "Item links",
                            "description": "Links to item relations",
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/link"
                            }
                        },
                        "assets": {
                            "$ref": "#/definitions/assets"
                        },
                        "properties": {
                            "allOf": [
                                {
                                    "$ref": "#/definitions/common_metadata"
                                },
                                {
                                    "anyOf": [
                                        {
                                            "required": [
                                                "datetime"
                                            ],
                                            "properties": {
                                                "datetime": {
                                                    "not": {
                                                        "type": "null"
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "required": [
                                                "datetime",
                                                "start_datetime",
                                                "end_datetime"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "if": {
                        "properties": {
                            "links": {
                                "contains": {
                                    "required": [
                                        "rel"
                                    ],
                                    "properties": {
                                        "rel": {
                                            "const": "collection"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "then": {
                        "required": [
                            "collection"
                        ],
                        "properties": {
                            "collection": {
                                "title": "Collection ID",
                                "description": "The ID of the STAC Collection this Item references to.",
                                "type": "string",
                                "minLength": 1
                            }
                        }
                    },
                    "else": {
                        "properties": {
                            "collection": {
                                "not": {}
                            }
                        }
                    }
                }
            ]
        },
        "link": {
            "type": "object",
            "required": [
                "rel",
                "href"
            ],
            "properties": {
                "href": {
                    "title": "Link reference",
                    "type": "string",
                    "format": "iri-reference",
                    "minLength": 1
                },
                "rel": {
                    "title": "Link relation type",
                    "type": "string",
                    "minLength": 1
                },
                "type": {
                    "title": "Link type",
                    "type": "string"
                },
                "title": {
                    "title": "Link title",
                    "type": "string"
                }
            }
        },
        "assets": {
            "title": "Asset links",
            "description": "Links to assets",
            "type": "object",
            "additionalProperties": {
                "$ref": "#/definitions/asset"
            }
        },
        "asset": {
            "allOf": [
                {
                    "type": "object",
                    "required": [
                        "href"
                    ],
                    "properties": {
                        "href": {
                            "title": "Asset reference",
                            "type": "string",
                            "format": "iri-reference",
                            "minLength": 1
                        },
                        "title": {
                            "title": "Asset title",
                            "type": "string"
                        },
                        "description": {
                            "title": "Asset description",
                            "type": "string"
                        },
                        "type": {
                            "title": "Asset type",
                            "type": "string"
                        },
                        "roles": {
                            "title": "Asset roles",
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                },
                {
                    "$ref": "#/definitions/common_metadata"
                }
            ]
        }
    }
}'''


CUMULUS_FILE_SCHEMA = {
    "type": "object",
    "required": ["bucket", "key", "fileName", "type", ],
    "properties": {
        "bucket": {"type": "string"},
        "key": {"type": "string"},
        "fileName": {"type": "string"},
        "type": {"type": "string"},
    }
}


class ItemTransformer(StacTransformerAbstract):
    def __init__(self):
        super().__init__()
        self.__stac_item_schema = json.loads(STAC_ITEM_SCHEMA)
        self.__cumulus_granule_schema = {}
        self.CUMULUS_2_STAC_KEYS_MAP = {
            'beginningDateTime': 'start_datetime',
            'endingDateTime': 'end_datetime',
            'productionDateTime': 'created',
            'updatedAt': 'updated',
            'granuleId': 'id',
            'collectionId': 'collection',
        }
        self.STAC_2_CUMULUS_KEYS_MAP = {v: k for k, v in self.CUMULUS_2_STAC_KEYS_MAP.items()}

    def __get_asset_name(self, input_dict):
        return os.path.basename(input_dict['fileName'])
        # if input_dict['type'] == 'data':
        #     return 'data'
        # if input_dict['type'] == 'metadata':
        #     filename = input_dict['fileName'].upper().strip()
        #     if filename.endswith('.CMR.XML'):
        #         return 'metadata__cmr'
        #     if filename.endswith('.PDS.XML'):
        #         return 'metadata__xml'
        #     return 'metadata__data'
        # return input_dict['type']

    def __get_asset_obj(self, input_dict):
        """
      {
        "bucket": "uds-sbx-cumulus-staging",
        "checksum": "9817be382b87c48ebe482b9c47d1525a",
        "checksumType": "md5",
        "fileName": "test_file01.cmr.xml",
        "key": "URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.cmr.xml",
        "size": 1768,
        "source": "s3://uds-staging/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417/URN:NASA:UNITY:UDS_LOCAL_TEST:DEV:UDS_COLLECTION___2311091417:test_file01/test_file01.cmr.xml",
        "type": "metadata"
      }
        "bucket": "am-uds-dev-cumulus-internal",
        "key": "ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16032024518500.PDS",
        "size": 760,
        "fileName": "P1570515ATMSSCIENCEAAT16032024518500.PDS",
        "source": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/031//P1570515ATMSSCIENCEAAT16032024518500.PDS",
        "type": "data"

        :param input_dict:
        :return:
        """
        # https://github.com/stac-extensions/file
        # https://github.com/stac-extensions/file/blob/main/examples/item.json
        description_keys = ['size', 'checksumType', 'checksum']
        descriptions = [f'{k}={input_dict[k]};' for k in description_keys if k in input_dict]
        asset = Asset(
            href=f"s3://{input_dict['bucket']}/{input_dict['key']}",
            title=input_dict['fileName'],
            description=''.join(descriptions),
            extra_fields={
                'file:size': input_dict['size'] if 'size' in input_dict else -1,
                'file:checksum': input_dict['checksum'] if 'checksum' in input_dict else -1,
            },
            roles=[input_dict['type']]
        )
        return asset

    def to_stac(self, source: dict) -> dict:
        """
        Sample: Cumulus granule
        {
            "published": false,
            "endingDateTime": "2016-01-31T19:59:59.991043",
            "status": "completed",
            "timestamp": 1648050501578,
            "createdAt": 1648050499079,
            "processingEndDateTime": "2022-03-23T15:48:20.869Z",
            "productVolume": 18096656,
            "timeToPreprocess": 20.302,
            "timeToArchive": 0,
            "productionDateTime": "2016-02-01T02:45:59.639000Z",
            "execution": "https://console.aws.amazon.com/states/home?region=us-west-2#/executions/details/arn:aws:states:us-west-2:884500545225:execution:am-uds-dev-cumulus-IngestGranule:ec602ca7-0243-44df-adc0-28fb8a486d54",
            "files": [
                {
                    "bucket": "am-uds-dev-cumulus-internal",
                    "key": "ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16032024518500.PDS",
                    "size": 760,
                    "fileName": "P1570515ATMSSCIENCEAAT16032024518500.PDS",
                    "source": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/031//P1570515ATMSSCIENCEAAT16032024518500.PDS",
                    "type": "data"
                },
                {
                    "bucket": "am-uds-dev-cumulus-internal",
                    "key": "ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16032024518501.PDS",
                    "size": 18084600,
                    "fileName": "P1570515ATMSSCIENCEAAT16032024518501.PDS",
                    "source": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/031//P1570515ATMSSCIENCEAAT16032024518501.PDS",
                    "type": "metadata"
                },
                {
                    "bucket": "am-uds-dev-cumulus-internal",
                    "key": "ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16032024518501.PDS.xml",
                    "size": 9547,
                    "fileName": "P1570515ATMSSCIENCEAAT16032024518501.PDS.xml",
                    "source": "data/SNPP_ATMS_Level0_T/ATMS_SCIENCE_Group/2016/031//P1570515ATMSSCIENCEAAT16032024518501.PDS.xml",
                    "type": "metadata"
                },
                {
                    "bucket": "am-uds-dev-cumulus-internal",
                    "key": "ATMS_SCIENCE_Group___1/P1570515ATMSSCIENCEAAT16032024518500.PDS.cmr.xml",
                    "size": 1749,
                    "fileName": "P1570515ATMSSCIENCEAAT16032024518500.PDS.cmr.xml",
                    "type": "metadata"
                }
            ],
            "processingStartDateTime": "2022-03-23T15:45:03.732Z",
            "updatedAt": 1648050501578,
            "beginningDateTime": "2016-01-31T18:00:00.009057",
            "provider": "snpp_provider_03",
            "granuleId": "P1570515ATMSSCIENCEAAT16032024518500.PDS",
            "collectionId": "ATMS_SCIENCE_Group___001",
            "duration": 197.993,
            "error": {},
            "custom_metadata": {
                "custom_entry_1": "test1",
                "custom_entry_2": true,
                "custom_entry_3": 3.14159,
                "custom_entry_4": -20107,
            }
            "lastUpdateDateTime": "2018-04-25T21:45:45.524053"
        }
        :param source:
        :return:
        """

        validation_result = JsonValidator(self.__cumulus_granule_schema).validate(source)
        if validation_result is not None:
            raise ValueError(f'invalid cumulus granule json: {validation_result}')

        cumulus_file_validator = JsonValidator(CUMULUS_FILE_SCHEMA)
        validated_files = [k for k in source['files'] if cumulus_file_validator.validate(k) is None]
        custom_metadata = source['custom_metadata'] if 'custom_metadata' in source else {}

        properties_template = [
            {
                'stac_key': 'datetime',
                'cumulus_key': 'createdAt',
                'execution': lambda x: f"{TimeUtils.decode_datetime(x['createdAt'], False)}Z"
            },
            {
                'stac_key': 'start_datetime',
                'cumulus_key': 'beginningDateTime',
                'execution': lambda x: datetime_to_str(self.get_time_obj(x['beginningDateTime']))
            },
            {
                'stac_key': 'end_datetime',
                'cumulus_key': 'endingDateTime',
                'execution': lambda x: datetime_to_str(self.get_time_obj(x['endingDateTime']))
            },
            {
                'stac_key': 'created',
                'cumulus_key': 'productionDateTime',
                'execution': lambda x: datetime_to_str(self.get_time_obj(x['productionDateTime']))
            },
            {
                'stac_key': 'updated',
                'cumulus_key': 'updatedAt',
                'execution': lambda x: datetime_to_str(TimeUtils().parse_from_unix(source['updatedAt'], True).get_datetime_obj())
            },
            {
                'stac_key': 'status',
                'cumulus_key': 'status',
                'execution': lambda x: x['status']
            },
            {
                'stac_key': 'provider',
                'cumulus_key': 'provider',
                'execution': lambda x: x['provider']
            },
        ]
        cumulus_properties = {
            k['stac_key']: k['execution'](source) for k in properties_template if k['cumulus_key'] in source
        }
        stac_item = Item(
            id=source['granuleId'],
            stac_extensions=["https://stac-extensions.github.io/file/v2.1.0/schema.json"],
            bbox=[-180.0, -90.0, 180.0, 90.0],
            properties={
                **custom_metadata,
                **cumulus_properties,
                # "datetime": f"{TimeUtils.decode_datetime(source['createdAt'], False)}Z",
                # "start_datetime": datetime_to_str(self.get_time_obj(source['beginningDateTime'])),
                # "end_datetime": datetime_to_str(self.get_time_obj(source['endingDateTime'])),
                # "created": datetime_to_str(self.get_time_obj(source['productionDateTime'])),
                # "updated": datetime_to_str(TimeUtils().parse_from_unix(source['updatedAt'], True).get_datetime_obj()),
            },
            collection=source['collectionId'],
            assets={self.__get_asset_name(k): self.__get_asset_obj(k) for k in validated_files},
            geometry={
                "type": "Point",
                "coordinates": [0.0, 0.0]
            },
            datetime=TimeUtils().parse_from_unix(source['createdAt'], True).get_datetime_obj(),
        )
        stac_item.links = [
            Link(rel='collection', target='.')
        ]
        return stac_item.to_dict(include_self_link=False, transform_hrefs=False)

    def from_stac(self, source: dict) -> Item:
        return Item.from_dict(source)
