import json
import unittest
import datetime

from bson.objectid import ObjectId

from common.service_access.utilities.json_helpers import APIEncoder
from geoprocessing.business_logic.business_objects.address import Address
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.geoprocessors.demographics.gp7_core_trade_area_geo_processor import GP7CoreTradeAreaDemographics
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from geoprocessing.helpers.postgis_calculator import GISCalculator


class GP7Tests(unittest.TestCase):

    """
    Note : A significant portion of these tests are very similar to the GP1 tests. We need to make sure that GP7
           covers the same ground where intended, and diverges where intended.
    """
    def setUp(self):

        # set up mock dependencies
        register_mock_dependencies()
        self.__rest_provider = Dependency("RestProvider").value
        self.__postgres_provider = Dependency('PostgresDataRepository').value
        self.__main_access = Dependency('CoreAPIProvider').value

        self.config = Dependency("Config").value
        self._dataset_year = self.config.dataset_year

        # update configs to match what we're testing
        self.config.gp1_templates = ["Demographic and Income Profile", "Nexus Age by Sex Report", "Automotive Aftermarket Expenditures"]

        # the trade area we'll be testing against
        self._test_trade_area = {
            '_id': ObjectId(),
            'data': {
                'store_id': ObjectId(),
                'trade_area_threshold': 'DistanceMiles10',
                'company_id': ObjectId(),
                'longitude': 1.0,
                'latitude': -1.0
            }
        }

        # the a pre-exiting trade area we'll be testing against
        self._test_trade_area_preexisting = {
            '_id': ObjectId(),
            'data': {
                'store_id': ObjectId(),
                'trade_area_threshold': 'DistanceMiles10',
                'company_id': ObjectId(),
                'longitude': 1.0,
                'latitude': -1.0,
                'demographics': {
                    'chicken': {
                        'value': 3,
                        'description': 'chickens...chickens everywhere'
                    },
                    'woot': {
                        'value': 33,
                        'description': 'make rocket go now'
                    }
                },
                'analytics': {
                    'shape': {
                        'surface_area': 55,
                        'shape_array': [1, 1]
                    }
                }
            }
        }

        self._expected_store = Store()
        self._expected_store.store_id = self._test_trade_area['data']['store_id']
        self._expected_store.company_id = self._test_trade_area['data']['company_id']

        self._expected_store.address = Address()
        self._expected_store.address.longitude = self._test_trade_area['data']['longitude']
        self._expected_store.address.latitude = self._test_trade_area['data']['latitude']



    def tearDown(self):
        dependencies.clear()


    # ____________________________________________ Test Initialization _______________________________________________ #
    def test_initialization(self):

        gp7_processor = GP7CoreTradeAreaDemographics()
        gp7_processor._entity = self._test_trade_area

        gp7_processor._initialize()

        # make sure the values are initialized correctly
        self.assertEqual(gp7_processor._store, self._expected_store)
        self.assertEqual(gp7_processor._threshold_id, 1)


    # __________________________________________ Test Get GIS Drive Times ____________________________________________ #
    def test_get_GIS_data_drive_time(self):
        """
        Almost exactly the same as GP1 - we want to make sure that they cover the same grounds when getting GIS data.
        """
        self.__rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'

        gp7_processor = GP7CoreTradeAreaDemographics()
        self._test_trade_area['data']['trade_area_threshold'] = 'DriveTimeMinutes10'
        gp7_processor._entity = self._test_trade_area

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()

        #create expected format
        #create expected response
        self.maxDiff = None
        points_json_format = json.dumps(
            {
                "Points":[
                    {
                        "longitude": self._expected_store.address.longitude,
                        "description": str(self._expected_store.store_id),
                        "latitude":self._expected_store.address.latitude,
                        "name": str(self._expected_store.store_id),
                        "storeID": self._expected_store.store_id,
                        "storeAddress": str(self._expected_store.store_id)
                    }
                ],
                "spatialReference": {"wkid": 4326}
            }, cls = APIEncoder)
        report_options = json.dumps([
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Demographic and Income Profile",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            },
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Nexus Age by Sex Report",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            },
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Automotive Aftermarket Expenditures",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            }
        ])
        expected_request_format = {
            'Stores': points_json_format,
            'Radii': "10",
            'DistanceUnits': "esriDriveTimeUnitsMinutes",
            'ActiveDatasetID': 'USA_ESRI_2011',
            'CreateDetailedBorder': 'true',
            'DetailedDriveTimes': 'true',
            'OutputSpatialReference': '{"wkid": 4326}',
            'ReportOptions': report_options,
            'OutputType': 'GetReport;GetFeatureClass',
            'f': 'JSON'
        }

        # make sure response has the right request for the drive time report
        self.assertEqual(gp7_processor._response.request, expected_request_format)


    # __________________________________________ Test Get GIS Simple Rings____________________________________________ #
    def test_get_GIS_data_simple_rings(self):
        """
        Test that gp1 calls the correct rest mocked method for the simple_rings complexity
        """
        self.__rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        gp7_processor = GP7CoreTradeAreaDemographics()
        self._test_trade_area['data']['trade_area_threshold'] = 'DistanceMiles10'
        gp7_processor._entity = self._test_trade_area

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()

        # create expected format
        points_json_format = json.dumps({
                                            "Points":[
                                                {
                                                    "longitude": self._expected_store.address.longitude,
                                                    "description": str(self._expected_store.store_id),
                                                    "latitude":self._expected_store.address.latitude,
                                                    "name": str(self._expected_store.store_id),
                                                    "storeID": self._expected_store.store_id,
                                                    "storeAddress": str(self._expected_store.store_id)
                                                }
                                            ],
                                            "spatialReference": {"wkid": 4326}
                                        }, cls = APIEncoder)

        report_options = json.dumps([
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Demographic and Income Profile",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            },
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Nexus Age by Sex Report",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            },
            {
                "ReportFormat":"s.xml",
                "TemplateName":"Automotive Aftermarket Expenditures",
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            }
        ])
        expected_request_format = {
            'Stores': points_json_format,
            'Radii': "10",
            'DistanceUnits': "esriMiles",
            'ActiveDatasetID': 'USA_ESRI_2011',
            'OutputSpatialReference': '{"wkid": 4326}',
            'ReportOptions': report_options,
            'OutputType': 'GetReport;GetFeatureClass',
            'f': 'JSON'
        }
        self.maxDiff = None
        # make sure response has the right request for the drive time report
        self.assertEqual(gp7_processor._response.request, expected_request_format)


    # __________________________________________ Test Processing of Data _____________________________________________ #
    def test_process_GIS_data_new_trade_area(self):
        """
        Test that gp1 parses the response and creates demographics for a new trade area
        """

        geoshape_calculator = GISCalculator()

        wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)'

        self.__postgres_provider.shape_areas = {wkt_representation: 4}
        self.__postgres_provider.shape_centroids = {wkt_representation: 'POINT(0 0)'}
        self.__postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(wkt_representation)): 1}

        self.__rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        gp7_processor = GP7CoreTradeAreaDemographics()
        gp7_processor._entity = self._test_trade_area
        gp7_processor._period_year = 2013

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()
        gp7_processor._preprocess_data_for_save()

        # verify initial shape parsing
        self.assertEqual(gp7_processor._trade_area_wkt_representation_linestring, 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')
        self.assertEqual(gp7_processor._trade_area_shape_array_representation, [[[1, 1], [-1, 1], [-1, -1], [1, -1]]])

        # verify demographics
        expected_demographics = {
            'TOTPOP_CY': {
                'target_year': 2011,
                'description': '2055 Total Population',
                'value': 2.2
            },
            'PCI_CY': {
                'target_year': 2011,
                'description': 'PCI',
                'value': 2
            },
            'ROB': {
                'target_year': 2011,
                'description': 'MALE 18-25',
                'value': 1010101010.0
            }
        }


        self.assertEqual(gp7_processor._entity['data']['demographics'], expected_demographics)

        # verify period information
        self.assertEqual(gp7_processor._entity['data']['period_duration'], 'year')
        self.assertEqual(gp7_processor._entity['data']['period_start_date'], datetime.datetime(2013, 1, 1).date())
        self.assertEqual(gp7_processor._entity['data']['period_end_date'], datetime.datetime(2013, 12, 31).date())

        # verify analytics

        expected_analytics = {
            'shape': {
                'surface_area': 4,
                'shape_array': [[[1, 1], [-1, 1], [-1, -1], [1, -1]]],
                'centroid': {
                    'longitude': 0.000000,
                    'latitude': 0.000000
                },
                'UTM_zone': '31N'
            },
            'AGG_INCOME_CY': {
                'description': 'Aggregate Income',
                'target_year': 2011,
                'value': 4.4
            }
        }

        self.assertEqual(gp7_processor._entity['data']['analytics'], expected_analytics)

    def test_process_GIS_data_preexisting_trade_area(self):
        """
        Test that gp1 parses the response and UPDATES demographics for a preexisting trade_area
        """

        geoshape_calculator = GISCalculator()

        wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)'

        self.__postgres_provider.shape_areas = {wkt_representation: 4}
        self.__postgres_provider.shape_centroids = {wkt_representation: 'POINT(0 0)'}
        self.__postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(wkt_representation)): 1}

        self.__rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        gp7_processor = GP7CoreTradeAreaDemographics()
        gp7_processor._entity = self._test_trade_area_preexisting
        gp7_processor._period_year = 2013

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()
        gp7_processor._preprocess_data_for_save()

        # verify initial shape parsing
        self.assertEqual(gp7_processor._trade_area_wkt_representation_linestring, 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')
        self.assertEqual(gp7_processor._trade_area_shape_array_representation, [[[1, 1], [-1, 1], [-1, -1], [1, -1]]])

        # verify demographics
        expected_demographics = {
            'TOTPOP_CY': {
                'target_year': 2011,
                'description': '2055 Total Population',
                'value': 2.2
            },
            'PCI_CY': {
                'target_year': 2011,
                'description': 'PCI',
                'value': 2
            },
            'ROB': {
                'target_year': 2011,
                'description': 'MALE 18-25',
                'value': 1010101010.0
            },
            'chicken': {
                'value': 3,
                'description': 'chickens...chickens everywhere'
            },
            'woot': {
                'value': 33,
                'description': 'make rocket go now'
            }
        }


        self.assertEqual(gp7_processor._entity['data']['demographics'], expected_demographics)

        # verify period information
        self.assertEqual(gp7_processor._entity['data']['period_duration'], 'year')
        self.assertEqual(gp7_processor._entity['data']['period_start_date'], datetime.datetime(2013, 1, 1).date())
        self.assertEqual(gp7_processor._entity['data']['period_end_date'], datetime.datetime(2013, 12, 31).date())

        # verify analytics

        expected_analytics = {

            'shape': {
                'surface_area': 4,
                'shape_array': [[[1, 1], [-1, 1], [-1, -1], [1, -1]]],
                'centroid': {
                    'longitude': 0.000000,
                    'latitude': 0.000000
                },
                'UTM_zone': '31N'
            },
            'AGG_INCOME_CY': {
                'description': 'Aggregate Income',
                'target_year': 2011,
                'value': 4.4
            }
        }

        self.assertEqual(gp7_processor._entity['data']['analytics'], expected_analytics)

    # _____________________________________________ Test Saving of Data ______________________________________________ #
    def test_save_processed_data_new_trade_area(self):
        """
        Test that gp7 calls MDS update on the right fields for a new trade area
        """

        geoshape_calculator = GISCalculator()
        wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)'

        self.__postgres_provider.shape_areas = {wkt_representation: 4}
        self.__postgres_provider.shape_centroids = {wkt_representation: 'POINT(0 0)'}
        self.__postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(wkt_representation)): 1}

        self.__rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        # create an empty entity keyed under the trade area id just to track the updates. we only want to update 4 things here.
        self.__main_access.mds.entities = {
            'trade_area': {
                self._test_trade_area['_id']: {}
            }
        }

        gp7_processor = GP7CoreTradeAreaDemographics()
        gp7_processor._entity = self._test_trade_area
        gp7_processor._period_year = 2013

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()
        gp7_processor._preprocess_data_for_save()



        gp7_processor._save_processed_data()

        updated_entity = self.__main_access.mds.entities['trade_area'][self._test_trade_area['_id']]


        self.assertEqual(len(updated_entity.keys()), 2)
        self.assertEqual(updated_entity['data.demographics'], gp7_processor._entity['data']['demographics'])
        self.assertEqual(updated_entity['data.analytics'], gp7_processor._entity['data']['analytics'])

    def test_save_processed_data_preexisting_trade_area(self):
        """
        Test that gp7 calls MDS update on the right fields for a preexisting trade area
        """

        geoshape_calculator = GISCalculator()
        wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)'

        self.__postgres_provider.shape_areas = {wkt_representation: 4}
        self.__postgres_provider.shape_centroids = {wkt_representation: 'POINT(0 0)'}
        self.__postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(wkt_representation)): 1}

        self.__rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        # create an empty entity keyed under the trade area id just to track the updates. we only want to update 4 things here.
        self.__main_access.mds.entities = {
            'trade_area': {
                self._test_trade_area_preexisting['_id']: {}
            }
        }

        gp7_processor = GP7CoreTradeAreaDemographics()
        gp7_processor._entity = self._test_trade_area_preexisting
        gp7_processor._period_year = 2013

        gp7_processor._initialize()
        gp7_processor._do_geoprocessing()
        gp7_processor._preprocess_data_for_save()



        gp7_processor._save_processed_data()

        updated_entity = self.__main_access.mds.entities['trade_area'][self._test_trade_area_preexisting['_id']]

        # expected update format
        expected_updated_data_fields = {
            'data.demographics.TOTPOP_CY': {
                'target_year': 2011,
                'description': '2055 Total Population',
                'value': 2.2
            },
            'PCI_CY': {
                'target_year': 2011,
                'description': 'PCI',
                'value': 2
            },
            'data.demographics.ROB': {
                'target_year': 2011,
                'description': 'MALE 18-25',
                'value': 1010101010.0
            }
        }

        # expected demographics
        expected_demographics = {
            'TOTPOP_CY': {
                'target_year': 2011,
                'description': '2055 Total Population',
                'value': 2.2
            },
            'PCI_CY': {
                'target_year': 2011,
                'description': 'PCI',
                'value': 2
            },
            'ROB': {
                'target_year': 2011,
                'description': 'MALE 18-25',
                'value': 1010101010.0
            },
            'chicken': {
                'value': 3,
                'description': 'chickens...chickens everywhere'
            },
            'woot': {
                'value': 33,
                'description': 'make rocket go now'
            }
        }

        # check demographics
        self.assertEqual(gp7_processor._entity['data']['demographics'], expected_demographics)

        # check updates - only the three new demographics go into the updates, plus all the analytics
        self.assertEqual(len(updated_entity.keys()), 5)
        self.assertTrue('data.demographics.TOTPOP_CY' in updated_entity.keys())
        self.assertTrue('data.demographics.PCI_CY' in updated_entity.keys())
        self.assertTrue('data.demographics.ROB' in updated_entity.keys())
        self.assertTrue('data.analytics.shape' in updated_entity.keys())
        self.assertTrue('data.analytics.AGG_INCOME_CY' in updated_entity.keys())

        self.assertEqual(updated_entity['data.demographics.TOTPOP_CY'], expected_updated_data_fields['data.demographics.TOTPOP_CY'])
        self.assertEqual(updated_entity['data.demographics.ROB'], expected_updated_data_fields['data.demographics.ROB'])
        self.assertEqual(updated_entity['data.analytics.shape'], gp7_processor._entity['data']['analytics']["shape"])
        self.assertEqual(updated_entity['data.analytics.AGG_INCOME_CY'], gp7_processor._entity['data']['analytics']["AGG_INCOME_CY"])


    # _____________________________________________ Test Complete Process ______________________________________________ #
    def test_complete_process(self):
        """
        Main end-to-end test of the process function.
        """

        try:
            geoshape_calculator = GISCalculator()
            wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)'

            self.__postgres_provider.shape_areas = {wkt_representation: 4}
            self.__postgres_provider.shape_centroids = {wkt_representation: 'POINT(0 0)'}
            self.__postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(wkt_representation)): 1}

            self.__rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

            # create an empty entity keyed under the trade area id just to track the updates. we only want to update 4 things here.
            self.__main_access.mds.entities = {
                'trade_area': {
                    self._test_trade_area['_id']: {}
                }
            }

            gp7_processor = GP7CoreTradeAreaDemographics()
            gp7_processor._config.dataset_year = 2013

            gp7_processor.process_object(self._test_trade_area)

            # _________________________________________ Verify _initialize() _____________________________________________ #
            self.assertEqual(gp7_processor._store, self._expected_store)
            self.assertEqual(gp7_processor._threshold_id, 1)

            # _______________________________________ Verify _do_geoprocessing() _________________________________________ #
            points_json_format = json.dumps({
                                                "Points":[
                                                    {
                                                        "longitude": self._expected_store.address.longitude,
                                                        "description": str(self._expected_store.store_id),
                                                        "latitude":self._expected_store.address.latitude,
                                                        "name": str(self._expected_store.store_id),
                                                        "storeID": self._expected_store.store_id,
                                                        "storeAddress": str(self._expected_store.store_id)
                                                    }
                                                ],
                                                "spatialReference": {"wkid": 4326}
                                            }, cls = APIEncoder)

            report_options = json.dumps([
                {
                    "ReportFormat":"s.xml",
                    "TemplateName":"Demographic and Income Profile",
                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                },
                {
                    "ReportFormat":"s.xml",
                    "TemplateName":"Nexus Age by Sex Report",
                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                },
                {
                    "ReportFormat":"s.xml",
                    "TemplateName":"Automotive Aftermarket Expenditures",
                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                }
            ])
            expected_request_format = {
                'Stores': points_json_format,
                'Radii': "10",
                'DistanceUnits': "esriMiles",
                'ActiveDatasetID': 'USA_ESRI_2011',
                'OutputSpatialReference': '{"wkid": 4326}',
                'ReportOptions': report_options,
                'OutputType': 'GetReport;GetFeatureClass',
                'f': 'JSON'
            }

            self.assertEqual(gp7_processor._response.request, expected_request_format)

            # _________________________________ Verify _preprocess_data_for_save() _______________________________________ #

            # verify demographics
            expected_demographics = {
                'TOTPOP_CY': {
                    'target_year': 2011,
                    'description': '2055 Total Population',
                    'value': 2.2
                },
                'PCI_CY': {
                    'target_year': 2011,
                    'description': 'PCI',
                    'value': 2
                },
                'ROB': {
                    'target_year': 2011,
                    'description': 'MALE 18-25',
                    'value': 1010101010.0
                }
            }


            self.assertEqual(gp7_processor._entity['data']['demographics'], expected_demographics)

            # verify period information
            self.assertEqual(gp7_processor._entity['data']['period_duration'], 'year')
            self.assertEqual(gp7_processor._entity['data']['period_start_date'], datetime.datetime(2013, 1, 1).date())
            self.assertEqual(gp7_processor._entity['data']['period_end_date'], datetime.datetime(2013, 12, 31).date())

            # verify analytics
            expected_analytics = {
                'shape': {
                    'surface_area': 4,
                    'shape_array': [[[1, 1], [-1, 1], [-1, -1], [1, -1]]],
                    'centroid': {
                        'longitude': 0.000000,
                        'latitude': 0.000000
                    },
                    'UTM_zone': '31N'
                },
                'AGG_INCOME_CY': {
                    'description': 'Aggregate Income',
                    'target_year': 2011,
                    'value': 4.4
                }
            }

            self.assertEqual(gp7_processor._entity['data']['analytics'], expected_analytics)

            # ____________________________________ Verify _save_processed_data() _________________________________________ #

            # verify updated fields
            updated_entity = self.__main_access.mds.entities['trade_area'][self._test_trade_area['_id']]

            self.assertEqual(updated_entity['data.demographics'], gp7_processor._entity['data']['demographics'])
            self.assertEqual(updated_entity['data.analytics'], gp7_processor._entity['data']['analytics'])
        except:
            raise
        finally:
            self.config.dataset_year = self._dataset_year


if __name__ == "__main__":
    unittest.main()



