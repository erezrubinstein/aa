import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.custom_analytics.data_checks.all_stores_have_counties_data_check import CustomAnalyticsStoresHaveCountiesDataCheck
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class AllStoresHaveCountiesDataCheckTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # insert a company
        cls.company_id = insert_test_company()

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create four stores
        cls.store_id_1 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_2 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_3 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_4 = insert_test_store(cls.company_id, cls.address_id)

        # create one county match for store 1 and two for store 2
        insert_county_store_match(1, cls.store_id_1)
        insert_county_store_match(1, cls.store_id_2)
        insert_county_store_match(2, cls.store_id_2)


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_from_county_store_matches()
        delete_all_stores(cls.company_id)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id)

        # clear the dependencies
        dependencies.clear()


    def test_all_stores_have_counties_data_check__failure(self):

        # create the data check and run it
        data_check_name, results = CustomAnalyticsStoresHaveCountiesDataCheck().run()

        # make sure the name is correct
        self.assertEqual(data_check_name, "All Stores Have at least one county")

        # make sure the results are correct
        self.assertEqual(results, {
            "headers": ["Store ID", "County Matches"],
            "rows": [
                {
                    "Store ID": self.store_id_3,
                    "County Matches": 0
                },
                {
                    "Store ID": self.store_id_4,
                    "County Matches": 0
                }
            ]
        })


    def test_all_stores_have_counties_data_check__success(self):

        # insert county matches for stores 3 and 4
        insert_county_store_match(1, self.store_id_3)
        insert_county_store_match(1, self.store_id_4)

        try:

            # create the data check and run it
            data_check_name, results = CustomAnalyticsStoresHaveCountiesDataCheck().run()

            # make sure the name is correct
            self.assertEqual(data_check_name, "All Stores Have at least one county")

            # verify that teh results are empty
            self.assertEqual(results, {})

        finally:

            # delete the store_matches we just created
            delete_county_store_matches_for_stores([self.store_id_3, self.store_id_4])