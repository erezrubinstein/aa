import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.data_checks.trade_areas_exist_data_check import CustomAnalyticsTradeAreaExistsDataCheck
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class TradeAreaExistsDataCheckTests(unittest.TestCase):

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

        # create all three trade areas for store 1
        insert_test_trade_area_raw(cls.store_id_1, TradeAreaThreshold.DistanceMiles1)
        insert_test_trade_area_raw(cls.store_id_1, TradeAreaThreshold.DistanceMiles2)
        insert_test_trade_area_raw(cls.store_id_1, TradeAreaThreshold.DistanceMiles10)

        # for stores 2, 3, 4, create 2 out of 3 trade areas for each.
        # each store is missing a different trade area
        insert_test_trade_area_raw(cls.store_id_2, TradeAreaThreshold.DistanceMiles2)
        insert_test_trade_area_raw(cls.store_id_2, TradeAreaThreshold.DistanceMiles10)
        insert_test_trade_area_raw(cls.store_id_3, TradeAreaThreshold.DistanceMiles1)
        insert_test_trade_area_raw(cls.store_id_3, TradeAreaThreshold.DistanceMiles10)
        insert_test_trade_area_raw(cls.store_id_4, TradeAreaThreshold.DistanceMiles1)
        insert_test_trade_area_raw(cls.store_id_4, TradeAreaThreshold.DistanceMiles2)

        # update the config to make sure it's doing the right thing
        cls._config = Dependency("Config").value
        cls._config.trade_area_thresholds = ["DistanceMiles1", "DistanceMiles2", "DistanceMiles10"]


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_trade_areas([cls.store_id_1, cls.store_id_2, cls.store_id_3, cls.store_id_4])
        delete_all_stores(cls.company_id)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id)

        # reset the config so it doesn't affect other tests
        Config.instance = None

        # clear the dependencies
        dependencies.clear()


    def test_trade_area_exists_data_check__failure(self):

        # create the data check and run it
        data_check_name, results = CustomAnalyticsTradeAreaExistsDataCheck().run()

        # make sure the name is correct
        self.assertEqual(data_check_name, "All Trade Areas Exist")

        # create the expected sql
        expected_sql = """
        select s.store_id, t_4.threshold_id, t_12.threshold_id, t_1.threshold_id
        from stores s
        left join trade_areas t_4 on t_4.store_id = s.store_id and t_4.threshold_id = 4\nleft join trade_areas t_12 on t_12.store_id = s.store_id and t_12.threshold_id = 12\nleft join trade_areas t_1 on t_1.store_id = s.store_id and t_1.threshold_id = 1
        where t_4.threshold_id is null or t_12.threshold_id is null or t_1.threshold_id is null
        """

        # make sure the results are correct
        self.assertEqual(results, {
            "headers": ["# Incorrect Stores", "SQL"],
            "rows": [
                {
                "# Incorrect Stores": 3,
                "SQL": expected_sql
                }
            ]
        })


    def test_trade_area_exists_data_check__success(self):

        # create the missing trade areas
        trade_area_id_1 = insert_test_trade_area_raw(self.store_id_2, TradeAreaThreshold.DistanceMiles1)
        trade_area_id_2 = insert_test_trade_area_raw(self.store_id_3, TradeAreaThreshold.DistanceMiles2)
        trade_area_id_3 = insert_test_trade_area_raw(self.store_id_4, TradeAreaThreshold.DistanceMiles10)

        try:

            # create the data check and run it
            data_check_name, results = CustomAnalyticsTradeAreaExistsDataCheck().run()

            # make sure the name is correct
            self.assertEqual(data_check_name, "All Trade Areas Exist")

            # verify that teh results are empty
            self.assertEqual(results, {})


        finally:

            # delete the trade areas
            delete_test_trade_area_by_trade_area_id(trade_area_id_1)
            delete_test_trade_area_by_trade_area_id(trade_area_id_2)
            delete_test_trade_area_by_trade_area_id(trade_area_id_3)