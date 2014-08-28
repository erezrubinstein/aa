import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.data_checks.trade_area_demographics_count_data_check import CustomAnalyticsTradeAreaDemographicCountsDataCheck
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class TradeAreaDemographicsCountDataCheckTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # insert a company
        cls.company_id = insert_test_company()

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create a bunch of stores
        cls.store_id_1 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_2 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_3 = insert_test_store(cls.company_id, cls.address_id)
        cls.store_id_4 = insert_test_store(cls.company_id, cls.address_id)

        # insert a trade area for every store
        cls.trade_area_id_1 = insert_test_trade_area_raw(cls.store_id_1, TradeAreaThreshold.DistanceMiles10)
        cls.trade_area_id_2 = insert_test_trade_area_raw(cls.store_id_2, TradeAreaThreshold.DistanceMiles10)
        cls.trade_area_id_3 = insert_test_trade_area_raw(cls.store_id_3, TradeAreaThreshold.DistanceMiles10)
        cls.trade_area_id_4 = insert_test_trade_area_raw(cls.store_id_4, TradeAreaThreshold.DistanceMiles10)

        # insert two demographics for store 1
        insert_test_demographic(cls.trade_area_id_1, 10, 10)
        insert_test_demographic(cls.trade_area_id_1, 13, 13)

        # insert one demographic for the three other trade areas
        insert_test_demographic(cls.trade_area_id_2, 10, 10)
        insert_test_demographic(cls.trade_area_id_3, 10, 10)
        insert_test_demographic(cls.trade_area_id_4, 10, 10)


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_demographic_num_and_str_values(cls.trade_area_id_1)
        delete_demographic_num_and_str_values(cls.trade_area_id_2)
        delete_demographic_num_and_str_values(cls.trade_area_id_3)
        delete_demographic_num_and_str_values(cls.trade_area_id_4)
        delete_all_trade_areas([cls.store_id_1, cls.store_id_2, cls.store_id_3, cls.store_id_4])
        delete_all_stores(cls.company_id)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id)

        # clear the dependencies
        dependencies.clear()


    def test_demographic_counts_data_check__failure(self):

        # run the data check
        data_check_name, results = CustomAnalyticsTradeAreaDemographicCountsDataCheck().run()

        # make sure the name is correct
        self.assertEqual(data_check_name, "Trade Area Demographic Counts Check")

        # create the expected sql
        expected_sql = """
        select t.trade_area_id, count(distinct d.data_item_id) as count
        from trade_areas t
        left join demographic_numvalues d on d.trade_area_id = t.trade_area_id
        group by t.trade_area_id
        order by count(distinct d.data_item_id) desc"""

        # make sure the results are correct
        self.assertEqual(results, {
            "headers": ["# Incorrect Trade Areas", "SQL"],
            "rows": [
                {
                "# Incorrect Trade Areas": 3,
                "SQL": expected_sql
                }
            ]
        })


    def test_demographic_counts_data_check__success(self):

        # add the missing demographics
        demographics_id_1 = insert_test_demographic(self.trade_area_id_2, 13, 13)
        demographics_id_2 = insert_test_demographic(self.trade_area_id_3, 13, 13)
        demographics_id_3 = insert_test_demographic(self.trade_area_id_4, 13, 13)

        try:

            # run the data check
            data_check_name, results = CustomAnalyticsTradeAreaDemographicCountsDataCheck().run()

            # make sure the name is correct
            self.assertEqual(data_check_name, "Trade Area Demographic Counts Check")

            # make sure the results are correct
            self.assertEqual(results, {})

        finally:

            # clean up after these demographics
            delete_demographic_num_value_by_demographics_id(demographics_id_1)
            delete_demographic_num_value_by_demographics_id(demographics_id_2)
            delete_demographic_num_value_by_demographics_id(demographics_id_3)