import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.custom_analytics.data_checks.store_count_data_check import CustomAnalyticsStoreCountsDataCheck
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class StoreCountsDataCheckTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # insert three companies
        cls.company_id_1 = insert_test_company(name = "Company 1")
        cls.company_id_2 = insert_test_company(name = "Company 2")
        cls.company_id_3 = insert_test_company(name = "Company 3")

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create a store for company 1 and none for companies 2 and three
        cls.store_id_1 = insert_test_store(cls.company_id_1, cls.address_id)


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_stores(cls.company_id_3)
        delete_all_stores(cls.company_id_2)
        delete_all_stores(cls.company_id_1)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id_3)
        delete_test_company(cls.company_id_2)
        delete_test_company(cls.company_id_1)

        # clear the dependencies
        dependencies.clear()


    def test_store_counts_data_check__failure(self):

        # create the data check and run it
        data_check_name, results = CustomAnalyticsStoreCountsDataCheck().run()

        # make sure the name is correct
        self.assertEqual(data_check_name, "All Companies Have At Least One Store")

        # make sure the results are correct
        self.assertEqual(results, {
            "headers": ["Company Name", "Store Count"],
            "rows": [
                {
                    "Company Name": "Company 2",
                    "Store Count": 0
                },
                {
                    "Company Name": "Company 3",
                    "Store Count": 0
                }
            ]
        })


    def test_store_counts_data_check__success(self):

        # create a store for the two other companies
        insert_test_store(self.company_id_2, self.address_id)
        insert_test_store(self.company_id_3, self.address_id)

        try:

            # create the data check and run it
            data_check_name, results = CustomAnalyticsStoreCountsDataCheck().run()

            # make sure the name is correct
            self.assertEqual(data_check_name, "All Companies Have At Least One Store")

            # verify that teh results are empty
            self.assertEqual(results, {})

        finally:

            # delete the stores
            delete_all_stores(self.company_id_3)
            delete_all_stores(self.company_id_2)