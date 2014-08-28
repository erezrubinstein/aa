from datetime import datetime
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.geographical_coordinate import Range
from geoprocessing.business_logic.business_objects.store import Store
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from common.utilities.signal_math import SignalDecimal
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_store, delete_test_store, delete_test_address, delete_test_competitors, insert_test_address, insert_test_company, delete_test_company, insert_test_problem_address, delete_test_problem_address, select_address_by_address_id

__author__ = 'erezrubinstein'

import unittest

class AddressDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

        # insert test data
        cls._company_id = insert_test_company()
        cls._address_id = insert_test_address(-1.2, 1.2)
        cls._store_id = insert_test_store(cls._company_id, cls._address_id)
        cls._problem_address_id = insert_test_problem_address(cls._store_id, 25.2, 25.2)

    @classmethod
    def tearDownClass(cls):
        # delete test data
        if cls._store_id is not None:
            delete_test_store(cls._store_id)
        if cls._address_id is not None:
            delete_test_address(cls._address_id)
        if cls._problem_address_id is not None:
            delete_test_problem_address(cls._problem_address_id)
        if cls._company_id is not None:
            delete_test_competitors(cls._company_id)
        if cls._company_id is not None:
            delete_test_company(cls._company_id)

        dependencies.clear()

    def test_get_address_by_id(self):
        """
        This test verifies that we can properly select address by it's store_id
        """
        address = self._SQL_data_repository.get_address_by_id(self._address_id)
        self.assertEquals(address.address_id, self._address_id)
        self.assertEquals(address.street_number, str(0))
        self.assertEquals(address.street, "UNITTEST")
        self.assertEquals(address.city, "UNITTEST")
        self.assertEquals(address.state, "NY")
        self.assertEquals(address.zip_code, "11111")
        self.assertEquals(address.country_id, 840)
        self.assertEquals(address.latitude, SignalDecimal(1.200000))
        self.assertEquals(address.longitude, SignalDecimal(-1.200000))


    def test_get_long_lat_problem_address(self):
        store = Store().select_by_id(self._store_id)
        long_lat_tup = self._SQL_data_repository.get_problem_long_lat(store)
        self.assertEqual(long_lat_tup.longitude, SignalDecimal(25.200000))
        self.assertEqual(long_lat_tup.latitude, SignalDecimal(25.200000))


    def test_mark_mopped(self):
        store = Store().select_by_id(self._store_id)
        self.assertFalse(self._SQL_data_repository.is_already_mopped(store))
        self._SQL_data_repository.mark_as_mopped(store)
        self.assertTrue(self._SQL_data_repository.is_already_mopped(store))


    def test_select_addresses_within_range__positive_match(self):
        latitudes = Range(-2.2, 2.2)
        # I pass in two ranges to make sure the query handles it properly
        longitudes = [Range(-5.2, -4.2), Range(-2.2, 2.2)]

        # query addresses as ids
        addresses = self._SQL_data_repository.select_addresses_within_range(longitudes, latitudes)
        addresses = [address.address_id for address in addresses]

        # make sure id is within ids
        self.assertIn(self._address_id, addresses)

    def test_select_addresses_within_range__negative_match(self):
        latitudes = Range(-50.3, -48.3)
        # I pass in two ranges to make sure the query handles it properly
        longitudes = [Range(-2.3, 2.3)]

        # query addresses as ids
        addresses = self._SQL_data_repository.select_addresses_within_range(longitudes, latitudes)
        addresses = [address.address_id for address in addresses]

        # make sure id is within ids
        self.assertNotIn(self._address_id, addresses)


    def test_select_addresses_within_range__company_filter(self):
        try:
            # create same address, but different company
            company_id = insert_test_company()
            address_id = insert_test_address(-1.2, 1.2)
            store_id = insert_test_store(company_id, address_id)

            latitudes = Range(-2.2, 2.2)
            # I pass in two ranges to make sure the query handles it properly
            longitudes = [Range(-5.2, -4.2), Range(-2.2, 2.2)]

            # query addresses as ids and verify both companies found
            addresses = self._SQL_data_repository.select_addresses_within_range(longitudes, latitudes)
            addresses = [address.address_id for address in addresses]
            self.assertIn(self._address_id, addresses)
            self.assertIn(address_id, addresses)

            # query addresses as ids with the home company id and verify only one shows up
            addresses = self._SQL_data_repository.select_addresses_within_range(longitudes, latitudes, self._company_id)
            addresses = [address.address_id for address in addresses]
            self.assertIn(self._address_id, addresses)
            self.assertNotIn(address_id, addresses)
        finally:
            delete_test_store(store_id)
            delete_test_address(address_id)
            delete_test_company(company_id)

    def test_insert_new_address_get_id__all_fields_filled_in(self):
        address = None
        try:
            # create address object and insert it
            suite_numbers = ['100', '200']
            address = Address.complex_init_for_loader(None, '10', "UNITTESTSTREET", "UNITTESTCITY", "NJ", '10000', 840, 1, 1, None, datetime(2012, 01, 01), None, suite_numbers, "UNITTESTCOMPLEX")
            address = self._SQL_data_repository.insert_new_address_get_id(address)

            # select and verify its values
            address_db = select_address_by_address_id(address.address_id)
            self.assertEqual(address_db.address_id, address.address_id)
            self.assertEqual(address_db.street_number, str(address.street_number))
            self.assertEqual(address_db.street, address.street)
            self.assertEqual(address_db.municipality, address.city)
            self.assertEqual(address_db.governing_district, address.state)
            self.assertEqual(address_db.postal_area, str(address.zip_code))
            self.assertEqual(address_db.country_id, address.country_id)
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.suite, "100, 200")
            self.assertEqual(address_db.shopping_center_name, address.complex)
            self.assertEqual(address_db.min_source_date, datetime(2012, 1, 1))
            self.assertEqual(address_db.max_source_date, datetime(2012, 1, 1))


            # test that re-inserting the same address does not insert, but does select the same id
            # create a copy and re-insert it
            address_copy = Address.complex_init_for_loader(None, 10, "UNITTESTSTREET", "UNITTESTCITY", "UNITTESTSTATE", 10000, 840, 1, 1, None, datetime(2012, 01, 01), None, suite_numbers, "UNITTESTCOMPLEX")
            address_copy = select_address_by_address_id(address.address_id)

            # verify that the addresses' ids match
            self.assertEqual(address_copy.address_id, address_db.address_id)
        except:
            raise
        finally:
            if address and address.address_id:
                delete_test_address(address.address_id)


    def test_insert_new_address_get_id__several_null_fields(self):
        address = None
        try:
            # create address object and insert it
            # VERY important: country_id, suite_numbers, and complex are all None.  that is the essense of this test
            address = Address.complex_init_for_loader(None, '10', "UNITTESTSTREET", "UNITTESTCITY", "NJ", 10000, None, 1, 1, None, datetime(2012, 01, 01), None, None, None)
            address = self._SQL_data_repository.insert_new_address_get_id(address)

            # select and verify its values
            address_db = select_address_by_address_id(address.address_id)
            self.assertEqual(address_db.address_id, address.address_id)
            self.assertEqual(address_db.street_number, str(address.street_number))
            self.assertEqual(address_db.street, address.street)
            self.assertEqual(address_db.municipality, address.city)
            self.assertEqual(address_db.governing_district, address.state)
            self.assertEqual(address_db.postal_area, str(address.zip_code))
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.min_source_date, datetime(2012, 1, 1))
            self.assertEqual(address_db.max_source_date, datetime(2012, 1, 1))
            # assert the several null fields inserted before
            self.assertIsNone(address_db.suite)
            self.assertIsNone(address_db.shopping_center_name)
            self.assertIsNone(address_db.country_id)


            # test that re-inserting the same address does not insert, but does select the same id
            # create a copy and re-insert it
            address_copy = Address.complex_init_for_loader(None, '10', "UNITTESTSTREET", "UNITTESTCITY", "UNITTESTSTATE", 10000, 840, 1, 1, None, datetime(2012, 01, 01), None, None, None)
            address_copy = select_address_by_address_id(address.address_id)

            # verify that the addresses' ids match
            self.assertEqual(address_copy.address_id, address_db.address_id)
        except:
            raise
        finally:
            if address and address.address_id:
                delete_test_address(address.address_id)


    def test_update_address(self):
        address = None
        try:
            # create address object and insert it
            suite_numbers = [100, 200]
            address = Address.complex_init_for_loader(None, '10', "UNITTESTSTREET", "UNITTESTCITY", "NJ", 10000, 840, 1, 1, None, datetime(2012, 1, 1), None, suite_numbers, "UNITTESTCOMPLEX")
            address = self._SQL_data_repository.insert_new_address_get_id(address)

            # update the address with new values
            address.street_number = 10
            address.street = "UNITTESTSTREETUPDATED"
            address.city = "UNITTESTCITYUPDATED"
            address.state = "NY"
            address.zip_code = 20000
            address.latitude = 2
            address.longitude = 2
            address.country_id = 4
            address.source_date = datetime(2012, 05, 05)
            address.suite_numbers = str([300, 400])
            address.complex = "UNITTESTCOMPLEXUPDAETD"
            self._SQL_data_repository.update_address(address)

            # select address and verify the updated values
            address_db = select_address_by_address_id(address.address_id)
            self.assertEqual(address_db.address_id, address.address_id)
            self.assertEqual(address_db.street_number, str(address.street_number))
            self.assertEqual(address_db.street, address.street)
            self.assertEqual(address_db.municipality, address.city)
            self.assertEqual(address_db.governing_district, address.state)
            self.assertEqual(address_db.postal_area, str(address.zip_code))
            self.assertEqual(address_db.country_id, address.country_id)
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.latitude, address.latitude)
            self.assertEqual(address_db.suite, "[300, 400]")
            self.assertEqual(address_db.shopping_center_name, address.complex)
            self.assertEqual(address_db.min_source_date, datetime(2012, 1, 1))
            self.assertEqual(address_db.max_source_date, datetime(2012, 5, 5))

            # update one more time with an empty suite number to make sure the list null is handled correctly
            address.suite_numbers = None
            self._SQL_data_repository.update_address(address)
            address_db = select_address_by_address_id(address.address_id)
            self.assertIsNone(address_db.suite)
        except:
            raise
        finally:
            if address and address.address_id:
                delete_test_address(address.address_id)

if __name__ == '__main__':
    unittest.main()
