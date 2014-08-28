"""
Created on Oct 18, 2012

@author: erezrubinstein
"""
import json
import unittest
from common.service_access.utilities.json_helpers import APIEncoder
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.trade_area import TradeArea
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.geoprocessors.competition.gp2_10_1_geo_processor import GP2_10_1_GeoProcessor
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse
from common.utilities.signal_math import SignalDecimal

#####################################################################################################################
###############################################   GeoProcessor Tests ################################################
#####################################################################################################################


class GP2ReportTests(unittest.TestCase):

    def setUp(self):
        # set up mock dependencies

        register_mock_dependencies()
        self.rest_provider = Dependency("RestProvider").value
        self.sql_provider = Dependency("DataRepository").value


        # Joseph A Bank
        self.store = Store.simple_init_with_address(43, 14107, -100.00, 45.00)
        self.sql_provider.stores[self.store.store_id] = self.store
        self.store.address_id = 10
        self.sql_provider.addresses[10] = self.store.address
        self.away_stores = {
            44: StoreCompetitionInstance.basic_init_with_competition(44, 14106, -73.54, 41.10, 1347901),
            45: StoreCompetitionInstance.basic_init_with_competition(45, 14107, -80.40, 37.21, 1347884)}

    def tearDown(self):
        dependencies.clear()



#####################################################################################################################
#############################################   initialization Tests ################################################
#####################################################################################################################
    def test_initialization_competition(self):
        """
        Verify that the GP2 initialization method sets its variables up correctly
        """
        # initialize mocks

        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self.store.store_id
        mock_trade_area.store_id = self.store.store_id
        mock_trade_area.threshold_id = 1
        self.sql_provider.mock_trade_areas[self.store.store_id] = mock_trade_area
        self.sql_provider.away_stores_within_range = self.away_stores
        # create geo processor and store
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._initialize()

        # make sure the away stores and initiated correctly
        self.assertEqual(gp2_processor._home_store.store_id, 43)
        self.assertEqual(len(gp2_processor._away_stores), 2)
        # store 1
        self.assertEqual(gp2_processor._away_stores[44].away_store_id, 44)
        self.assertEqual(gp2_processor._away_stores[44].company_id, 14106)
        self.assertEqual(gp2_processor._away_stores[44].longitude, SignalDecimal(41.10))
        self.assertEqual(gp2_processor._away_stores[44].latitude, SignalDecimal(-73.54))
        self.assertEqual(gp2_processor._away_stores[44].competitive_company_id, 1347901)
        # store 2
        self.assertEqual(gp2_processor._away_stores[45].away_store_id, 45)
        self.assertEqual(gp2_processor._away_stores[45].company_id, 14107)
        self.assertEqual(gp2_processor._away_stores[45].longitude, SignalDecimal( 37.21))
        self.assertEqual(gp2_processor._away_stores[45].latitude, SignalDecimal(-80.40))
        self.assertEqual(gp2_processor._away_stores[45].competitive_company_id, 1347884)

        # make sure that the competition instance has the correct type and that the trade area is selected correctly
        self.assertEqual(gp2_processor._entity.trade_area_id, self.store.store_id)


#####################################################################################################################
##############################################   get_GIS_data Tests #################################################
#####################################################################################################################
    def test_get_GIS_data(self):
        #set up test data and run
        self.sql_provider.away_stores_within_range = self.away_stores
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._initialize()
        self.rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        away_stores = gp2_processor._away_stores
        gp2_processor._do_geoprocessing()

        #set up expected format
        home_point = {
            "longitude": self.store.address.longitude,
            "description":self.store.store_id,
            "latitude": self.store.address.latitude,
            "name": self.store.store_id,
            "storeID": self.store.store_id
        }

        wrapped_home_point = json.dumps({
                                            "Points": [home_point],
                                            "spatialReference": {"wkid": 4326}
                                        }, cls = APIEncoder)
        # make the large list of away store points
        away_store_list = []
        for away_store in away_stores.values():
            away_store_list.append({
                "storeID": away_store.away_store_id,
                "name": away_store.away_store_id,
                "description": away_store.away_store_id,
                "latitude": away_store.latitude,
                "longitude": away_store.longitude,
                "storeAddress": away_store.away_store_id
            })
        wrapped_away_points = json.dumps({
                                             "Points": away_store_list,
                                             "spatialReference": {"wkid": 4326}
                                         }, cls = APIEncoder)
        report_options = json.dumps({
            "ReportFormat":"s.xml",
            "ReportHeader":[
                {
                    "key":"subtitle",
                    "value":"Custom Report Title"
                }
            ]
        })

        expected_form = {

            'Stores': wrapped_home_point,
            'BusinessPoints': wrapped_away_points,
            'BusinessesSearchMethod': 'esriWithinRange',
            'CalculationMethod': 'esriDistanceCalcTypeDriveTime',
            'FieldNames': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'FieldAliases': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'ActiveDatasetID': 'USA_ESRI_2011',
            'StoreIDField': 'STORE_ID',
            'StoreNameField': 'NAME',
            'NearestDistance': '10',
            'NearestDistanceUnits': 'esriMiles',
            'DistanceUnits': 'esriMiles', #try removing this one -- it's ignored for DriveTime
            'StandardReportOptions': report_options,
            'OutputType': 'GetReport',
            'ReturnGeometry': 'false', #to speed things up
            'f': 'JSON'

        }

        #make sure expected format matches returned
        self.maxDiff = None
        self.assertEqual(gp2_processor._response.request, expected_form)


    def test_get_GIS_data__does_not_run_without_away_stores(self):
        # make sure away stores of None works
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._away_stores = None
        gp2_processor._do_geoprocessing()
        self.assertEqual(gp2_processor._response, None)

        # make sure away stores of {} works
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._away_stores = {}
        gp2_processor._do_geoprocessing()
        self.assertEqual(gp2_processor._response, None)


#####################################################################################################################
#############################################   process_GIS_data Tests ##############################################
#####################################################################################################################
    def test_process_GIS_data(self):
        # mock up trade area
        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self.store.store_id
        mock_trade_area.store_id = self.store.store_id
        mock_trade_area.threshold_id = 1

        self.sql_provider.mock_trade_areas[self.store.store_id] = mock_trade_area
        self.sql_provider.away_stores_within_range = self.away_stores
        #set up fake data and process
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._initialize()
        gp2_processor._response = MockResponse('{"results":[{"paramName":"LocatorP.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/TESTLocatorReport.s.xml"}}],"messages":[]}', None, None)
        gp2_processor._preprocess_data_for_save()

        #make sure the drive time for the store is what the mock data is setting it up to be
        self.assertEqual(len(gp2_processor._competition_instance.away_stores), 2)
        self.assertEqual(gp2_processor._competition_instance.away_stores[0].travel_time, '6.05')
        self.assertEqual(gp2_processor._competition_instance.away_stores[1].travel_time, '5.06')

    def test_process_GIS_data__does_not_run_without_away_stores(self):
        # mock up trade area
        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self.store.store_id
        mock_trade_area.store_id = self.store.store_id
        mock_trade_area.threshold_id = 1

        # make sure away stores of None works
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._away_stores = None
        gp2_processor._entity = mock_trade_area
        gp2_processor._preprocess_data_for_save()
        self.assertEqual(len(gp2_processor._competition_instance.away_stores),0)

#        # make sure away stores of {} works
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._away_stores = {}
        gp2_processor._entity = mock_trade_area
        gp2_processor._preprocess_data_for_save()
        self.assertEqual(len(gp2_processor._competition_instance.away_stores),0)





#####################################################################################################################
###########################################   save_processed_data Tests #############################################
#####################################################################################################################
    def test_save_processed_synchronizes_competitive_stores(self):
        """
        Test that gp1 calls the correct synchronize competitive_stores db method
        """
        #set up fake data and process it
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._competition_instance = CompetitiveStoreHelper(self.store, self.away_stores.values(), 100, self.sql_provider)
        gp2_processor._save_processed_data()

        #assert mock has correct data and tht both templates were saved
        self.assertEqual(self.sql_provider.home_store_id, self.store.store_id)
        self.assertEqual(self.sql_provider.batch_upserted_trade_area_id, 100)
        self.assertEqual(len(self.sql_provider.batch_upserted_competitive_stores), 2)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[0]["away_store_id"], 44)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[1]["away_store_id"], 45)

    def test_save_processed_synchronize_monopolies(self):
        """
        Test that gp1 calls the correct data access (insert_demographics) method with it's built in _demographics
        """
        #s et up fake data and process it
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self.store
        gp2_processor._competition_instance = CompetitiveStoreHelper(self.store, self.away_stores.values(), 100, self.sql_provider)

        # mock up competitive_stores_instances for monopolies
        self.sql_provider.competitive_stores[self.store.store_id] = []

        # call save_processed_data()
        gp2_processor._save_processed_data()

        # assert mock has correct data and that both templates were saved
        self.assertEqual(self.sql_provider.home_store_id, self.store.store_id)

        # verify that the right away companies were upserted
        self.assertEqual(self.sql_provider.batch_upserted_trade_area_id, 100)
        self.assertEqual(len(self.sql_provider.batch_upserted_competitive_stores), 2)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[0]["away_store_id"], 44)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[1]["away_store_id"], 45)

        # verify that this is not a monopoly
        self.assertEqual(len(self.sql_provider.upserted_monopolies), 1)




#####################################################################################################################
#############################################   complete process Tests ##############################################
#####################################################################################################################
    
    def test_complete_process(self):
        """
        Main end-to-end test of the process function.
        """
        # mock up data and process
        self.sql_provider.away_stores_within_range = self.away_stores
        self.sql_provider.period_ids_per_year[2011] = 3
        self.sql_provider.longitude = self.store.address.longitude
        self.sql_provider.latitude = self.store.address.latitude
        self.rest_provider.post_response = '''{"results":[{"paramName":"LocatorP.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/LocatorReport/_ags_T7BEDF943448A6A55353A90D388BCF.s.xml"}}],"messages":[]}'''

        self.sql_provider.mock_trade_areas[self.store.store_id] = self.store.select_trade_areas()

        # create processor and process
        gp2_processor = GP2_10_1_GeoProcessor(TradeAreaThreshold.DistanceMiles10)
        gp2_processor.process(self.store.company_id, self.store.store_id)

        # verify processing
        self.assertEqual(gp2_processor._period_id, 3)
        self.assertIsNotNone(gp2_processor._response)
        self.assertGreater(len(gp2_processor._response.text), 100)
        # make sure it calls the simple rings version
        self.assertTrue(gp2_processor._response.url, 'http://192.168.10.114/arcgis/rest/services/DefaultMap/MapServer/exts/BAServer/LocatorReport/execute')

        # assert process_data demographics
        self.assertEqual(gp2_processor._competition_instance.away_stores[0].travel_time, '6.05')
        self.assertEqual(gp2_processor._competition_instance.away_stores[1].travel_time, '5.06')

        # assert save_processed_data data provider
        self.assertEqual(self.sql_provider.batch_upserted_trade_area_id, self.store.store_id)
        self.assertEqual(len(self.sql_provider.batch_upserted_competitive_stores), 2)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[0]["away_store_id"], 44)
        self.assertEqual(self.sql_provider.batch_upserted_competitive_stores[1]["away_store_id"], 45)
