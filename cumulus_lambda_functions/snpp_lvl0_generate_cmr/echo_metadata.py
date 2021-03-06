
"""

sampleEcho10Granule = {
  Granule: {
    GranuleUR: 'MYD13Q1.A2017297.h19v10.006.2017313221202',
    InsertTime: '2018-04-25T21:45:45.524043',
    LastUpdate: '2018-04-25T21:45:45.524053',
    Collection: {
      ShortName: 'MYD13Q1',
      VersionId: '006',
    },
    DataGranule:
    {
      SizeMBDataGranule: '10',
      ReprocessingPlanned: 'The Reprocessing Planned Statement Value',
      ReprocessingActual: 'The Reprocessing Actual Statement Value',
      ProducerGranuleId: 'SMAP_L3_SM_P_20150407_R13080_001.h5',
      DayNightFlag: 'UNSPECIFIED',
      ProductionDateTime: '2018-07-19T12:01:01Z',
      LocalVersionId: 'LocalVersionIdValue',
    },
    Temporal: {
      RangeDateTime: {
        BeginningDateTime: '2017-10-24T00:00:00Z',
        EndingDateTime: '2017-11-08T23:59:59Z',
      },
    },
    Spatial: {
      HorizontalSpatialDomain: {
        Geometry: {
          GPolygon: {
            Boundary: {
              Point: [
                {
                  PointLongitude: '10.598766856250499',
                  PointLatitude: '-20.004533998735798',
                },
                {
                  PointLongitude: '10.116488181247300',
                  PointLatitude: '-9.963464459448231',
                },
                {
                  PointLongitude: '20.318223437416400',
                  PointLatitude: '-9.958850980581371',
                },
                {
                  PointLongitude: '21.290997939442398',
                  PointLatitude: '-19.999772984245801',
                },
              ],
            },
          },
        },
      },
    },
    // TwoDCoordinateSystem: {
    //   StartCoordinate1: '19',
    //   StartCoordinate2: '10',
    //   TwoDCoordinateSystemName: 'MODIS Tile SIN'
    // },
    OnlineAccessURLs: [{
      OnlineAccessURL: {
        URL: 'https://enjo7p7os7.execute-api.us-east-1.amazonaws.com/dev/MYD13Q1.A2017297.h19v10.006.2017313221202.hdf',
        URLDescription: 'Download MYD13Q1.A2017297.h19v10.006.2017313221202.hdf',
      },
    }],
    Orderable: 'true',
    Visible: 'true',
    CloudCover: '13',
  },
};
"""
from copy import deepcopy

from cumulus_lambda_functions.snpp_lvl0_generate_cmr.pds_metadata import PdsMetadata

SAMPLE_METADATA = {
    "GranuleUR": "MYD13Q1.A2017297.h19v10.006.2017313221202",
    "InsertTime": "2018-04-25T21:45:45.524043",
    "LastUpdate": "2018-04-25T21:45:45.524053",
    "Collection": {
        "ShortName": "MYD13Q1",
        "VersionId": "006"
    },
    "DataGranule": {
        "SizeMBDataGranule": "10",
        "ReprocessingPlanned": "The Reprocessing Planned Statement Value",
        "ReprocessingActual": "The Reprocessing Actual Statement Value",
        "ProducerGranuleId": "SMAP_L3_SM_P_20150407_R13080_001.h5",
        "DayNightFlag": "UNSPECIFIED",
        "ProductionDateTime": "2018-07-19T12:01:01Z",
        "LocalVersionId": "LocalVersionIdValue"
    },
    "Temporal": {
        "RangeDateTime": {
            "BeginningDateTime": "2017-10-24T00:00:00Z",
            "EndingDateTime": "2017-11-08T23:59:59Z"
        }
    },
    "Spatial": {
        "HorizontalSpatialDomain": {
            "Geometry": {
                "GPolygon": {
                    "Boundary": {
                        "Point": [
                            {
                                "PointLongitude": "10.598766856250499",
                                "PointLatitude": "-20.004533998735798"
                            },
                            {
                                "PointLongitude": "10.116488181247300",
                                "PointLatitude": "-9.963464459448231"
                            },
                            {
                                "PointLongitude": "20.318223437416400",
                                "PointLatitude": "-9.958850980581371"
                            },
                            {
                                "PointLongitude": "21.290997939442398",
                                "PointLatitude": "-19.999772984245801"
                            }
                        ]
                    }
                }
            }
        }
    },
    "OnlineAccessURLs": [
        {
            "OnlineAccessURL": {
                "URL": "https://enjo7p7os7.execute-api.us-east-1.amazonaws.com/dev/MYD13Q1.A2017297.h19v10.006.2017313221202.hdf",
                "URLDescription": "Download MYD13Q1.A2017297.h19v10.006.2017313221202.hdf"
            }
        }
    ],
    "Orderable": "true",
    "Visible": "true",
    "CloudCover": "13"
}


class EchoMetadata:
    def __init__(self, pds_metadata: PdsMetadata):
        self.__pds_metadata = pds_metadata
        self.__echo_metadata = deepcopy(SAMPLE_METADATA)

    @property
    def echo_metadata(self):
        return {'Granule': self.__echo_metadata}

    @echo_metadata.setter
    def echo_metadata(self, val):
        """
        :param val:
        :return: None
        """
        self.__echo_metadata = val
        return

    def load(self):
        incomplete_metadata = {
            'GranuleUR': self.__pds_metadata.granule_id,
            'InsertTime': self.__pds_metadata.insert_dt,
            # 'LastUpdate': 'TODO',
            'Collection': {
                'ShortName': self.__pds_metadata.collection_name,
                'VersionId': self.__pds_metadata.collection_version,
            },
            'DataGranule': {
                'ProductionDateTime': self.__pds_metadata.prod_dt,
            },
            'Temporal': {
                'RangeDateTime': {
                    'BeginningDateTime': self.__pds_metadata.beginning_dt,
                    'EndingDateTime': self.__pds_metadata.ending_dt,
                }
            }
        }
        self.__echo_metadata.update(incomplete_metadata)
        return self
