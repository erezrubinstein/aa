from core.common.business_logic.service_entity_logic.trade_area_upserter import TradeAreaUpserter
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from tests.integration_tests.utilities.data_access_misc_queries import *
from common.utilities.inversion_of_control import Dependency
from common.utilities.signal_math import SignalDecimal
from bson.objectid import ObjectId


__author__ = 'erezrubinstein'


class StoreHelperTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = ObjectId()
        self.source = "main_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        # get dependencies
        self.main_params = Dependency("CoreAPIParamsBuilder").value
        
        # create helper vars for this class
        self.store_helper = StoreHelper()

    def setUp(self):
        # delete when starting
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    # --------------------------- Begin Tests ---------------------------

    def store_helper_test_delete_store_and_all_children(self):

        # create a company, a rir, a store, and an address
        test_company_name = "chick_woot_company"
        company_id = ensure_id(insert_test_company(name=test_company_name))
        rir_id = ensure_id(insert_test_rir(self.context, company_id, company_name=test_company_name))
        store_id = self.store_helper.create_new_store(self.context, rir_id, async=False)

        trade_area_upserter = TradeAreaUpserter(str(store_id))
        trade_area_upserter.initialize()
        trade_area_upserter.upsert('DistanceMiles10')

        # get the objects above
        company = self.__find_raw_by_id("company", company_id)
        rir = self.__find_raw_by_id("retail_input_record", rir_id)
        store = self.__find_raw_by_id("store", store_id)

        # get address from store and query for it
        address_id = store["links"]["address"]["address_assignment"][0]["entity_id_to"]
        address = self.__find_raw_by_id("address", address_id)

        # get the trade area
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = { "data.store_id": str(store_id) }, entity_fields = ["data"])["params"]
        trade_area = self.main_access.mds.call_find_entities_raw("trade_area", params, encode_and_decode_results=False)[0]

        # verify that nothing is null
        self.test_case.assertIsNotNone(company)
        self.test_case.assertIsNotNone(rir)
        self.test_case.assertIsNotNone(store)
        self.test_case.assertIsNotNone(address)
        self.test_case.assertIsNotNone(trade_area)

        # delete the store
        self.store_helper.delete_store_and_all_children(store_id, self.context)

        # query everything again and verify that it's not there
        company = self.__find_raw_by_id("company", company_id)
        rir = self.__find_raw_by_id("retail_input_record", rir_id)
        store = self.__find_raw_by_id("store", store_id)
        address = self.__find_raw_by_id("address", address_id)
        trade_area = self.main_access.mds.call_find_entities_raw("trade_area", params, encode_and_decode_results=False)

        # verify that everything is null except for the company
        self.test_case.assertIsNotNone(company)
        self.test_case.assertIsNone(rir)
        self.test_case.assertIsNone(store)
        self.test_case.assertIsNone(address)
        self.test_case.assertEqual(trade_area, [])


    def test_select_potential_away_stores_for_geoprocessing__companies_filter(self):
        """
        Make sure that the company filter is used correctly
        """

        # create a homeboy store_id - doesn't need to exist in the db for this test
        home_store_id = ObjectId()

        # create three companies
        company_id1 = ensure_id(insert_test_company())
        company_id2 = ensure_id(insert_test_company())
        company_id3 = ensure_id(insert_test_company())

        # insert a store area per company
        store_id_1 = ensure_id(create_store_with_rir(company_id1))
        store_id_2 = ensure_id(create_store_with_rir(company_id2))
        store_id_3 = ensure_id(create_store_with_rir(company_id3))

        # add a second test trade area to company2, just for testing
        store_id_22 = ensure_id(create_store_with_rir(company_id2))

        # select stores for companies 1 and 2 and make sure the correct ones show up
        search_limits = GeographicalCoordinate(-1, 1, threshold = SignalDecimal(1)).get_search_limits()
        stores = self.store_helper.select_potential_away_stores_given_lat_long_filter(home_store_id ,[company_id1, company_id2], search_limits)
        stores = convert_entity_list_to_dictionary(stores, "store_id")

        # verify results
        expected_stores = {
            str(store_id_1): {"store_id": str(store_id_1), "company_id": str(company_id1), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" },
            str(store_id_2): {"store_id": str(store_id_2), "company_id": str(company_id2), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" },
            str(store_id_22): {"store_id": str(store_id_22), "company_id": str(company_id2), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" }
        }
        self.test_case.assertEqual(stores, expected_stores)


    def test_select_potential_away_stores_for_geoprocessing__lat_long_filter(self):
        """
        Make sure that the company filter is used correctly
        """

        # create a homeboy store_id - doesn't need to exist in the db for this test
        home_store_id = ObjectId()

        # create one company
        company_id1 = ensure_id(insert_test_company())

        # insert several stores.  some within the range and some outside
        store_id_1 = ensure_id(create_store_with_rir(company_id1, latitude = 2, longitude = -2))      # inside
        store_id_2 = ensure_id(create_store_with_rir(company_id1, latitude = 1.5, longitude = -1.5))  # inside
        store_id_3 = ensure_id(create_store_with_rir(company_id1, latitude = 2.1, longitude = -2.1))  # outside
        store_id_4 = ensure_id(create_store_with_rir(company_id1, latitude = 2, longitude = 2))       # outside
        store_id_5 = ensure_id(create_store_with_rir(company_id1, latitude = -2, longitude = 2))      # outside
        store_id_6 = ensure_id(create_store_with_rir(company_id1, latitude = -2, longitude = -2))     # outside

        # select stores for companies 1 and 2 and make sure the correct ones show up
        search_limits = GeographicalCoordinate(-1, 1, threshold = SignalDecimal(1)).get_search_limits()
        stores = self.store_helper.select_potential_away_stores_given_lat_long_filter(home_store_id ,[company_id1], search_limits)
        stores = convert_entity_list_to_dictionary(stores, "store_id")

        # verify results
        expected_stores = {
            str(store_id_1): { "store_id": str(store_id_1), "company_id": str(company_id1), "latitude": 2, "longitude": -2, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD , "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY"},
            str(store_id_2): { "store_id": str(store_id_2), "company_id": str(company_id1), "latitude": 1.5, "longitude": -1.5, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" }
        }
        self.test_case.assertEqual(stores, expected_stores)


    def test_select_potential_away_stores_for_geoprocessing__test_open_close_dates(self):
        """
        Make sure that the company filter is used correctly
        """

        # create a homeboy store_id - doesn't need to exist in the db for this test
        home_store_id = ObjectId()

        # create a company
        company_id1 = ensure_id(insert_test_company())

        # insert two stores, one with a start date
        opened_date = datetime(2012, 1, 1)
        closed_date = datetime(2013, 1, 1)
        store_id_1 = ensure_id(create_store_with_rir(company_id1, as_of_date = opened_date, as_of_date_is_opened_date = True))
        store_id_2 = ensure_id(create_store_with_rir(company_id1))

        # update store_1 to give it the correct end_date
        query = { "_id": store_id_1 }
        update_operation = { "$set": { "interval.1": closed_date }}
        self.main_access.mds.call_batch_update_entities("store", query, update_operation, self.context)

        # select stores for companies 1 and 2 and make sure the correct ones show up
        search_limits = GeographicalCoordinate(-1, 1, threshold = SignalDecimal(1)).get_search_limits()
        stores = self.store_helper.select_potential_away_stores_given_lat_long_filter(home_store_id ,[company_id1], search_limits)
        stores = convert_entity_list_to_dictionary(stores, "store_id")

        # verify results
        expected_stores = {
            str(store_id_1): { "store_id": str(store_id_1), "company_id": str(company_id1), "latitude": 1, "longitude": -1, "store_opened_date": opened_date, "store_closed_date": closed_date, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" },
            str(store_id_2): { "store_id": str(store_id_2), "company_id": str(company_id1), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" },
        }
        self.test_case.assertEqual(stores, expected_stores)


    def test_select_potential_away_stores_for_geoprocessing__ignore_self(self):
        """
        Make sure that the company filter is used correctly
        """

        # create three companies
        company_id1 = ensure_id(insert_test_company())

        # insert several stores
        store_id_1 = ensure_id(create_store_with_rir(company_id1))
        store_id_2 = ensure_id(create_store_with_rir(company_id1))
        store_id_3 = ensure_id(create_store_with_rir(company_id1))

        # select trade trade areas for the company
        search_limits = GeographicalCoordinate(-1, 1, threshold = SignalDecimal(1)).get_search_limits()
        stores = self.store_helper.select_potential_away_stores_given_lat_long_filter(store_id_2 ,[company_id1], search_limits)
        stores = convert_entity_list_to_dictionary(stores, "store_id")

        # verify that it did not select trade area 2, since it was included as "itself"
        expected_stores = {
            str(store_id_1): { "store_id": str(store_id_1), "company_id": str(company_id1), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" },
            str(store_id_3): { "store_id": str(store_id_3), "company_id": str(company_id1), "latitude": 1, "longitude": -1, "store_opened_date": START_OF_WORLD, "store_closed_date": END_OF_WORLD, "street_number": "123", "street": "Main St", "city": "UNIT_TEST_VILLE", "state": "UT", "zip": "12345", "company_name": "UNITTEST_COMPANY" }
        }
        self.test_case.assertEqual(stores, expected_stores)




    # --------------------------- Private Methods ---------------------------

    def __find_raw_by_id(self, entity_type, id):
        query = {"_id": ensure_id(id)}
        entity_fields = ["_id", "name", "links"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=entity_fields)["params"]
        results = self.main_access.mds.call_find_entities_raw(entity_type, params, encode_and_decode_results=False)

        if results:
            return results[0]
        else:
            return None




