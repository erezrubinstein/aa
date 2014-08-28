import json
import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access import store_handler
from geoprocessing.geoprocessors.regional_mapping_gps.gp21_stores_within_county import GP21StoresWithinCounty
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class GP21Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # create a company
        cls.company_id = insert_test_company()

        # create two addresses in san fransisco (same exact address on purpose.  This tests a bug)
        cls.address_sf_1 = insert_test_address(-122.4167, 37.7833)
        cls.address_sf_2 = insert_test_address(-122.4167, 37.7833)

        # create an address in nyc
        cls.address_nyc = insert_test_address(-74.006605, 40.714623)

        # create an address that doesn't make sense
        cls.address_bosnia = insert_test_address(-1, 1)

        # create a store for each address
        cls.store_sf_1 = insert_test_store(cls.company_id, cls.address_sf_1)
        cls.store_sf_2 = insert_test_store(cls.company_id, cls.address_sf_2)
        cls.store_nyc_1 = insert_test_store(cls.company_id, cls.address_nyc)
        cls.store_bosnia = insert_test_store(cls.company_id, cls.address_bosnia)


    @classmethod
    def tearDownClass(cls):

        # delete the test data backwards
        delete_all_stores(cls.company_id)
        delete_test_address(cls.address_sf_1)
        delete_test_address(cls.address_sf_2)
        delete_test_address(cls.address_nyc)
        delete_test_address(cls.address_bosnia)
        delete_test_company(cls.company_id)

        # clear the dependencies
        dependencies.clear()


    def test_gp21(self):

        try:

            # get the nyc/sf counties (these ids are always the same - should be)
            nyc_cbsa = select_county_by_id(2448)
            sf_cbsa = select_county_by_id(637)

            # get the store points
            stores = store_handler.get_store_points_by_store_ids([self.store_sf_1, self.store_sf_2, self.store_nyc_1, self.store_bosnia])

            # run all of the stores against these two cbsas
            GP21StoresWithinCounty(nyc_cbsa, stores).simple_process()
            GP21StoresWithinCounty(sf_cbsa, stores).simple_process()

            # query all matches
            matches = select_all_county_matches()

            # convert matches to dicts, for easy comparing.  Also sort, for easy comparing.
            matches = sorted([
                { "county_id": match.county_id, "store_id": match.store_id }
                for match in matches
            ])

            # verify we got what we're looking for
            self.assertEqual(matches, sorted([
                {
                    "county_id": 2448, # nyc
                    "store_id": self.store_nyc_1
                },
                {
                    "county_id": 637, # sf
                    "store_id": self.store_sf_1
                },
                {
                    "county_id": 637, # sf
                    "store_id": self.store_sf_2
                }
            ]))

        finally:

            # delete the matches that were created
            delete_all_from_county_store_matches()


    def test_gp21__border(self):
        """
        Very specific test for a bug where stores on the border wouldn't count
        """

        try:

            # select the first county (doesn't matter which one)
            county = select_county_by_id(1)

            # get the shape of the county
            shape = json.loads(county.points_json)

            # create an address that's the same lat/long as the first point of the shape
            longitude = shape[0][0][0]
            latitude = shape[0][0][1]
            address_id = insert_test_address(longitude, latitude)

            # insert a new store with that address
            store_id = insert_test_store(self.company_id, address_id)

            # get the store points
            stores = store_handler.get_store_points_by_store_ids([store_id])

            # run geoprocessing
            GP21StoresWithinCounty(county, stores).simple_process()

            # query all matches
            matches = select_all_county_matches()

            # convert matches to dicts, for easy comparing.  Also sort, for easy comparing.
            matches = sorted([
                { "county_id": match.county_id, "store_id": match.store_id }
                for match in matches
            ])

            # verify we got what we're looking for
            self.assertEqual(matches, sorted([
                {
                    "county_id": 1, # nyc
                    "store_id": store_id
                }
            ]))

        finally:

            # delete the matches that were created
            delete_all_from_county_store_matches()

            # delete the store and address
            delete_test_store(store_id)
            delete_test_address(address_id)