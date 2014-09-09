from datetime import datetime
import mox
from mox import IsA
from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import company_helper, store_helper
from geoprocessing.business_logic.business_helpers import competitive_store_helper
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.data_access.core_data_access.data_repository_core import CoreDataRepository
from geoprocessing.geoprocessors.competition.gp9_core_trade_area_competition_geo_json import GP9CoreTradeAreaCompetition
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies

__author__ = 'erezrubinstein'

class GP9Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP9Tests, self).setUp()

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
                "latitude" : 35.600383,
                "longitude" : -119.356367,
                "store_closed_date" : None,
                "store_id" : self.store_id,
                "store_opened_date" : None,
                "trade_area_threshold" : "DistanceMiles10",
                "analytics": {
                    "shape": {
                        "shape_array": "peanut_butter_jelly_time"
                    }
                }
            }
        }

        # create the test gp
        self.gp = GP9CoreTradeAreaCompetition()
        self.gp._entity = self.trade_area


    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(GP9Tests, self).doCleanups()
        dependencies.clear()



    # ------------------------------ Initialize Tests ------------------------------

    def test_initialize(self):

        # stub out some methods
        self.mox.StubOutWithMock(self.gp, "_get_home_store")
        self.mox.StubOutWithMock(self.gp, "_set_competitive_companies")

        # begin recording
        self.gp._get_home_store().AndReturn("cucumber")
        self.gp._set_competitive_companies()

        # replay all
        self.mox.ReplayAll()

        # go
        self.gp._initialize()

        # verify the initialization
        self.assertEqual(self.gp.home_store, "cucumber")
        self.assertEqual(self.gp.trade_area_shape, "peanut_butter_jelly_time")


    def test_get_home_store(self):

        # create expected objects
        expected_params = { "query": { "_id": self.store_id }, "entity_fields": ["_id", "interval", "data.company_id"] }

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


    def test_set_competitive_companies(self):

        # create mock competitive companies
        mock_competitive_companies = [
            { "_id": "chicken"},
            { "_id": "wings"}
        ]

        # stub the company helper class
        self.mox.StubOutWithMock(company_helper, "select_competitive_companies")

        # start recording
        company_helper.select_competitive_companies(self.company_id).AndReturn(mock_competitive_companies)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._set_competitive_companies()

        # verify the various that the company vars were set correctly (and it's own company was added to the mix)
        self.assertEqual(self.gp.competitive_companies_dictionary, {
            "chicken": { "_id": "chicken"},
            "wings": { "_id": "wings"},
            self.company_id: { "_id": self.company_id }
        })
        self.assertEqual(self.gp.competitive_company_ids, ["chicken", "wings", self.company_id])



    # ------------------------------ Do Geoprocessing Tests ------------------------------

    def test_do_geoprocessing(self):

        # create mock competitive stores
        mock_stores = [
            { "store_id": 1, "company_id": 1, "latitude": 1, "longitude": -1, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous"},
            { "store_id": 2, "company_id": 2, "latitude": 2, "longitude": -2, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous"},
            { "store_id": 3, "company_id": 3, "latitude": 3, "longitude": -3, "store_opened_date": None, "store_closed_date": None, "company_name": "yo", "street_number": "how", "street": "you", "city": "doin", "state": "i'm", "zip": "stupendous"}
        ]

        # mock gp data
        self.gp.competitive_company_ids = ["check", "yourself", "before", "you", "wreck", "yourself"]
        self.gp.trade_area_shape = "peanut_butter_jelly_time"
        self.gp.competitive_companies_dictionary = {
            1: { "_id": 1, "interval": None, "competition_strength": 1 },
            2: { "_id": 2, "interval": None, "competition_strength": 1 },
            3: { "_id": 3, "interval": None, "competition_strength": 1 },
        }

        # begin stubbing methods/classes
        self.mox.StubOutClassWithMocks(store_helper, "StoreHelper")

        # begin recording (store1 and store3 are in, store2 is out)
        store_helper.StoreHelper().select_competitive_stores_given_trade_area_shape(self.store_id, self.gp.competitive_company_ids, "peanut_butter_jelly_time").AndReturn(mock_stores)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._do_geoprocessing()

        # make sure store1 and store3 were matched as away stores
        expected = [
            StoreCompetitionInstance.detailed_init(1, 1, 1, -1, None, None, START_OF_WORLD, END_OF_WORLD,
                                                   START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD,
                                                   "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(2, 2, 2, -2, None, None, START_OF_WORLD, END_OF_WORLD,
                                                   START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD,
                                                   "yo", "how", "you", "doin", "i'm", "stupendous").__dict__,
            StoreCompetitionInstance.detailed_init(3, 3, 3, -3, None, None, START_OF_WORLD, END_OF_WORLD,
                                                   START_OF_WORLD, END_OF_WORLD, START_OF_WORLD, END_OF_WORLD,
                                                   "yo", "how", "you", "doin", "i'm", "stupendous").__dict__
        ]
        competitive_store_results = [competitive_store.__dict__ for competitive_store in self.gp._competitive_stores]
        self.assertItemsEqual(competitive_store_results, expected)



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