from datetime import datetime
import unittest
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.zip_code import ZipCode
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from common.utilities.signal_math import SignalDecimal
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'erezrubinstein'


class StoreTests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

    def tearDown(self):
        dependencies.clear()

    def test_select_competitive_stores_within_range(self):
        store = Store.simple_init_with_address(43, 24, longitude = 1, latitude = -1)
        competitor_stores = store.select_stores_of_competitive_companies_within_range()

        # verify that we're using the real lat/long
        self.assertEqual(self._data_repository.latitude_range.start, SignalDecimal(-1.4))
        self.assertEqual(self._data_repository.latitude_range.stop, SignalDecimal(-0.6))
        self.assertEqual(len(self._data_repository.longitude_range), 1)
        self.assertEqual(self._data_repository.longitude_range[0].start, SignalDecimal(0.6))
        self.assertEqual(self._data_repository.longitude_range[0].stop, SignalDecimal(1.4))

    def test_select_stores_of_competitive_companies_within_old_problem_range(self):
        store = Store.simple_init_with_address(43, 24, longitude = 1, latitude = 1)
        store.problem_latitude = 50
        store.problem_longitude = -50
        competitor_stores = store.select_stores_of_competitive_companies_within_old_problem_range()

        # verify that we're using the problem lat/long
        self.assertEqual(self._data_repository.latitude_range.start, SignalDecimal(49.6))
        self.assertEqual(self._data_repository.latitude_range.stop, SignalDecimal(50.4))
        self.assertEqual(len(self._data_repository.longitude_range), 1)
        self.assertEqual(self._data_repository.longitude_range[0].start, SignalDecimal(-50.4))
        self.assertEqual(self._data_repository.longitude_range[0].stop, SignalDecimal(-49.6))

    def test_opened_date_property(self):
        # create three stores.  one with both dates, one with assumed date only, and one with no dates.
        # I kept end_dates in both just to verify the properties use the right internal field
        store_use_opened_date = Store.standard_init(1, 1, 1, None, None, None, None, "2012-01-01", "2012-12-01", "2012-01-02", "2012-12-02")
        store_use_assumed_opened_date = Store.standard_init(1, 1, 1, None, None, None, None, None, "2012-12-01", "2012-01-02", "2012-12-02")
        store_use_assumed_opened_date_min_date = Store.standard_init(1, 1, 1, None, None, None, None, datetime(1900, 1, 1), "2012-12-01", "2012-01-02", "2012-12-02")
        store_use_assumed_opened_date_min_date_str = Store.standard_init(1, 1, 1, None, None, None, None, "1900-01-01", "2012-12-01", "2012-01-02", "2012-12-02")
        store_no_date = Store.standard_init(1, 1, 1, None, None, None, None, None, "2012-12-01", None, "2012-12-02")

        # verify that each store has the right opened_date
        self.assertEqual(store_use_opened_date.opened_date, "2012-01-01")
        self.assertEqual(store_use_assumed_opened_date.opened_date, "2012-01-02")
        self.assertEqual(store_use_assumed_opened_date_min_date.opened_date, "2012-01-02")
        self.assertEqual(store_use_assumed_opened_date_min_date_str.opened_date, "2012-01-02")
        self.assertIsNone(store_no_date.opened_date)

    def test_closed_date_property(self):
        # create three stores.  one with both dates, one with assumed date only, and one with no dates.
        # I kept start_dates in both just to verify the properties use the right internal field
        store_use_closed_date = Store.standard_init(1, 1, 1, None, None, None, None, "2012-01-01", "2012-12-01", "2012-01-02", "2012-12-02")
        store_use_assumed_closed_date = Store.standard_init(1, 1, 1, None, None, None, None, "2012-01-01", None, "2012-01-02", "2012-12-02")
        store_no_date = Store.standard_init(1, 1, 1, None, None, None, None, "2012-01-01", None, "2012-01-02", None)

        # verify that each store has the right opened_date
        self.assertEqual(store_use_closed_date.closed_date, "2012-12-01")
        self.assertEqual(store_use_assumed_closed_date.closed_date, "2012-12-02")
        self.assertIsNone(store_no_date.closed_date)

    def test_address_property(self):
        store = Store()
        store.address_id = 100

        # mock address
        address = Address.standard_init(100, 999, None, None, None, None, None, None, None, None, None)
        self._data_repository.addresses[100] = address

        # get store address and verify it's id matches our mock
        self.assertEqual(store.address.street_number, 999)


    def test_select_zips_within_range(self):
        #set up a test store with a specific zip code and lat/long
        store = Store.simple_init_with_address(44, 24, longitude = 10.24, latitude = 10.24)
        store.address.zip_code = "12345"
        centroid = GeographicalCoordinate(store.address.longitude, store.address.latitude)

        # the mock data repo makes a single-item list of zip codes
        # using the store's own zip code and lat/long
        expected_zips = [ZipCode.standard_init(store.address.zip_code, centroid)]
        self._data_repository.zips = expected_zips

        test_zips = store.select_zips_within_range()
        self.assertEqual(test_zips, expected_zips)

if __name__ == '__main__':
    unittest.main()