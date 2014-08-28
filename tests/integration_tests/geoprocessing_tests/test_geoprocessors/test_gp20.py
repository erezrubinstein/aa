import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access import store_handler
from geoprocessing.geoprocessors.regional_mapping_gps.gp20_stores_within_cbsa import GP20StoresWithinCBSA
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class GP20Tests(unittest.TestCase):

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
        cls.address_nyc = insert_test_address(-73.9400, 40.6700)

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


    def test_gp20(self):

        # get the nyc/sf cbsas (these ids are always the same - should be)
        nyc_cbsa = select_cbsa_by_id(255)
        sf_cbsa = select_cbsa_by_id(29)

        # get the store points
        stores = store_handler.get_store_points_by_store_ids([self.store_sf_1, self.store_sf_2, self.store_nyc_1, self.store_bosnia])

        # run all of the stores against these two cbsas
        GP20StoresWithinCBSA(nyc_cbsa, stores).simple_process()
        GP20StoresWithinCBSA(sf_cbsa, stores).simple_process()

        # query all matches
        matches = select_all_cbsa_matches()

        # convert matches to dicts, for easy comparing.  Also sort, for easy comparing.
        matches = sorted([
            { "cbsa_id": match.cbsa_id, "store_id": match.store_id }
            for match in matches
        ])

        # verify we got what we're looking for
        self.assertEqual(matches, sorted([
            {
                "cbsa_id": 255, # nyc
                "store_id": self.store_nyc_1
            },
            {
                "cbsa_id": 29, # sf
                "store_id": self.store_sf_1
            },
            {
                "cbsa_id": 29, # sf
                "store_id": self.store_sf_2
            }
        ]))

        # delete the matches that were created
        delete_all_from_cbsa_store_matches()