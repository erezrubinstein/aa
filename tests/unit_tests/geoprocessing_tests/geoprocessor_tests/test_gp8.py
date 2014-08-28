from datetime import datetime
from bson.objectid import ObjectId
import mox
from mox import IsA
from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from common.utilities.inversion_of_control import Dependency, dependencies
from common.utilities.signal_math import SignalDecimal
from core.common.business_logic.service_entity_logic import company_helper, store_helper
from geoprocessing.business_logic.business_helpers import competitive_store_helper
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects import geographical_coordinate
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.data_access.core_data_access.data_repository_core import CoreDataRepository
from geoprocessing.geoprocessors.competition.gp8_core_trade_area_competition import GP8CoreTradeAreaCompetition
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies

__author__ = 'erezrubinstein'

class GP8Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP8Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # create the mock trade _area
        self.trade_area_id = 1
        self.company_id = "woot"
        self.store_id = "chicken"
        self.trade_area = {
            "_id" : self.trade_area_id,
            "entity_type" : "trade_area",
            "interval" : None,
            "name" : "woot",
            "data" : {
                "address_id" : "519f910cf3d31b8e7d10d10e",
                "city" : "Wasco",
                "company_id" : self.company_id,
                "company_name" : "TEST_EREZ_BALDUCCI'S2",
                "demographics" : {
                    "HINC25_CY" : {
                        "value" : 2023,
                        "description" : "HINC25_CY",
                        "target_year" : 2011
                    }
                },
                "latitude" : 35.600383,
                "longitude" : -119.356367,
                "store_closed_date" : None,
                "store_id" : self.store_id,
                "store_opened_date" : None,
                "trade_area_threshold" : "DistanceMiles10",
            }
        }

        # create the test gp
        self.gp = GP8CoreTradeAreaCompetition("DistanceMiles10")
        self.gp._entity = self.trade_area


    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(GP8Tests, self).doCleanups()
        dependencies.clear()



    # ------------------------------ Initialize Tests ------------------------------

    def test_initialize(self):

        # stub out some methods
        self.mox.StubOutWithMock(self.gp, "_get_home_store")
        self.mox.StubOutWithMock(self.gp, "_get_trade_area_outer_shape")
        self.mox.StubOutWithMock(self.gp, "_get_potential_competitive_stores")

        # begin recording
        self.gp._get_home_store().AndReturn("cucumber")
        self.gp._get_trade_area_outer_shape().AndReturn("tomato")
        self.gp._get_potential_competitive_stores().AndReturn("bananas")

        # replay all
        self.mox.ReplayAll()

        # go
        self.gp._initialize()

        # verify the initialization
        self.assertEqual(self.gp.home_store, "cucumber")
        self.assertEqual(self.gp.trade_area_shape, "tomato")
        self.assertEqual(self.gp.potential_competitive_stores, "bananas")


    def test_get_home_store(self):

        # create expected objects
        expected_params = { "query": { "_id": self.store_id }, "entity_fields": ["_id", "interval", "data"] }

        # create mock objects
        mock_store = { "_id": "yo", "data": { "company_id": "soy erez" }, "interval": ["2012-01-01T00:00:00", None]}

        # start recording
        self.mock_main_access.mds.call_find_entities_raw("store", expected_params).AndReturn([mock_store])

        # replay all
        self.mox.ReplayAll()

        # go!
        store_obj = self.gp._get_home_store()

        # verify it matches expected object
        self.assertEqual(store_obj, Store.standard_init("yo", "soy erez", None, None, None, None, None, datetime(2012, 1, 1), END_OF_WORLD, datetime(2012, 1, 1), END_OF_WORLD))



    def test_get_trade_area_outer_shape(self):

        # mock up trade area shape.  Have 3 child arrays, with the second being the largest
        self.gp._entity["data"] = {
            "analytics" : {
                "shape" : {
                    "shape_array" : [
                        [[-1, 1]],
                        [[-1, 1], [-2, 2], [-3, 3]],
                        [[-1, 1], [-2, 2]]
                    ]
                }
            }
        }

        # go
        trade_area_outer_shape = self.gp._get_trade_area_outer_shape()

        # verify it gets the largest shape
        self.assertEqual(trade_area_outer_shape, "LINESTRING(-1.000000 1.000000, -2.000000 2.000000, -3.000000 3.000000)")


    def test_get_potential_competitive_stores__basic(self):

        cid1 = ObjectId()
        cid2 = ObjectId()
        cid3 = ObjectId()
        cid4 = ObjectId()

        sid1 = ObjectId()
        sid2 = ObjectId()
        sid3 = ObjectId()
        sid4 = ObjectId()

        # mock/expected data
        mock_competitive_companies = [
            { "_id": str(cid1), "interval": None, "competition_strength": 1 },
            { "_id": str(cid2), "interval": ['2012-01-01T00:00:00', '2013-02-02T00:00:00'], "competition_strength": 1},
            { "_id": str(cid3), "interval": ['2012-03-03T00:00:00', None], "competition_strength": 1},
            { "_id": str(cid4), "interval": [None, '2013-04-04T00:00:00'], "competition_strength": 1}
        ]
        mock_search_limits = GeographicalCoordinate(self.trade_area["data"]["longitude"], self.trade_area["data"]["latitude"], threshold = SignalDecimal(0.3)).get_search_limits()
        mock_stores = [
            { "store_id": str(sid1), "company_id": str(cid1), "latitude": 1, "longitude": -1, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid2), "company_id": str(cid2), "latitude": 2, "longitude": -2, "store_opened_date": '2012-01-02T00:00:00', "store_closed_date": '2013-02-03T00:00:00', "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid3), "company_id": str(cid3), "latitude": 3, "longitude": -3, "store_opened_date": '2012-03-04T00:00:00', "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid4), "company_id": str(cid4), "latitude": 4, "longitude": -4, "store_opened_date": None, "store_closed_date": '2013-04-05T00:00:00', "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" }
        ]

        # stub out certain methods
        self.mox.StubOutWithMock(company_helper, "select_competitive_companies")
        self.mox.StubOutClassWithMocks(store_helper, "StoreHelper")

        # start recording
        company_helper.select_competitive_companies(self.company_id).AndReturn(mock_competitive_companies)
        mock_store_helper = store_helper.StoreHelper()
        # include home company as potential competitor
        mock_store_helper.select_potential_away_stores_given_lat_long_filter(self.store_id, [str(cid1), str(cid2), str(cid3), str(cid4), "woot"], mock_search_limits).AndReturn(mock_stores)

        # replay all
        self.mox.ReplayAll()

        # go!
        away_stores = self.gp._get_potential_competitive_stores()
        away_stores = sorted([store.__dict__ for store in away_stores], key=lambda x: x["away_store_id"])

        # create expected stores
        expected_away_stores = [
            StoreCompetitionInstance.detailed_init(str(sid1), str(cid1), 1, -1, None, None, START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD, "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(str(sid2), str(cid2), 2, -2, None, None, datetime(2012, 1, 2), datetime(2013, 2, 3), datetime(2012, 1, 2), datetime(2013, 2, 3), datetime(2012, 1, 1), datetime(2013, 2, 2), "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(str(sid3), str(cid3), 3, -3, None, None, datetime(2012, 3, 4), END_OF_WORLD, datetime(2012, 3, 4), END_OF_WORLD, datetime(2012, 3, 3), END_OF_WORLD, "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(str(sid4), str(cid4), 4, -4, None, None, START_OF_WORLD, datetime(2013, 4, 5), START_OF_WORLD, datetime(2013, 4, 5), START_OF_WORLD, datetime(2013, 4, 4), "yo", "how", "you", "doin", "i'm", "stupendous").__dict__
        ]

        # verify that the away stores are correct
        self.assertItemsEqual(away_stores, expected_away_stores)


    def test_get_potential_competitive_stores__dedupe_trade_areas(self):
        """
        The query that this method does, selects stores from the trade areas table.  This could result in duplicate stores since each store has multiple trade areas in different thresholds.
        This test verifies that the method dedupes the stores correctly.
        """

        cid1 = ObjectId()

        sid1 = ObjectId()
        sid2 = ObjectId()

        # mock/expected data
        mock_competitive_companies = [{ "_id": str(cid1), "interval": None, "competition_strength": 1 }]
        mock_search_limits = GeographicalCoordinate(self.trade_area["data"]["longitude"], self.trade_area["data"]["latitude"], threshold = SignalDecimal(0.3)).get_search_limits()

        # create trade areas with some dupes
        mock_stores = [
            { "store_id": str(sid1), "company_id": str(cid1), "latitude": 1, "longitude": -1, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid1), "company_id": str(cid1), "latitude": 1, "longitude": -1, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid1), "company_id": str(cid1), "latitude": 1, "longitude": -1, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid2), "company_id": str(cid1), "latitude": 2, "longitude": -2, "store_opened_date": '2012-01-02T00:00:00', "store_closed_date": '2013-02-03T00:00:00', "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" },
            { "store_id": str(sid2), "company_id": str(cid1), "latitude": 2, "longitude": -2, "store_opened_date": '2012-01-02T00:00:00', "store_closed_date": '2013-02-03T00:00:00', "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous" }
        ]

        # stub out certain methods
        self.mox.StubOutWithMock(company_helper, "select_competitive_companies")
        self.mox.StubOutClassWithMocks(store_helper, "StoreHelper")

        # start recording
        company_helper.select_competitive_companies(self.company_id).AndReturn(mock_competitive_companies)
        mock_store_helper = store_helper.StoreHelper()
        mock_store_helper.select_potential_away_stores_given_lat_long_filter(self.store_id, [str(cid1), "woot"], mock_search_limits).AndReturn(mock_stores)

        # replay all
        self.mox.ReplayAll()

        # go!
        away_stores = self.gp._get_potential_competitive_stores()
        away_stores = sorted([store.__dict__ for store in away_stores], key=lambda x: x["away_store_id"])

        # create expected stores (i.e. no dupes)
        expected_stores = [
            StoreCompetitionInstance.detailed_init(str(sid1), str(cid1), 1, -1, None, None, START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD, "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(str(sid2), str(cid1), 2, -2, None, None, datetime(2012, 1, 2), datetime(2013, 2, 3), datetime(2012, 1, 2), datetime(2013, 2, 3), START_OF_WORLD, END_OF_WORLD, "yo", "how", "you", "doin", "i'm", "stupendous").__dict__
        ]

        # verify that the away stores are correct (i.e. no dupes)
        self.assertItemsEqual(away_stores, expected_stores)



    # ------------------------------ Do Geoprocessing Tests ------------------------------

    def test_do_geoprocessing(self):

        # create mock potential competitive stores
        store_1 = StoreCompetitionInstance.basic_init(1, 1, 1, -1)
        store_2 = StoreCompetitionInstance.basic_init(2, 2, 2, -2)
        store_3 = StoreCompetitionInstance.basic_init(3, 3, 3, -3)
        self.gp.potential_competitive_stores = [store_1, store_2, store_3]

        # mock geo shape calculator and trade area shape
        self.gp._geoshape_calculator = self.mox.CreateMockAnything()
        self.gp.trade_area_shape = "chilly_willy"

        # begin stubbing methods/classes
        self.mox.StubOutClassWithMocks(geographical_coordinate, "GeographicalCoordinate")

        # begin recording (store1 and store3 are in, store2 is out)
        goe_coordinate = geographical_coordinate.GeographicalCoordinate(store_1.longitude, store_1.latitude)
        goe_coordinate.wkt_representation().AndReturn("woot")
        self.gp._geoshape_calculator.shape_contains_point("chilly_willy", "woot").AndReturn(True)
        goe_coordinate = geographical_coordinate.GeographicalCoordinate(store_2.longitude, store_2.latitude)
        goe_coordinate.wkt_representation().AndReturn("chicken")
        self.gp._geoshape_calculator.shape_contains_point("chilly_willy", "chicken").AndReturn(False)
        goe_coordinate = geographical_coordinate.GeographicalCoordinate(store_3.longitude, store_3.latitude)
        goe_coordinate.wkt_representation().AndReturn("Salad")
        self.gp._geoshape_calculator.shape_contains_point("chilly_willy", "Salad").AndReturn(True)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._do_geoprocessing()

        # make sure store1 and store3 were matched as away stores
        self.assertEqual(self.gp._competitive_stores, [store_1, store_3])



    # ------------------------------ Preprocess Tests ------------------------------

    def test_preprocess_data_for_save(self):

        # mock various parts of gp
        self.gp.home_store = "chicken"
        self.gp._competitive_stores = "woot"

        # stub out the CompetitiveStoreHelper class
        self.mox.StubOutClassWithMocks(competitive_store_helper, "CompetitiveStoreHelper")

        # start recording
        competitive_store_helper.CompetitiveStoreHelper("chicken", "woot", self.trade_area_id, IsA(CoreDataRepository))

        # replay all
        self.mox.ReplayAll()

        # test!
        self.gp._preprocess_data_for_save()



    # ------------------------------ Save Processed Data Tests ------------------------------

    def test_save_processed_data(self):

        # mock out the competition instance
        self.gp._competition_instance = self.mox.CreateMock(CompetitiveStoreHelper)

        # start recording
        self.gp._competition_instance.synchronize_competitive_stores_in_db()
        self.gp._competition_instance.synchronize_monopolies_in_db()

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._save_processed_data()