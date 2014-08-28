import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.data_checks.trade_area_competition_or_monopolies_data_check import CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck
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

        # create a company competition record
        cls.company_competition_id = insert_test_competitor(cls.company_id, cls.company_id)

        # create competition and monopolies for the first trade area
        insert_test_competitive_store(cls.company_competition_id, cls.trade_area_id_1, cls.store_id_1, cls.store_id_2, None, None)
        insert_test_monopoly(cls.trade_area_id_1, cls.store_id_1)

        # create a competition for trade area 2
        insert_test_competitive_store(cls.company_competition_id, cls.trade_area_id_2, cls.store_id_2, cls.store_id_3, None, None)

        # create a monopoly for trade area 3
        insert_test_monopoly(cls.trade_area_id_3, cls.store_id_3)

        # nothing for trade area 4 (which will be the bad one)


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_monopolies([cls.trade_area_id_1, cls.trade_area_id_2, cls.trade_area_id_3, cls.trade_area_id_4])
        delete_all_competitive_stores([cls.store_id_1, cls.store_id_2, cls.store_id_3, cls.store_id_4])
        delete_test_competitors(cls.company_id)
        delete_all_trade_areas([cls.store_id_1, cls.store_id_2, cls.store_id_3, cls.store_id_4])
        delete_all_stores(cls.company_id)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id)

        # clear the dependencies
        dependencies.clear()


    def test_trade_area_competition_data_check__failure(self):

        # run the data check
        data_check_name, results = CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck().run()

        # make sure the name is correct
        self.assertEqual(data_check_name, "All Trade Areas Have Competition or Monopolies")

        # create the expected sql
        expected_sql = """
        select t.trade_area_id, competition.count as competition_count, monopolies.count as monopolies_count
        from trade_areas t
        cross apply
        (
            select count(*) as count
            from competitive_stores cs
            where cs.trade_area_id = t.trade_area_id
        ) competition
        cross apply
        (
            select count(*) as count
            from monopolies m
            where m.trade_area_id = t.trade_area_id
        ) monopolies
        where competition.count = 0 and monopolies.count = 0"""

        # make sure the results are correct
        self.assertEqual(results, {
            "headers": ["# Incorrect Trade Areas", "SQL"],
            "rows": [
                {
                "# Incorrect Trade Areas": 1,
                "SQL": expected_sql
                }
            ]
        })


    def test_trade_area_competition_data_check__success(self):

        # add a monopoly to the fourth trade area, so that it passes
        insert_test_monopoly(self.trade_area_id_4, self.store_id_4)

        try:

            # run the data check
            data_check_name, results = CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck().run()

            # make sure the name is correct
            self.assertEqual(data_check_name, "All Trade Areas Have Competition or Monopolies")

            # make sure it passes
            self.assertEqual(results, {})

        finally:

            # delete the monopoly
            delete_all_monopolies([self.trade_area_id_4])