"""
Created on Oct 18, 2012

@author: erezrubinstein
"""
import json

import unittest
from common.service_access.utilities.json_helpers import APIEncoder
from geoprocessing.business_logic.business_objects.trade_area import TradeArea
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.geoprocessors.demographics.gp1_10_1_geo_processor import GP1_10_1_GeoProcessor, demographics_data
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from geoprocessing.helpers.postgis_calculator import GISCalculator



class GP1Tests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies

        register_mock_dependencies()
        self.data_provider = Dependency("DataRepository").value
        self.rest_provider = Dependency("RestProvider").value
        self._postgres_provider = Dependency('PostgresDataRepository').value
        self.config = Dependency("Config").value


        # set up data
        self.store = Store.simple_init_with_address(store_id=777777, company_id=666666, longitude=99.99999999, latitude=88.88888888)
        self.store.address_id = 10
        self.data_provider.stores[self.store.store_id] = self.store
        self.data_provider.addresses[10] = self.store.address

        # make config match the below expectations
        self.config.gp1_templates = ["Demographic and Income Profile", "Nexus Age by Sex Report", "Automotive Aftermarket Expenditures"]

    def tearDown(self):
        dependencies.clear()


    #####################################################################################################################
    #############################################   initialization Tests ################################################
    #####################################################################################################################
    def test_initialization(self):
        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp1_processor._initialize()

        #make sure the values are initialized correctly
        self.assertEqual(gp1_processor._demographics, [])


    #####################################################################################################################
    ##############################################   get_GIS_data Tests #################################################
    #####################################################################################################################
    def test_get_GIS_data_drive_time(self):
        """
        Test that gp1 calls the correct rest mocked method for the drive time complexity
        """
        self.rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DriveTimeMinutes10)
        gp1_processor._home_store = self.store
        gp1_processor._do_geoprocessing()

        #create expected format
        #create expected response
        self.maxDiff = None
        points_json_format = json.dumps(
            {
                "Points":[
                    {
                        "longitude": self.store.address.longitude,
                        "description": str(self.store.store_id),
                        "latitude":self.store.address.latitude,
                        "name": str(self.store.store_id),
                        "storeID": self.store.store_id,
                        "storeAddress": str(self.store.store_id)
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

        #make sure response has the right request for the drive time report
        self.assertEqual(gp1_processor._response.request, expected_request_format)

    def test_get_GIS_data_simple_rings(self):
        """
        Test that gp1 calls the correct rest mocked method for the simple_rings complexity
        """
        self.rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp1_processor._home_store = self.store
        gp1_processor._do_geoprocessing()

        #create expected format
        points_json_format = json.dumps({
            "Points":[
                {
                    "longitude": self.store.address.longitude,
                    "description": str(self.store.store_id),
                    "latitude":self.store.address.latitude,
                    "name": str(self.store.store_id),
                    "storeID": self.store.store_id,
                    "storeAddress": str(self.store.store_id)
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
        #make sure response has the right request for the drive time report
        self.assertEqual(gp1_processor._response.request, expected_request_format)


    #####################################################################################################################
    #############################################   process_GIS_data Tests ##############################################
    #####################################################################################################################
    def test_process_GIS_data(self):
        """
        Test that gp1 parses the response and appends it to its internal list
        """
        #set up fake data and process it
        geoshape_calculator = GISCalculator()
        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')

        self._postgres_provider.shape_areas = {trade_area_1.wkt_representation(): 4}
        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)'}
        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1}
        
        self.rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp1_processor._home_store = self.store
        gp1_processor._demographics = []
        gp1_processor._do_geoprocessing()
        gp1_processor._preprocess_data_for_save()

        #verify the demographics were added to the _demographics variable
        self.assertEqual(gp1_processor._trade_area_area, 4)
        self.assertEqual(gp1_processor._trade_area_wkt_representation_linestring, 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')
        self.assertEqual(len(gp1_processor._demographics), 3)
        self.assertEqual(len(gp1_processor._demographics[0].dem_report_items), 4)
        self.assertEqual(len(gp1_processor._demographics[1].dem_report_items), 4)
        self.assertEqual(len(gp1_processor._demographics[2].dem_report_items), 4)

########################################################################################################################
###########################################   save_processed_data Tests ################################################
########################################################################################################################
    def test_save_processed_data(self):
        """
        Test that gp1 calls the correct data access (insert_demographics) method with it's built in _demographics
        """
        #set up fake data and process it

        geoshape_calculator = GISCalculator()
        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')


        self._postgres_provider.shape_areas = {trade_area_1.wkt_representation(): 4}
        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)'}
        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1}

        self.rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}},{"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'

        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp1_processor._home_store = self.store
        gp1_processor._store_id = self.store.store_id
        gp1_processor._demographics = []
        gp1_processor._period_id = 3
        gp1_processor._demographics.append(demographics_data("Demographic and Income Profile", [], 2091))
        gp1_processor._demographics.append(demographics_data("Nexus Age by Sex Report", [], 2092))
        gp1_processor._do_geoprocessing()
        gp1_processor._preprocess_data_for_save()
        gp1_processor._save_processed_data()

        #assert mock has correct data and tht both templates were saved
        self.assertEqual(len(self.data_provider.inserted_demographics), 5)
        self.assertEqual(self.data_provider.saved_trade_areas[0].area, 4)
        self.assertEqual(self.data_provider.inserted_demographics[0]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[1]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[0]["demographic_report_items"], [])
        self.assertEqual(self.data_provider.inserted_demographics[1]["demographic_report_items"], [])
        self.assertEqual(self.data_provider.inserted_demographics[0]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[1]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["template_name"], "Demographic and Income Profile")
        self.assertEqual(self.data_provider.inserted_demographics[1]["template_name"], "Nexus Age by Sex Report")


    #####################################################################################################################
    #############################################   complete process Tests ##############################################
    #####################################################################################################################
    def test_complete_process(self):
        """
        Main end-to-end test of the process function.
        """

        # mock up some data
        geoshape_calculator = GISCalculator()
        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')


        self._postgres_provider.shape_areas = {trade_area_1.wkt_representation(): 4}
        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)'}
        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1}

        self.rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[1, 1], [-1, 1], [-1, -1], [1, -1]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}, {"paramName":"Automotive Aftermarket Expenditures.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'
        self.data_provider.period_ids_per_year[2011] = 3

        # create GP1 processor and process
        gp1_processor = GP1_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp1_processor.process(self.store.company_id, self.store.store_id)

        # verify that everything is processed correctly
        self.assertEqual(self.data_provider.trade_area_shape, 'LINESTRING(1 1, -1 1, -1 -1, 1 -1)')
        self.assertEqual(gp1_processor._period_id, 3)

        # assert the get_data response
        self.assertIsNotNone(gp1_processor._response)
        self.assertGreater(len(gp1_processor._response.text), 100)

        # make sure it calls the simple rings version
        self.assertTrue(gp1_processor._response.url, 'http://192.168.10.114/arcgis/rest/services/DefaultMap/MapServer/exts/BAServer/SimpleRings/execute')

        # assert process_data demographics
        self.assertEqual(len(gp1_processor._demographics), 3)
        self.assertEqual(len(gp1_processor._demographics[0].dem_report_items), 4)
        self.assertEqual(len(gp1_processor._demographics[1].dem_report_items), 4)
        self.assertEqual(len(gp1_processor._demographics[2].dem_report_items), 4)

        # assert save_processed_data data provider
        self.assertEqual(len(self.data_provider.inserted_demographics), 3)
        self.assertEqual(self.data_provider.saved_trade_areas[0].area, 4)
        self.assertEqual(self.data_provider.inserted_demographics[0]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[1]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[2]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[0]["demographic_report_items"], gp1_processor._demographics[0].dem_report_items)
        self.assertEqual(self.data_provider.inserted_demographics[1]["demographic_report_items"], gp1_processor._demographics[1].dem_report_items)
        self.assertEqual(self.data_provider.inserted_demographics[2]["demographic_report_items"], gp1_processor._demographics[2].dem_report_items)
        self.assertEqual(self.data_provider.inserted_demographics[0]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[1]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[2]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["template_name"], "Demographic and Income Profile")
        self.assertEqual(self.data_provider.inserted_demographics[1]["template_name"], "Nexus Age by Sex Report")
        self.assertEqual(self.data_provider.inserted_demographics[2]["template_name"], "Automotive Aftermarket Expenditures")



#####################################################################################################################
###############################################  Main ######### #####################################################
#####################################################################################################################
if __name__ == "__main__":
    unittest.main()

    
    
