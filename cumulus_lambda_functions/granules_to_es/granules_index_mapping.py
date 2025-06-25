class GranulesIndexMapping:
    archiving_keys = [
        'archive_status', 'archive_error_message', 'archive_error_code'
    ]
    percolator_mappings = {
        "daac_collection_name": {
            "type": "keyword"
        },
        "daac_data_version": {
            "type": "keyword"
        },
        "daac_provider": {
            "type": "keyword"
        },
        "daac_role_arn": {
            "type": "keyword"
        },
        "daac_role_session_name": {
            "type": "keyword"
        },
        "archiving_types": {
            "type": "object",
            "properties": {
                "data_type": {"type": "keyword"},
                "file_extension": {"type": "keyword"},
            }
        },
        "daac_sns_topic_arn": {
            "type": "keyword"
        },
        "ss_query": {
            "type": "percolator"
        },
        "ss_username": {
            "type": "keyword"
        },
    }
    stac_mappings = {
        "archive_status": {"type": "keyword"},
        "archive_error_message": {"type": "text"},
        "archive_error_code": {"type": "keyword"},

        "event_time": {"type": "long"},
        "type": {"type": "keyword"},
        "stac_version": {"type": "keyword"},
        "id": {"type": "keyword"},
        "collection": {"type": "keyword"},
        "geometry": {"type": "geo_shape"},
        "bbox": {"type": "geo_shape"},
        "links": {
            "type": "object",
            "properties": {
                "href": {"type": "keyword"},
                "rel": {"type": "keyword"},
                "type": {"type": "keyword"},
                "title": {"type": "text"}
            }
        },
        "stac_extensions": {"type": "keyword"},
        "properties": {
            "dynamic": "false",
            "properties": {
                "provider": {"type": "keyword"},
                "status": {"type": "keyword"},
                "datetime": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"},
                "updated": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"},
                "start_datetime": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"},
                "end_datetime": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"},
                "created": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd||epoch_millis"},
            },
        },
        "assets": {
            "type": "object",
            "dynamic": False,
        }
    }
    mappings = {
        "eventTime": {"type": "long"},
        "collectionId": {"type": "keyword"},
        "createdAt": {"type": "long"},
        "duration": {"type": "float"},
        "error": {
            "type": "object",
            "properties": {
                "Cause": {"type": "text"},
                "Error": {"type": "text"}
            }
        },
        "execution": {"type": "text"},
        "granuleId": {"type": "keyword"},
        "processingEndDateTime": {"type": "date"},
        "processingStartDateTime": {"type": "date"},
        "productVolume": {"type": "keyword"},
        "provider": {"type": "keyword"},
        "published": {"type": "boolean"},
        "status": {"type": "keyword"},
        "timestamp": {"type": "long"},
        "timeToArchive": {"type": "float"},
        "timeToPreprocess": {"type": "float"},
        "updatedAt": {"type": "long"},
        "files": {
            "type": "object",
            "properties": {
                "bucket": {"type": "keyword"},
                "checksum": {"type": "keyword"},
                "checksumType": {"type": "keyword"},
                "fileName": {"type": "keyword"},
                "key": {"type": "keyword"},
                "size": {"type": "integer"},
                "source": {"type": "text"},
                "type":{"type": "keyword"}
            }
        },
        "beginningDateTime": {"type": "date"},
        "endingDateTime": {"type": "date"},
        "lastUpdateDateTime": {"type": "date"},
        "productionDateTime": {"type": "date"},
    }
