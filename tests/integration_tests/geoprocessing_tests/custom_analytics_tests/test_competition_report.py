import pprint
import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from geoprocessing.custom_analytics.reports.custom_analytics_competition_report import CustomAnalyticsCompetitionReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class DemographicsAggregateReportTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # define two dates
        date_1 = datetime.datetime(1900, 1, 1)
        date_2 = datetime.datetime(2012, 1, 1)

        # define the time series for this report
        cls.time_series = [
            {
                "label": "t0",
                "date": date_1
            },
            {
                "label": "t1",
                "date": date_2
            }
        ]

        # insert 3 companies
        cls.company_id_1 = insert_test_company(name = "Company 1")
        cls.company_id_2 = insert_test_company(name = "Company 2")
        cls.company_id_3 = insert_test_company(name = "Company 3")

        # company 4 is a very specific bug in production where a company doesn't have stores in one period
        cls.company_id_4 = insert_test_company(name = "Company 4")

        # have all companies compete with all
        cls.company_competition_11 = insert_test_competitor(cls.company_id_1, cls.company_id_1)
        cls.company_competition_12 = insert_test_competitor(cls.company_id_1, cls.company_id_2)
        cls.company_competition_13 = insert_test_competitor(cls.company_id_1, cls.company_id_3)
        cls.company_competition_21 = insert_test_competitor(cls.company_id_2, cls.company_id_1)
        cls.company_competition_22 = insert_test_competitor(cls.company_id_2, cls.company_id_2)
        cls.company_competition_23 = insert_test_competitor(cls.company_id_2, cls.company_id_3)
        cls.company_competition_31 = insert_test_competitor(cls.company_id_3, cls.company_id_1)
        cls.company_competition_32 = insert_test_competitor(cls.company_id_3, cls.company_id_2)
        cls.company_competition_33 = insert_test_competitor(cls.company_id_3, cls.company_id_3)

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create a bunch of stores with different dates
        cls.test_store_1_1 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_2_1 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        cls.test_store_2_2 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        cls.test_store_2_3 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_2)
        cls.test_store_2_4 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_3_1 = insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_3_2 = insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_1)

        # company 4 has a store in date 2 only
        cls.test_store_4_1 = insert_test_store(cls.company_id_4, cls.address_id, assumed_opened_date = date_2)

        # create 2 trade areas for each store
        cls.trade_area_1_1_1 = insert_test_trade_area_raw(cls.test_store_1_1, 5)
        cls.trade_area_1_1_2 = insert_test_trade_area_raw(cls.test_store_1_1, 1)
        cls.trade_area_2_1_1 = insert_test_trade_area_raw(cls.test_store_2_1, 5)
        cls.trade_area_2_1_2 = insert_test_trade_area_raw(cls.test_store_2_1, 1)
        cls.trade_area_2_2_1 = insert_test_trade_area_raw(cls.test_store_2_2, 5)
        cls.trade_area_2_2_2 = insert_test_trade_area_raw(cls.test_store_2_2, 1)
        cls.trade_area_2_3_1 = insert_test_trade_area_raw(cls.test_store_2_3, 5)
        cls.trade_area_2_3_2 = insert_test_trade_area_raw(cls.test_store_2_3, 1)
        cls.trade_area_2_4_1 = insert_test_trade_area_raw(cls.test_store_2_4, 5)
        cls.trade_area_2_4_2 = insert_test_trade_area_raw(cls.test_store_2_4, 1)
        cls.trade_area_3_1_1 = insert_test_trade_area_raw(cls.test_store_3_1, 5)
        cls.trade_area_3_1_2 = insert_test_trade_area_raw(cls.test_store_3_1, 1)
        cls.trade_area_3_2_1 = insert_test_trade_area_raw(cls.test_store_3_2, 5)
        cls.trade_area_3_2_2 = insert_test_trade_area_raw(cls.test_store_3_2, 1)
        cls.trade_area_4_1_1 = insert_test_trade_area_raw(cls.test_store_4_1, 5)
        cls.trade_area_4_1_2 = insert_test_trade_area_raw(cls.test_store_4_1, 1)

        # create competition:
        # company_1's store competes with two of company 2's stores
        # for trade area 2, we only have one competition
        insert_test_competitive_store(cls.company_competition_12, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_2_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_12, cls.trade_area_1_1_2, cls.test_store_1_1, cls.test_store_2_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_12, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_2_2, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_12, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_2_3, date_2, None)

        # company_2's stores compete with all of company 1's stores, except store 2_4, which has no competition
        insert_test_competitive_store(cls.company_competition_21, cls.trade_area_2_1_1, cls.test_store_2_1, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_21, cls.trade_area_2_1_2, cls.test_store_2_1, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_21, cls.trade_area_2_2_1, cls.test_store_2_2, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_21, cls.trade_area_2_3_1, cls.test_store_2_3, cls.test_store_1_1, date_2, None)
        # have company 2's first two stores compete with each other for one trade area
        insert_test_competitive_store(cls.company_competition_22, cls.trade_area_2_1_1, cls.test_store_2_1, cls.test_store_2_2, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_22, cls.trade_area_2_2_1, cls.test_store_2_2, cls.test_store_2_1, date_1, date_2)

        # company 4 has no competition with anything... Specific production case

    @classmethod
    def tearDownClass(cls):

        # delete the data (backwards order of inserting)
        delete_all_competitive_stores([cls.test_store_1_1, cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4, cls.test_store_3_1, cls.test_store_3_2, cls.test_store_4_1])
        delete_all_trade_areas([cls.test_store_1_1, cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4, cls.test_store_3_1, cls.test_store_3_2, cls.test_store_4_1])
        delete_all_stores(cls.company_id_1)
        delete_all_stores(cls.company_id_2)
        delete_all_stores(cls.company_id_3)
        delete_all_stores(cls.company_id_4)
        delete_test_address(cls.address_id)
        delete_test_competitors(cls.company_id_1)
        delete_test_competitors(cls.company_id_2)
        delete_test_competitors(cls.company_id_3)
        delete_test_competitors(cls.company_id_4)
        delete_test_company(cls.company_id_1)
        delete_test_company(cls.company_id_2)
        delete_test_company(cls.company_id_3)
        delete_test_company(cls.company_id_4)

        # clear the dependencies
        dependencies.clear()


    def test_competition_report(self):

        # create the report
        report = CustomAnalyticsCompetitionReport(self.time_series)

        # truncate the report
        report.lets_make_a_run_for_the_border()

        # run the report
        report.taco_flavored_kisses()

        # query the report
        results = report.omg_they_killed_kenny()

        # group the results nicely, according to the excel logic
        excel_results = report._get_excel_data_sets(results)

        # make sure the results are correct
        self.assertEqual(excel_results, [
            {
                "label": "Competition Summary",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "5 Miles",
                        "headers": ["Banner", "t0 - Comp Ratio", "t1 - Comp Ratio", "t0 - % Store Base Affected", "t1 - % Store Base Affected", "t1 - Comp Ratio % Change", "t1 - % Store Base Affected - Change"],
                        "headers_comments": {
                            "t0 - Comp Ratio": "Competition Ratio; equivalent to Competition Instances divided by Home Stores.",
                            "t1 - Comp Ratio": "Competition Ratio; equivalent to Competition Instances divided by Home Stores.",
                            "t0 - % Store Base Affected": "The percentage of the banner's store base that has at least one competition instance.",
                            "t1 - % Store Base Affected": "The percentage of the banner's store base that has at least one competition instance.",
                            "t1 - Comp Ratio % Change": "% change in between the previous period and this period's Comp Ratio.",
                            "t1 - % Store Base Affected - Change": "% change in between the previous period and this period's % Store Base Affected."
                        },
                        "rows": [
                            {
                                "Banner": "Company 1",
                                "t0 - Comp Ratio": 2,
                                "t1 - Comp Ratio": 1,
                                "t0 - % Store Base Affected": 100,
                                "t1 - % Store Base Affected": 100,
                                "t1 - Comp Ratio % Change": -50,
                                "t1 - % Store Base Affected - Change": 0
                            },
                            {
                                "Banner": "Company 2",
                                "t0 - Comp Ratio": 1.33333,
                                "t1 - Comp Ratio": .5,
                                "t0 - % Store Base Affected": 66.66667,
                                "t1 - % Store Base Affected": 50,
                                "t1 - Comp Ratio % Change": -62.5,
                                "t1 - % Store Base Affected - Change": -25
                            },
                            {
                                "Banner": "Company 3",
                                "t0 - Comp Ratio": 0,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 0,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": 0,
                                "t1 - % Store Base Affected - Change": 0
                            },
                            {
                                "Banner": "Company 4",
                                "t0 - Comp Ratio": 0,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 0,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": 0,
                                "t1 - % Store Base Affected - Change": 0
                            }
                        ]
                    },
                    {
                        "header": "10 Miles",
                        "headers": ["Banner", "t0 - Comp Ratio", "t1 - Comp Ratio", "t0 - % Store Base Affected", "t1 - % Store Base Affected", "t1 - Comp Ratio % Change", "t1 - % Store Base Affected - Change"],
                        "headers_comments": {
                            "t0 - Comp Ratio": "Competition Ratio; equivalent to Competition Instances divided by Home Stores.",
                            "t1 - Comp Ratio": "Competition Ratio; equivalent to Competition Instances divided by Home Stores.",
                            "t0 - % Store Base Affected": "The percentage of the banner's store base that has at least one competition instance.",
                            "t1 - % Store Base Affected": "The percentage of the banner's store base that has at least one competition instance.",
                            "t1 - Comp Ratio % Change": "% change in between the previous period and this period's Comp Ratio.",
                            "t1 - % Store Base Affected - Change": "% change in between the previous period and this period's % Store Base Affected."
                        },
                        "rows": [
                            {
                                "Banner": "Company 1",
                                "t0 - Comp Ratio": 1,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 100,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": -100,
                                "t1 - % Store Base Affected - Change": -100
                            },
                            {
                                "Banner": "Company 2",
                                "t0 - Comp Ratio": .33333,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 33.33333,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": -100,
                                "t1 - % Store Base Affected - Change": -100
                            },
                            {
                                "Banner": "Company 3",
                                "t0 - Comp Ratio": 0,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 0,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": 0,
                                "t1 - % Store Base Affected - Change": 0
                            },
                            {
                                "Banner": "Company 4",
                                "t0 - Comp Ratio": 0,
                                "t1 - Comp Ratio": 0,
                                "t0 - % Store Base Affected": 0,
                                "t1 - % Store Base Affected": 0,
                                "t1 - Comp Ratio % Change": 0,
                                "t1 - % Store Base Affected - Change": 0
                            }
                        ]
                    }
                ]
            },
            {
                "headers": ["Home Banner", "Away Banner", "Trade Area", "Distinct Away Stores", "Competitive Instances", "Home Stores", "Competition Ratio", "Percent Store Base Affected"],
                "headers_comments": {
                    "Home Banner": "Competition metrics have a directionality. The home banner is the retailer that owns or operates the stores that experience competition from the away banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                    "Away Banner": "Competition metrics have a directionality. The away banner is the retailer that is exerting competitive pressure on the home banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                    "Distinct Away Stores": "Distinct away banner stores that compete with the home banner's stores.",
                    "Competitive Instances": "The number of times that a competitor store competes with the stores of this banner.",
                    "Home Stores": "The number of times that a competitor store competes with the stores of this banner.",
                    "Competition Ratio": "Competition Instances divided by Home Stores.",
                    "Percent Store Base Affected": "The percentage of the home banner's store base that has at least one competition instance with the away banner's stores."
                },
                "label": "t0 - detail",
                "rows": [
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 2,
                        "Competitive Instances": 2,
                        "Home Stores": 1,
                        "Competition Ratio": 2,
                        "Percent Store Base Affected": 100
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 1,
                        "Competitive Instances": 2,
                        "Home Stores": 3,
                        "Competition Ratio": 0.66667,
                        "Percent Store Base Affected": 66.66667
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 2,
                        "Competitive Instances": 2,
                        "Home Stores": 3,
                        "Competition Ratio": .66667,
                        "Percent Store Base Affected": 66.66667
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 3,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 3,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 1,
                        "Competitive Instances": 1,
                        "Home Stores": 1,
                        "Competition Ratio": 1,
                        "Percent Store Base Affected": 100
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 1,
                        "Competitive Instances": 1,
                        "Home Stores": 3,
                        "Competition Ratio": .33333,
                        "Percent Store Base Affected": 33.33333
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 3,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 3,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 3,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 0,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    }
                ]
            },
            {
                "headers": ["Home Banner", "Away Banner", "Trade Area", "Distinct Away Stores", "Competitive Instances", "Home Stores", "Competition Ratio", "Percent Store Base Affected"],
                "headers_comments": {
                    "Home Banner": "Competition metrics have a directionality. The home banner is the retailer that owns or operates the stores that experience competition from the away banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                    "Away Banner": "Competition metrics have a directionality. The away banner is the retailer that is exerting competitive pressure on the home banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                    "Distinct Away Stores": "Distinct away banner stores that compete with the home banner's stores.",
                    "Competitive Instances": "The number of times that a competitor store competes with the stores of this banner.",
                    "Home Stores": "The number of times that a competitor store competes with the stores of this banner.",
                    "Competition Ratio": "Competition Instances divided by Home Stores.",
                    "Percent Store Base Affected": "The percentage of the home banner's store base that has at least one competition instance with the away banner's stores."
                },
                "label": "t1 - detail",
                "rows":  [
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 1,
                        "Competitive Instances": 1,
                        "Home Stores": 1,
                        "Competition Ratio": 1,
                        "Percent Store Base Affected": 100
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 1,
                        "Competitive Instances": 1,
                        "Home Stores": 2,
                        "Competition Ratio": .5,
                        "Percent Store Base Affected": 50
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 1",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 2",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 3",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 4",
                        "Trade Area": "5 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 1",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 2",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 3",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 2,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 1",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 2",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 3",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    },
                    {
                        "Home Banner": "Company 4",
                        "Away Banner": "Company 4",
                        "Trade Area": "10 Miles",
                        "Distinct Away Stores": 0,
                        "Competitive Instances": 0,
                        "Home Stores": 1,
                        "Competition Ratio": 0,
                        "Percent Store Base Affected": 0
                    }
                ]
            }
        ])