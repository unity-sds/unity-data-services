import json
from urllib.parse import quote_plus

from cumulus_lambda_functions.cumulus_stac.stac_transformer_abstract import StacTransformerAbstract

STAC_COLLECTION_SCHEMA = '''{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json#",
    "title": "STAC Collection Specification",
    "description": "This object represents Collections in a SpatioTemporal Asset Catalog.",
    "allOf": [
        {
            "$ref": "#/definitions/collection"
        }
    ],
    "definitions": {
        "collection": {
            "title": "STAC Collection",
            "description": "These are the fields specific to a STAC Collection. All other fields are inherited from STAC Catalog.",
            "type": "object",
            "required": [
                "stac_version",
                "type",
                "id",
                "description",
                "license",
                "extent",
                "links"
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
                "type": {
                    "title": "Type of STAC entity",
                    "const": "Collection"
                },
                "id": {
                    "title": "Identifier",
                    "type": "string",
                    "minLength": 1
                },
                "title": {
                    "title": "Title",
                    "type": "string"
                },
                "description": {
                    "title": "Description",
                    "type": "string",
                    "minLength": 1
                },
                "keywords": {
                    "title": "Keywords",
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "license": {
                    "title": "Collection License Name",
                    "type": "string",
                    "pattern": "^[\\\\w\\\\-\\\\.\\\\+]+$"
                },
                "providers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "name"
                        ],
                        "properties": {
                            "name": {
                                "title": "Organization name",
                                "type": "string"
                            },
                            "description": {
                                "title": "Organization description",
                                "type": "string"
                            },
                            "roles": {
                                "title": "Organization roles",
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "producer",
                                        "licensor",
                                        "processor",
                                        "host"
                                    ]
                                }
                            },
                            "url": {
                                "title": "Organization homepage",
                                "type": "string",
                                "format": "iri"
                            }
                        }
                    }
                },
                "extent": {
                    "title": "Extents",
                    "type": "object",
                    "required": [
                        "spatial",
                        "temporal"
                    ],
                    "properties": {
                        "spatial": {
                            "title": "Spatial extent object",
                            "type": "object",
                            "required": [
                                "bbox"
                            ],
                            "properties": {
                                "bbox": {
                                    "title": "Spatial extents",
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "title": "Spatial extent",
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
                            }
                        },
                        "temporal": {
                            "title": "Temporal extent object",
                            "type": "object",
                            "required": [
                                "interval"
                            ],
                            "properties": {
                                "interval": {
                                    "title": "Temporal extents",
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "title": "Temporal extent",
                                        "type": "array",
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": {
                                            "type": [
                                                "string",
                                                "null"
                                            ],
                                            "format": "date-time",
                                            "pattern": "(\\\\+00:00|Z)$"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "assets": {
                    "$ref": "../../item-spec/json-schema/item.json#/definitions/assets"
                },
                "links": {
                    "title": "Links",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/link"
                    }
                },
                "summaries": {
                    "$ref": "#/definitions/summaries"
                }
            }
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
        "summaries": {
            "type": "object",
            "additionalProperties": {
                "anyOf": [
                    {
                        "title": "JSON Schema",
                        "type": "object",
                        "minProperties": 1,
                        "allOf": [
                            {
                                "$ref": "http://json-schema.org/draft-07/schema"
                            }
                        ]
                    },
                    {
                        "title": "Range",
                        "type": "object",
                        "required": [
                            "minimum",
                            "maximum"
                        ],
                        "properties": {
                            "minimum": {
                                "title": "Minimum value",
                                "type": [
                                    "number",
                                    "string"
                                ]
                            },
                            "maximum": {
                                "title": "Maximum value",
                                "type": [
                                    "number",
                                    "string"
                                ]
                            }
                        }
                    },
                    {
                        "title": "Set of values",
                        "type": "array",
                        "minItems": 1
                    }
                ]
            }
        }
    }
}'''
# The following lines are a part of summaries > additionalProperties > oneOf > [last item].
# But including that will not make it a valid schema.
# excluding it for now
# "items": {
#     "description": "For each field only the original data type of the property can occur (except for arrays), but we can't validate that in JSON Schema yet. See the sumamry description in the STAC specification for details."
# }


class CollectionTransformer(StacTransformerAbstract):
    def __init__(self):
        self.__stac_collection_schema = json.loads(STAC_COLLECTION_SCHEMA)
        self.__cumulus_collection_schema = {}

    def __convert_to_stac_links(self, collection_file_obj: dict):
        """
        expected output
        {
          "title": "<sampleFileName>",
          "href": "<bucket>___<regex>"
          "type": "<type>",
          "rel": "item"
        }

        Sample input:
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                }
        TODO: missing reportToEms
        :param collection_file_obj:
        :return: dict
        """
        if collection_file_obj is None:
            return {}
        stac_link = {
            'rel': 'item',
        }
        if 'type' in collection_file_obj:
            stac_link['type'] = collection_file_obj['type']
        if 'sampleFileName' in collection_file_obj:
            stac_link['title'] = collection_file_obj['sampleFileName']
        href_link = ['unknown_bucket', 'unknown_regex']
        if 'bucket' in collection_file_obj:
            href_link[0] = collection_file_obj['bucket']
        if 'regex' in collection_file_obj:
            href_link[1] = collection_file_obj['regex']
        stac_link['href'] = f"./collection.json?bucket={href_link[0]}&regex={quote_plus(href_link[1])}"
        return stac_link

    def to_stac(self, source: dict) -> dict:
        source_sample = {
            "createdAt": 1647992847582,
            "granuleId": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$",
            "process": "modis",
            "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
            "name": "ATMS_SCIENCE_Group",
            "files": [
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS\\.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS.xml",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00.PDS.cmr.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml",
                    "reportToEms": True,
                    "type": "metadata"
                }
            ],
            "granuleIdExtraction": "(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+",
            "reportToEms": True,
            "version": "001",
            "duplicateHandling": "replace",
            "updatedAt": 1647992847582,
            "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}",
            "timestamp": 1647992849273
        }
        stac_collection = {
            "type": "Collection",
            "stac_version": "1.0.0",
            # "stac_extensions": [],
            "id": f"{source['name']}___{source['version']}",
            "description": "TODO",
            "license": "proprietary",
            # "keywords": [],
            "providers": [],
            "extent": {
                "spatial": {
                    "bbox": [[0, 0, 0, 0]]
                },
                "temporal": {
                    "interval": [[source['dateFrom'] if 'dateFrom' in source else None,
                                 source['dateTo'] if 'dateTo' in source else None
                                  ]]
                }
            },
            "assets": {},
            "summaries": {
                "granuleId": [source['granuleId'] if 'granuleId' in source else ''],
                "granuleIdExtraction": [source['granuleIdExtraction'] if 'granuleIdExtraction' in source else ''],
                "process": [source['process'] if 'process' in source else ''],
                "totalGranules": [source['total_size'] if 'total_size' in source else -1],
            },
            "links": [{
                        "rel": "root",
                        "type": "application/json",
                        "title": f"{source['name']}___{source['version']}",
                        "href": "./collection.json"
                    }] + [self.__convert_to_stac_links(k) for k in source['files']],
        }
        return stac_collection

    def from_stac(self, source: dict) -> dict:
        return {}
