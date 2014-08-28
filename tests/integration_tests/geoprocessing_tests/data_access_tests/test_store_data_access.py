from datetime import datetime
from common.business_logic.company_info import CompanyInfo
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.zip_code import ZipCode
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance

from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from geoprocessing.data_access.trade_area_handler import insert_trade_area_shape
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_store, delete_test_store, delete_test_address, delete_test_competitors, insert_test_address, insert_test_company, insert_test_competitor, delete_test_company, delete_test_trade_area, select_store_by_store_id, delete_test_trade_area_shape, insert_test_zip, delete_test_zip

__author__ = 'erezrubinstein'

import unittest

class StoreDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

        # insert test data
        cls._company_id = insert_test_company()
        cls._address_id = insert_test_address(-1, 1)
        cls._store_id = insert_test_store(cls._company_id, cls._address_id, "20120101", "20121201", "20120102", "20121202")
        cls._store = Store().select_by_id(cls._store_id)

        # away stores
        cls._away_store_1_company_id = insert_test_company()
        cls._away_store_2_company_id = insert_test_company()
        insert_test_competitor(cls._company_id, cls._away_store_1_company_id)
        insert_test_competitor(cls._company_id, cls._away_store_2_company_id)
        cls._away_store_1_address_id = insert_test_address(-1, 1)
        cls._away_store_2_address_id = insert_test_address( -2, 2)
        cls._away_store_1_id = insert_test_store(cls._away_store_1_company_id, cls._away_store_1_address_id, "20110101", "20111201", "20110102", "20111202")
        cls._away_store_2_id = insert_test_store(cls._away_store_2_company_id, cls._away_store_2_address_id, "20110101", "20111201", "20110102", "20111202")

        # create trade area
        cls._trade_area = cls._SQL_data_repository.select_trade_area_force_insert(cls._store_id, TradeAreaThreshold.DistanceMiles10)
        insert_trade_area_shape(cls._trade_area.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)
        cls._start_date = datetime(2012, 01, 01)
        cls._end_date = datetime(2012, 12, 01)

    @classmethod
    def tearDownClass(cls):
        # delete test data
        delete_test_trade_area_shape(cls._trade_area.trade_area_id)
        delete_test_trade_area(cls._store_id)
        delete_test_store(cls._store_id)
        delete_test_address(cls._address_id)
        delete_test_store(cls._away_store_1_id)
        delete_test_store(cls._away_store_2_id)
        delete_test_address(cls._away_store_1_address_id)
        delete_test_address(cls._away_store_2_address_id)
        delete_test_competitors(cls._company_id)
        delete_test_company(cls._away_store_1_company_id)
        delete_test_company(cls._away_store_2_company_id)
        delete_test_company(cls._company_id)

        dependencies.clear()


    def test_get_count_stores_by_company_id(self):
        # make sure the test company has the right count
        count_class_company = self._SQL_data_repository.get_count_stores_by_company_id(self._company_id)
        self.assertEqual(count_class_company, 1)

    def test_get_all_store_ids_with_company_ids(self):
        # get all store_id / company_ids from the db
        store_ids = self._SQL_data_repository.get_all_store_ids_with_company_ids()

        # variables to make sure the stores from the fake stores are in the list
        home_store_in_list = False
        away_store1_in_list = False
        away_store2_in_list = False

        # loop through store_ids making sure the three in the init are there
        for store in store_ids:
            if store.store_id == self._store_id and store.company_id == self._company_id:
                home_store_in_list = True
            elif store.store_id == self._away_store_1_id and store.company_id == self._away_store_1_company_id:
                away_store1_in_list = True
            elif store.store_id == self._away_store_2_id and store.company_id == self._away_store_2_company_id:
                away_store2_in_list = True

        self.assertTrue(home_store_in_list)
        self.assertTrue(away_store1_in_list)
        self.assertTrue(away_store2_in_list)

    def test_get_store_by_id(self):
        """
        This tests the main select statement for a store
        """
        # select store and verify it's properties
        store = self._SQL_data_repository.get_store_by_id(self._store_id)
        self.assertEqual(store.store_id, self._store_id)
        self.assertEqual(store.company_id, self._company_id)
        self.assertEqual(store.address_id, self._address_id)
        self.assertEqual(store.phone_number, "(000) 000-0000")
        self.assertEqual(str(store._opened_date), '2012-01-01 00:00:00')
        self.assertEqual(str(store._closed_date), '2012-12-01 00:00:00')
        self.assertEqual(str(store._assumed_opened_date), '2012-01-02 00:00:00')
        self.assertEqual(str(store._assumed_closed_date), '2012-12-02 00:00:00')

    def test_get_all_store_ids_from_company_id(self):
        """
        This test verifies that the get_all_store_ids_from_company_id data access function works properly
        """
        fake_company_id, fake_store1_id, fake_store2_id = None, None, None
        fake_address1_id, fake_address1_id = None, None
        try:
            #create fake company and two stores
            fake_company_id = insert_test_company('UNITTESTCOMPETITOR1')
            fake_address1_id = insert_test_address(-1, 1)
            fake_address2_id = insert_test_address(-1, 1)
            fake_store1_id = insert_test_store(fake_company_id, fake_address1_id)
            fake_store2_id = insert_test_store(fake_company_id, fake_address2_id)

            # select the stores and verify their content
            stores = self._SQL_data_repository.get_all_store_ids_from_company_id(fake_company_id)
            self.assertEqual(len(stores), 2)
            self.assertEqual(stores[0].store_id, fake_store1_id)
            self.assertEqual(stores[1].store_id, fake_store2_id)
        except:
            raise
        finally:
            #delete fake data
            if fake_store1_id:
                delete_test_store(fake_store1_id)
            if fake_store2_id:
                delete_test_store(fake_store2_id)
            if fake_address1_id:
                delete_test_address(fake_address1_id)
            if fake_address2_id:
                delete_test_address(fake_address2_id)
            if fake_company_id:
                delete_test_company(fake_company_id)


    def test_get_away_stores__all_stores(self):
        """
        Test to make sure the query gets all stores if no lat/long is passed in.
        we will create a third competitive store that a far away and we will make sure it's selected properly
        """
        fake_store1_id = None
        try:
            # crete third store that's far away
            fake_address1_id = insert_test_address(-100, 100)
            fake_store1_id = insert_test_store(self._away_store_2_company_id, fake_address1_id)

            away_stores = self._SQL_data_repository.get_away_stores_within_lat_long_range(self._store, None, None)
            away_stores = sorted(away_stores.values(), key = lambda store : store.away_store_id)

            # assert all stores are selected
            self.assertEqual(len(away_stores), 3)
            # assert first store
            self.assertEqual(away_stores[0].away_store_id, self._away_store_1_id)
            self.assertEqual(away_stores[0].company_id, self._away_store_1_company_id)
            self.assertEqual(away_stores[0].longitude, -1)
            self.assertEqual(away_stores[0].latitude, 1)
            self.assertEqual(str(away_stores[0]._opened_date), '2011-01-01 00:00:00')
            self.assertEqual(str(away_stores[0]._closed_date), '2011-12-01 00:00:00')
            self.assertEqual(str(away_stores[0]._assumed_opened_date), '2011-01-02 00:00:00')
            self.assertEqual(str(away_stores[0]._assumed_closed_date), '2011-12-02 00:00:00')
            # assert second store
            self.assertEqual(away_stores[1].away_store_id, self._away_store_2_id)
            self.assertEqual(away_stores[1].company_id, self._away_store_2_company_id)
            self.assertEqual(away_stores[1].longitude, -2)
            self.assertEqual(away_stores[1].latitude, 2)
            self.assertEqual(str(away_stores[1]._opened_date), '2011-01-01 00:00:00')
            self.assertEqual(str(away_stores[1]._closed_date), '2011-12-01 00:00:00')
            self.assertEqual(str(away_stores[1]._assumed_opened_date), '2011-01-02 00:00:00')
            self.assertEqual(str(away_stores[1]._assumed_closed_date), '2011-12-02 00:00:00')
            # assert second store
            self.assertEqual(away_stores[2].away_store_id, fake_store1_id)
            self.assertEqual(away_stores[2].company_id, self._away_store_2_company_id)
            self.assertEqual(away_stores[2].longitude, -100)
            self.assertEqual(away_stores[2].latitude, 100)
            self.assertEqual(away_stores[2]._opened_date, None)
            self.assertEqual(away_stores[2]._closed_date, None)
            self.assertEqual(away_stores[2]._assumed_opened_date, None)
            self.assertEqual(away_stores[2]._assumed_closed_date, None)
        except:
            raise
        finally:
            delete_test_store(fake_store1_id)
            delete_test_address(fake_address1_id)

    def test_get_away_stores_latitude__outside_range(self):
        """
        Test to make sure get_away_stores_within_lat_long_range works
        We will create 2 fake companies with three stores and test the select format against the created
        """

        #get lat long search range (1 degree) for store
        lat_long_search_range = GeographicalCoordinate(self._store.address.longitude, self._store.address.latitude).get_search_limits()

        #select competitors and make sure they match above structure
        away_stores = self._SQL_data_repository.get_away_stores_within_lat_long_range(self._store, lat_long_search_range["latitudes"], lat_long_search_range["longitudes"])
        away_stores = sorted(away_stores.values(), key = lambda store : store.away_store_id)

        # assert all stores are selected
        self.assertEqual(len(away_stores), 2)
        # assert first store
        self.assertEqual(away_stores[0].away_store_id, self._away_store_1_id)
        self.assertEqual(away_stores[0].company_id, self._away_store_1_company_id)
        self.assertEqual(away_stores[0].longitude, -1)
        self.assertEqual(away_stores[0].latitude, 1)
        self.assertEqual(str(away_stores[0]._opened_date), '2011-01-01 00:00:00')
        self.assertEqual(str(away_stores[0]._closed_date), '2011-12-01 00:00:00')
        self.assertEqual(str(away_stores[0]._assumed_opened_date), '2011-01-02 00:00:00')
        self.assertEqual(str(away_stores[0]._assumed_closed_date), '2011-12-02 00:00:00')
        # assert second store
        self.assertEqual(away_stores[1].away_store_id, self._away_store_2_id)
        self.assertEqual(away_stores[1].company_id, self._away_store_2_company_id)
        self.assertEqual(away_stores[1].longitude, -2)
        self.assertEqual(away_stores[1].latitude, 2)
        self.assertEqual(str(away_stores[1]._opened_date), '2011-01-01 00:00:00')
        self.assertEqual(str(away_stores[1]._closed_date), '2011-12-01 00:00:00')
        self.assertEqual(str(away_stores[1]._assumed_opened_date), '2011-01-02 00:00:00')
        self.assertEqual(str(away_stores[1]._assumed_closed_date), '2011-12-02 00:00:00')


    def test_get_away_stores_longitude__outside_range_close_to_180(self):
        """
        Test to make sure get_away_stores_within_lat_long_range works
        We will create 2 fake companies with three stores and test the select format against the created
        """
        new_company_id = insert_test_company()
        new_address_id = insert_test_address(-1, 1)
        new_store_id = insert_test_store(new_company_id, new_address_id)
        new_store = Store().select_by_id(new_store_id)

        try:
            #create fake company and stores for competitors
            fake_company1_id = insert_test_company('UNITTESTCOMPETITOR1')
            fake_company2_id = insert_test_company('UNITTESTCOMPETITOR2')
            #create fake competitor structure
            insert_test_competitor(new_company_id, fake_company1_id)
            insert_test_competitor(new_company_id, fake_company2_id)
            #create fake addresses for all stores
            fake_address1_id = insert_test_address(178.25, 1)
            fake_address2_id = insert_test_address(-179.75, 1)
            fake_address3_id = insert_test_address(-179, 1)
            #fake company 1 has 2 stores and fake company 2 has one store
            fake_store1_id = insert_test_store(fake_company1_id, fake_address1_id)
            fake_store2_id = insert_test_store(fake_company1_id, fake_address2_id)
            fake_store3_id = insert_test_store(fake_company2_id, fake_address3_id)

            #get lat long search range (1 degree) for store
            lat_long_search_range = GeographicalCoordinate(179.25, 1).get_search_limits()

            #select competitors and make sure they match above structure
            away_stores = self._SQL_data_repository.get_away_stores_within_lat_long_range(new_store,
                lat_long_search_range["latitudes"], lat_long_search_range["longitudes"])

            expected_away_stores = {fake_store1_id: StoreCompetitionInstance.basic_init(fake_store1_id, fake_company1_id, 1.0, 178.25),
                                    fake_store2_id: StoreCompetitionInstance.basic_init(fake_store2_id, fake_company1_id, 1.0, -179.75)}
            #the last company should be filtered out because it's outside the range

            self.assertEqual(expected_away_stores, away_stores)

        except:
            raise
        finally:
            #delete up fake companies and competitors
            delete_test_store(new_store_id)
            delete_test_address(new_address_id)
            delete_test_store(fake_store1_id)
            delete_test_store(fake_store2_id)
            delete_test_store(fake_store3_id)
            delete_test_address(fake_address1_id)
            delete_test_address(fake_address2_id)
            delete_test_address(fake_address3_id)
            delete_test_competitors(new_company_id)
            delete_test_company(fake_company1_id)
            delete_test_company(fake_company2_id)
            delete_test_company(new_company_id)


    def test_get_away_stores_longitude__outside_range_close_to_negative_180(self):
        """
        Test to make sure get_away_stores_within_lat_long_range works
        We will create 2 fake companies with three stores and test the select format against the created
        """
        new_company_id = insert_test_company()
        new_address_id = insert_test_address(-1, 1)
        new_store_id = insert_test_store(new_company_id, new_address_id)
        new_store = Store().select_by_id(new_store_id)


        fake_company1_id = None
        fake_company2_id = None
        fake_store1_id = None
        fake_store2_id = None
        fake_store3_id = None
        fake_address1_id = None
        fake_address2_id = None
        fake_address3_id = None
        try:
            #create fake company and stores for competitors
            fake_company1_id = insert_test_company('UNITTESTCOMPETITOR1')
            fake_company2_id = insert_test_company('UNITTESTCOMPETITOR2')
            #create fake competitor structure
            insert_test_competitor(new_company_id, fake_company1_id)
            insert_test_competitor(new_company_id, fake_company2_id)
            #create fake addresses for all stores
            fake_address1_id = insert_test_address(-178.25, 1)
            fake_address2_id = insert_test_address(179.75, 1)
            fake_address3_id = insert_test_address(1, 1)
            #fake company 1 has 2 stores and fake company 2 has one store
            fake_store1_id = insert_test_store(fake_company1_id, fake_address1_id)
            fake_store2_id = insert_test_store(fake_company1_id, fake_address2_id)
            fake_store3_id = insert_test_store(fake_company2_id, fake_address3_id)

            #get lat long search range (1 degree) for store
            lat_long_search_range = GeographicalCoordinate(-179.25, 1).get_search_limits()

            #select competitors and make sure they match above structure
            away_stores = self._SQL_data_repository.get_away_stores_within_lat_long_range(new_store,
                lat_long_search_range["latitudes"], lat_long_search_range["longitudes"])

            expected_away_stores = {fake_store1_id: StoreCompetitionInstance.basic_init(fake_store1_id, fake_company1_id, 1.0, -178.25),
                                    fake_store2_id: StoreCompetitionInstance.basic_init(fake_store2_id, fake_company1_id, 1.0, 179.75)}

            self.assertEqual(expected_away_stores, away_stores)

        except:
            raise
        finally:
            #delete up fake companies and competitors
            delete_test_store(new_store_id)
            delete_test_address(new_address_id)
            delete_test_store(fake_store1_id)
            delete_test_store(fake_store2_id)
            delete_test_store(fake_store3_id)
            delete_test_address(fake_address1_id)
            delete_test_address(fake_address2_id)
            delete_test_address(fake_address3_id)
            delete_test_competitors(new_company_id)
            delete_test_company(fake_company1_id)
            delete_test_company(fake_company2_id)
            delete_test_company(new_company_id)


    def test_get_away_stores_longitude__no_stores(self):
        """
        Test to make sure get_away_stores_within_lat_long_range returns {} for an empty set
        """
        try:
            new_company_id = insert_test_company()
            new_address_id = insert_test_address(-1, 1)
            new_store_id = insert_test_store(new_company_id, new_address_id)
            new_store = Store().select_by_id(new_store_id)

            #get lat long search range (1 degree) for store
            lat_long_search_range = GeographicalCoordinate(-179.25, 1).get_search_limits()

            #select competitors and make sure they match above structure
            away_stores = self._SQL_data_repository.get_away_stores_within_lat_long_range(new_store,
                lat_long_search_range["latitudes"], lat_long_search_range["longitudes"])

            self.assertEqual(away_stores, {})

        except:
            raise
        finally:
            #delete up fake companies and competitors
            delete_test_store(new_store_id)
            delete_test_address(new_address_id)
            delete_test_competitors(new_company_id)
            delete_test_company(new_company_id)


    def test_get_open_store_ids_and_open_dates_for_company_got_stores(self):
        try:
            # add two open stores
            test_address_id1 = insert_test_address(1, -1)
            test_store_id1 = insert_test_store(self._company_id, test_address_id1, "2012-01-01", None, "1900-01-10", None)
            test_store_id2 = insert_test_store(self._company_id, test_address_id1, "2012-01-02", None, "1900-01-12", None)

            # add two closed store, one with closed_date and one with assumed_closed_date
            test_store_id3 = insert_test_store(self._company_id, test_address_id1, "2012-01-01", "2012-05-01", "2012-01-10", None)
            test_store_id4 = insert_test_store(self._company_id, test_address_id1, "2012-01-02", None, "2012-01-12", "2012-05-01")

            company_info = CompanyInfo(company_name = 'Woot', source_name = 'Woot_2012_2_4.xlsx')
            company_info._company_id = self._company_id

            # query stores and make sure that only the opened stores are selected correctly
            stores = self._SQL_data_repository.get_open_store_ids_and_open_dates_for_company(company_info)
            self.assertEqual(len(stores), 2)
            self.assertEqual(stores[0].store_id, test_store_id1)
            self.assertEqual(str(stores[0]._opened_date), '2012-01-01 00:00:00')
            self.assertEqual(str(stores[0]._assumed_opened_date), '1900-01-10 00:00:00')
            self.assertEqual(stores[1].store_id, test_store_id2)
            self.assertEqual(str(stores[1]._opened_date), '2012-01-02 00:00:00')
            self.assertEqual(str(stores[1]._assumed_opened_date), '1900-01-12 00:00:00')
        except:
            raise
        finally:
            delete_test_store(test_store_id1)
            delete_test_store(test_store_id2)
            delete_test_store(test_store_id3)
            delete_test_store(test_store_id4)
            delete_test_address(test_address_id1)

    def test_get_open_store_ids_and_open_dates_for_company_got_no_stores(self):
        try:
            # add two open stores
            test_address_id1 = insert_test_address(1, -1)
            test_store_id1 = insert_test_store(self._company_id, test_address_id1, "2012-01-01", None, "2012-01-10", None)
            test_store_id2 = insert_test_store(self._company_id, test_address_id1, "2012-01-02", None, "2012-01-12", None)

            # add two closed store, one with closed_date and one with assumed_closed_date
            test_store_id3 = insert_test_store(self._company_id, test_address_id1, "2012-01-01", "2012-05-01", "2012-01-10", None)
            test_store_id4 = insert_test_store(self._company_id, test_address_id1, "2012-01-02", None, "2012-01-12", "2012-05-01")

            company_info = CompanyInfo(company_name = 'Woot', source_name = 'Woot_2011_2_4.xlsx')
            company_info._company_id = self._company_id

            # query stores and make sure that only the opened stores are selected correctly
            stores = self._SQL_data_repository.get_open_store_ids_and_open_dates_for_company(company_info)
            self.assertEqual(len(stores), 0)

        except:
            raise
        finally:
            delete_test_store(test_store_id1)
            delete_test_store(test_store_id2)
            delete_test_store(test_store_id3)
            delete_test_store(test_store_id4)
            delete_test_address(test_address_id1)


    def test_insert_store_return_with_new_store_id(self):
        try:
            # create fake company and address
            company_id = insert_test_company()
            address_id = insert_test_address(-40, 40)

            # create fake store
            store = Store.standard_init(None, company_id, address_id, "111-111-1111", "UNITTESTSTOREFORMAT", "UNITTESTCOMPANYGENERAGEDSTORENUMBER", "UNITETESTNOTE", None, None, "2012-02-02", None)

            # save store, which should initialize itself with the store_id and the change type
            store = self._SQL_data_repository.insert_store_return_with_new_store_id(store)

            # verify ID is set
            self.assertIsNotNone(store.store_id)

            # select store and verify fields
            store = Store.select_by_id(store.store_id)
            self.assertEqual(store.company_id, company_id)
            self.assertEqual(store.address_id, address_id)
            self.assertEqual(store.phone_number, "111-111-1111")
            self.assertEqual(store.note, "UNITETESTNOTE")
            self.assertEqual(store.store_format, "UNITTESTSTOREFORMAT")
            self.assertEqual(store.company_generated_store_number, "UNITTESTCOMPANYGENERAGEDSTORENUMBER")
            self.assertIsNone(store._opened_date)
            self.assertIsNone(store._closed_date)
            self.assertEqual(store._assumed_opened_date, datetime(2012, 2, 2))
            self.assertIsNone(store._assumed_closed_date)
        finally:
            delete_test_store(store.store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)

    def test_insert_store_return_with_new_store_id__different_phone_numbers(self):
        """
        two stores that have the same address id and company id but different phone numbers, make sure we get the right ones back
        """

        try:
            # create fake company and address
            company_id = insert_test_company()
            address_id = insert_test_address(-40, 40)

            # create fake store
            store = Store.standard_init(None, company_id, address_id, "111-111-1111", "UNITETESTFORMAT", None, None, None, None, "2012-02-02", None)
            store_2 = Store.standard_init(None, company_id, address_id, "111-111-1112", "UNITETESTFORMAT", None, None, None, None, "2012-02-02", None)

            # save store, which should initialize itself with the store_id and the change type
            store_returned = self._SQL_data_repository.insert_store_return_with_new_store_id(store)
            store_2_returned = self._SQL_data_repository.insert_store_return_with_new_store_id(store_2)

            self.assertIsNotNone(store.store_id)
            # verify store has id, correct fields, and correct change type
            self.assertEqual(store_returned.company_id, company_id)
            self.assertEqual(store_returned.address_id, address_id)
            self.assertEqual(store_returned.phone_number, "111-111-1111")
            self.assertIsNone(store_returned._opened_date)
            self.assertIsNone(store_returned._closed_date)
            self.assertEqual(store_returned._assumed_opened_date, "2012-02-02")
            self.assertIsNone(store_returned._assumed_closed_date)

            self.assertEqual(store_2_returned.phone_number, "111-111-1112")

        except:
            raise
        finally:
            delete_test_store(store.store_id)
            delete_test_store(store_2.store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)


    def test_get_matched_open_store_from_db_open_in_db(self):
        try:
            # create fake company and address
            company_id = insert_test_company()
            address_id = insert_test_address(-40, 40)
            phone_number = "(000) 000-0000"
            store_format = "UNITTESTSTOREFORMAT"

            # insert the fake store in order to test updated
            store_id = insert_test_store(company_id, address_id, assumed_opened_date = '2012-02-04', phone_number = phone_number, note = "UNITTESTNOTE", store_format = store_format)

            # query store and verify they right fields are queried correctly
            store_from_db = self._SQL_data_repository.get_matched_open_store_from_db(address_id, company_id, phone_number, store_format)
            self.assertEqual(store_from_db.store_id, store_id)
            self.assertEqual(store_from_db.address_id, address_id)
            self.assertEqual(store_from_db.company_id, company_id)
            self.assertEqual(store_from_db.phone_number, phone_number)
            self.assertEqual(store_from_db.note, "UNITTESTNOTE")
            self.assertEqual(store_from_db.store_format, store_format)
        except:
            raise
        finally:
            delete_test_store(store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)


    def test_get_matched_open_store_from_db_closed_in_db(self):
        try:
            # create fake company and address
            company_id = insert_test_company()
            address_id = insert_test_address(-40, 40)

            # insert the fake store in order to test updated
            store_id = insert_test_store(company_id, address_id, assumed_opened_date = '2012-02-04', assumed_closed_date = '2012-02-05', phone_number = '5555555555', store_format = "UNITTESTSTOREFORMAT")

            # create store object, with the same id as inserted store above, and with mismatched parameters
            store = Store()
            store.address_id = address_id
            store.company_id = company_id

            # save store, which should not insert, but should initialize itself the change type
            store_from_db = self._SQL_data_repository.get_matched_open_store_from_db(store.address_id, store.company_id, '5555555555', "UNITTESTSTOREFORMAT")

            # verify that the store has the right change type
            self.assertIsNone(store_from_db)

        except:
            raise
        finally:
            delete_test_store(store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)



    def test_close_old_stores(self):
        try:
            # create fake company and address
            company_id = insert_test_company()
            address_id = insert_test_address(-40, 40)

            # create two fake stores to close together
            store_id1 = insert_test_store(company_id, address_id)
            store_id2 = insert_test_store(company_id, address_id)

            # close both stores
            self._SQL_data_repository.close_old_stores([store_id1, store_id2], "2012-01-01")

            # select both stores and verify their close dates
            store1 = select_store_by_store_id(store_id1)
            store2 = select_store_by_store_id(store_id2)
            self.assertEqual(store1.assumed_closed_date, datetime(2012, 1, 1))
            self.assertEqual(store2.assumed_closed_date, datetime(2012, 1, 1))
        except:
            raise
        finally:
            delete_test_store(store_id1)
            delete_test_store(store_id2)
            delete_test_address(address_id)
            delete_test_company(company_id)

    def test_get_trade_area_by_store(self):
        trade_areas = self._store.select_trade_areas()
        self.assertEqual(len(trade_areas), 1)
        self.assertEqual(trade_areas[0].trade_area_id, self._trade_area.trade_area_id)


    def test_get_zip_by_zip_code(self):
        try:
            zip_code = insert_test_zip('11111', -10.24, 10.24)
            expected_zip = ZipCode.standard_init(zip_code, GeographicalCoordinate(-10.24, 10.24))
            test_zip = ZipCode.select_by_zip_code(zip_code)
            self.assertEquals(test_zip, expected_zip)
        except:
            raise
        finally:
            if zip_code:
                delete_test_zip(zip_code)

    def test_select_zips_within_range(self):
        try:
            store_id = None
            zip_code = None
            address_id = None
            company_id = None

            zip_code = insert_test_zip('11111', -10.24, 10.24)
            expected_zips = [ZipCode.standard_init(zip_code, GeographicalCoordinate(-10.24, 10.24))]

            # get a test store
            company_id = insert_test_company()
            address_id = insert_test_address(-10.24, 10.24)
            store_id = insert_test_store(company_id, address_id)

            #get lat long search range (1 degree) for store
            lat_long_search_range = GeographicalCoordinate(-10.24, 10.24).get_search_limits()
            # get zips in range
            zips = self._SQL_data_repository.get_zips_within_lat_long_range(lat_long_search_range['latitudes'], lat_long_search_range['longitudes'])

            self.assertEquals(zips, expected_zips)
        except:
            raise
        finally:
            delete_test_zip(zip_code)
            delete_test_store(store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)


    def test_update_store(self):
        try:
            # create test store
            company_id = insert_test_company()
            address_id = insert_test_address(-10.24, 10.24)
            store_id = insert_test_store(company_id, address_id)

            # select the store and update the note, format fields
            store = Store.select_by_id(store_id)
            store.note = "UNITTEST-NOTE-UPDATED"
            store.store_format = "UNITTEST-STOREFORAMT-UPDATED"

            # update the store
            self._SQL_data_repository.update_store(store)

            # re-select the store and verify that everything was updated properly
            store_updated = Store.select_by_id(store_id)
            self.assertEqual(store.note, "UNITTEST-NOTE-UPDATED")
            self.assertEqual(store.store_format, "UNITTEST-STOREFORAMT-UPDATED")
        finally:
            delete_test_store(store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)

if __name__ == '__main__':
    unittest.main()