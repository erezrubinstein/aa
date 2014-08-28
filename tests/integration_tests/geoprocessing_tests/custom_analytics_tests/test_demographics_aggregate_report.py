import pprint
import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from geoprocessing.custom_analytics.reports.custom_analytics_demographics_aggregate_report import CustomAnalyticsDemographicsAggregateReport
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

        # insert 2 companies
        cls.company_id_1 = insert_test_company(name = "Company 1")
        cls.company_id_2 = insert_test_company(name = "Company 2")

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create five stores for company 1, with two openings and two closings in the second period
        cls.test_store_1_1 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_1_2 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        cls.test_store_1_3 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        cls.test_store_1_4 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_2)
        cls.test_store_1_5 = insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_2)

        # create 3 stores for company 2 (no openings/closings)
        cls.test_store_2_1 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_2_2 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_2_3 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)
        cls.test_store_2_4 = insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)

        # insert two trade areas for each store 5 mile and 10 mile
        cls.trade_area_1_1_1 = insert_test_trade_area_raw(cls.test_store_1_1, 5)
        cls.trade_area_1_1_2 = insert_test_trade_area_raw(cls.test_store_1_1, 1)
        cls.trade_area_1_2_1 = insert_test_trade_area_raw(cls.test_store_1_2, 5)
        cls.trade_area_1_2_2 = insert_test_trade_area_raw(cls.test_store_1_2, 1)
        cls.trade_area_1_3_1 = insert_test_trade_area_raw(cls.test_store_1_3, 5)
        cls.trade_area_1_3_2 = insert_test_trade_area_raw(cls.test_store_1_3, 1)
        cls.trade_area_1_4_1 = insert_test_trade_area_raw(cls.test_store_1_4, 5)
        cls.trade_area_1_4_2 = insert_test_trade_area_raw(cls.test_store_1_4, 1)
        cls.trade_area_1_5_1 = insert_test_trade_area_raw(cls.test_store_1_5, 5)
        cls.trade_area_1_5_2 = insert_test_trade_area_raw(cls.test_store_1_5, 1)
        cls.trade_area_2_1_1 = insert_test_trade_area_raw(cls.test_store_2_1, 5)
        cls.trade_area_2_1_2 = insert_test_trade_area_raw(cls.test_store_2_1, 1)
        cls.trade_area_2_2_1 = insert_test_trade_area_raw(cls.test_store_2_2, 5)
        cls.trade_area_2_2_2 = insert_test_trade_area_raw(cls.test_store_2_2, 1)
        cls.trade_area_2_3_1 = insert_test_trade_area_raw(cls.test_store_2_3, 5)
        cls.trade_area_2_3_2 = insert_test_trade_area_raw(cls.test_store_2_3, 1)
        cls.trade_area_2_4_1 = insert_test_trade_area_raw(cls.test_store_2_4, 5)
        cls.trade_area_2_4_2 = insert_test_trade_area_raw(cls.test_store_2_4, 1)

        # create company competition with themselves
        cls.company_competition_1 = insert_test_competitor(cls.company_id_1, cls.company_id_1)
        cls.company_competition_2 = insert_test_competitor(cls.company_id_2, cls.company_id_2)

        # create competition for stores of company 1
        # store 1 competes with 2, 3, 4 (and vice versa)
        # store 5 has no competition
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_1_2, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_2, cls.test_store_1_1, cls.test_store_1_2, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_1_3, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_2, cls.test_store_1_1, cls.test_store_1_3, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_1, cls.test_store_1_1, cls.test_store_1_4, date_2, None)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_1_2, cls.test_store_1_1, cls.test_store_1_4, date_2, None)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_2_1, cls.test_store_1_2, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_2_2, cls.test_store_1_2, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_3_1, cls.test_store_1_3, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_3_2, cls.test_store_1_3, cls.test_store_1_1, date_1, date_2)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_4_1, cls.test_store_1_4, cls.test_store_1_1, date_2, None)
        insert_test_competitive_store(cls.company_competition_1, cls.trade_area_1_4_2, cls.test_store_1_4, cls.test_store_1_1, date_2, None)

        # create competition for stores of company 2
        # store 1 competes with 2, 3
        # store 4 has no competition
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_1_1, cls.test_store_2_1, cls.test_store_2_2, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_1_2, cls.test_store_2_1, cls.test_store_2_2, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_1_1, cls.test_store_2_1, cls.test_store_2_3, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_1_2, cls.test_store_2_1, cls.test_store_2_3, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_2_1, cls.test_store_2_2, cls.test_store_2_1, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_2_2, cls.test_store_2_2, cls.test_store_2_1, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_3_1, cls.test_store_2_3, cls.test_store_2_1, date_1, None)
        insert_test_competitive_store(cls.company_competition_2, cls.trade_area_2_3_2, cls.test_store_2_3, cls.test_store_2_1, date_1, None)


        # begin inserting demographics (population = 13, households = 16)
        # population gets the id value of the trade area.  households is the same * 10
        insert_test_demographic(cls.trade_area_1_1_1, 13, 111)
        insert_test_demographic(cls.trade_area_1_1_2, 13, 112)
        insert_test_demographic(cls.trade_area_1_2_1, 13, 121)
        insert_test_demographic(cls.trade_area_1_2_2, 13, 122)
        insert_test_demographic(cls.trade_area_1_3_1, 13, 131)
        insert_test_demographic(cls.trade_area_1_3_2, 13, 132)
        insert_test_demographic(cls.trade_area_1_4_1, 13, 141)
        insert_test_demographic(cls.trade_area_1_4_2, 13, 142)
        insert_test_demographic(cls.trade_area_1_5_1, 13, 151)
        insert_test_demographic(cls.trade_area_1_5_2, 13, 152)
        insert_test_demographic(cls.trade_area_2_1_1, 13, 211)
        insert_test_demographic(cls.trade_area_2_1_2, 13, 212)
        insert_test_demographic(cls.trade_area_2_2_1, 13, 221)
        insert_test_demographic(cls.trade_area_2_2_2, 13, 222)
        insert_test_demographic(cls.trade_area_2_3_1, 13, 231)
        insert_test_demographic(cls.trade_area_2_3_2, 13, 232)
        insert_test_demographic(cls.trade_area_2_4_1, 13, 241)
        insert_test_demographic(cls.trade_area_2_4_2, 13, 242)
        insert_test_demographic(cls.trade_area_1_1_1, 16, 1110)
        insert_test_demographic(cls.trade_area_1_1_2, 16, 1120)
        insert_test_demographic(cls.trade_area_1_2_1, 16, 1210)
        insert_test_demographic(cls.trade_area_1_2_2, 16, 1220)
        insert_test_demographic(cls.trade_area_1_3_1, 16, 1310)
        insert_test_demographic(cls.trade_area_1_3_2, 16, 1320)
        insert_test_demographic(cls.trade_area_1_4_1, 16, 1410)
        insert_test_demographic(cls.trade_area_1_4_2, 16, 1420)
        insert_test_demographic(cls.trade_area_1_5_1, 16, 1510)
        insert_test_demographic(cls.trade_area_1_5_2, 16, 1520)
        insert_test_demographic(cls.trade_area_2_1_1, 16, 2110)
        insert_test_demographic(cls.trade_area_2_1_2, 16, 2120)
        insert_test_demographic(cls.trade_area_2_2_1, 16, 2210)
        insert_test_demographic(cls.trade_area_2_2_2, 16, 2220)
        insert_test_demographic(cls.trade_area_2_3_1, 16, 2310)
        insert_test_demographic(cls.trade_area_2_3_2, 16, 2320)
        insert_test_demographic(cls.trade_area_2_4_1, 16, 2410)
        insert_test_demographic(cls.trade_area_2_4_2, 16, 2420)

    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_competitive_stores([cls.test_store_1_1, cls.test_store_1_2, cls.test_store_1_3, cls.test_store_1_4, cls.test_store_1_5,
                                    cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4])
        delete_test_competitors(cls.company_id_1)
        delete_test_competitors(cls.company_id_2)
        delete_all_demographic_numvalues([cls.trade_area_1_1_1, cls.trade_area_1_1_2, cls.trade_area_1_2_1, cls.trade_area_1_2_2,
                                          cls.trade_area_1_3_1, cls.trade_area_1_3_2, cls.trade_area_1_4_1, cls.trade_area_1_4_2,
                                          cls.trade_area_1_5_1, cls.trade_area_1_5_2, cls.trade_area_2_1_1, cls.trade_area_2_1_2,
                                          cls.trade_area_2_2_1, cls.trade_area_2_2_2, cls.trade_area_2_3_1, cls.trade_area_2_3_2,
                                          cls.trade_area_2_4_1, cls.trade_area_2_4_2])
        delete_all_trade_areas([cls.test_store_1_1, cls.test_store_1_2, cls.test_store_1_3, cls.test_store_1_4, cls.test_store_1_5,
                                cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4])
        delete_all_stores(cls.company_id_1)
        delete_all_stores(cls.company_id_2)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id_1)
        delete_test_company(cls.company_id_2)

        # clear the dependencies
        dependencies.clear()


    def test_demographics_aggregate(self):

        # here is a basic summary of the raw data expected here
        # t0 - all stores:
        #   company 1:
        #       store: 1
        #           competition + 1: 3
        #           ta 1 - pop = 111
        #           ta 1 - households = 1110
        #           ta 2 - pop = 112
        #           ta 2 - households = 1120
        #
        #       store: 2
        #           competition + 1: 2
        #           ta 1 - pop = 121
        #           ta 1 - households = 1210
        #           ta 2 - pop = 122
        #           ta 2 - households = 1220
        #
        #       store: 3
        #           competition + 1: 2
        #           ta 1 - pop = 131
        #           ta 1 - households = 1310
        #           ta 2 - pop = 132
        #           ta 2 - households = 1320
        #
        #   company 2:
        #       store: 1
        #           competition + 1: 3
        #           ta 1 - pop = 211
        #           ta 1 - households = 2110
        #           ta 2 - pop = 212
        #           ta 2 - households = 2120
        #
        #       store: 2
        #           competition + 1: 2
        #           ta 1 - pop = 221
        #           ta 1 - households = 2210
        #           ta 2 - pop = 222
        #           ta 2 - households = 2220
        #
        #       store: 3
        #           competition + 1: 2
        #           ta 1 - pop = 231
        #           ta 1 - households = 2310
        #           ta 2 - pop = 232
        #           ta 2 - households = 2320
        #
        #       store: 4
        #           competition + 1: 1
        #           ta 1 - pop = 241
        #           ta 1 - households = 2410
        #           ta 2 - pop = 242
        #           ta 2 - households = 2420
        #
        # -------------------------------------------
        #
        # t1 - all stores:
        #   company 1:
        #       store: 1
        #           competition + 1: 2
        #           ta 1 - pop = 111
        #           ta 1 - households = 1110
        #           ta 2 - pop = 112
        #           ta 2 - households = 1120
        #
        #       store: 4
        #           competition + 1: 2
        #           ta 1 - pop = 141
        #           ta 1 - households = 1410
        #           ta 2 - pop = 142
        #           ta 2 - households = 1420
        #
        #       store: 5
        #           competition + 1: 1
        #           ta 1 - pop = 151
        #           ta 1 - households = 1510
        #           ta 2 - pop = 152
        #           ta 2 - households = 1520
        #
        #   company 2:
        #       store: 1
        #           competition + 1: 3
        #           ta 1 - pop = 211
        #           ta 1 - households = 2110
        #           ta 2 - pop = 212
        #           ta 2 - households = 2120
        #
        #       store: 2
        #           competition + 1: 2
        #           ta 1 - pop = 221
        #           ta 1 - households = 2210
        #           ta 2 - pop = 222
        #           ta 2 - households = 2220
        #
        #       store: 3
        #           competition + 1: 2
        #           ta 1 - pop = 231
        #           ta 1 - households = 2310
        #           ta 2 - pop = 232
        #           ta 2 - households = 2320
        #
        #       store: 4
        #           competition + 1: 1
        #           ta 1 - pop = 241
        #           ta 1 - households = 2410
        #           ta 2 - pop = 242
        #           ta 2 - households = 2420
        #
        # -------------------------------------------
        #
        # t1 - closings:
        #   company 1:
        #       store: 2
        #           competition + 1: 2
        #           ta 1 - pop = 121
        #           ta 1 - households = 1210
        #           ta 2 - pop = 122
        #           ta 2 - households = 1220
        #
        #       store: 3
        #           competition + 1: 2
        #           ta 1 - pop = 131
        #           ta 1 - households = 1310
        #           ta 2 - pop = 132
        #           ta 2 - households = 1320
        #
        # -------------------------------------------
        #
        # t1 - openings:
        #   company 1:
        #       store: 4
        #           competition + 1: 2
        #           ta 1 - pop = 141
        #           ta 1 - households = 1410
        #           ta 2 - pop = 142
        #           ta 2 - households = 1420
        #
        #       store: 5
        #           competition + 1: 1
        #           ta 1 - pop = 151
        #           ta 1 - households = 1510
        #           ta 2 - pop = 152
        #           ta 2 - households = 1520


        # create the report
        report = CustomAnalyticsDemographicsAggregateReport(self.time_series)

        # truncate the report
        report.lets_make_a_run_for_the_border()

        # run the report
        report.taco_flavored_kisses()

        # query the report
        results = report.omg_they_killed_kenny()

        # group the results nicely, according to the excel logic
        excel_results = report._get_excel_data_sets(results)

        self.assertEqual(excel_results, [
            {
                "headers": ["Banner Name", "Trade Area", "Demographic", "Description", "Minimum", "Maximum", "Average", "Median",
                            "Competition Adjusted Min", "Competition Adjusted Max", "Competition Adjusted Avg", "Competition Adjusted Med"],
                "label": "t0 - all stores",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 111,
                        "Maximum": 131,
                        "Average": 121,
                        "Median": 121,
                        "Competition Adjusted Min": 37,
                        "Competition Adjusted Max": 65.5,
                        "Competition Adjusted Avg": 54.33333,
                        "Competition Adjusted Med": 60.5
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1110,
                        "Maximum": 1310,
                        "Average": 1210,
                        "Median": 1210,
                        "Competition Adjusted Min": 370,
                        "Competition Adjusted Max": 655,
                        "Competition Adjusted Avg": 543.33333,
                        "Competition Adjusted Med": 605
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 112,
                        "Maximum": 132,
                        "Average": 122,
                        "Median": 122,
                        "Competition Adjusted Min": 37.33333,
                        "Competition Adjusted Max": 66,
                        "Competition Adjusted Avg": 54.77778,
                        "Competition Adjusted Med": 61
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1120,
                        "Maximum": 1320,
                        "Average": 1220,
                        "Median": 1220,
                        "Competition Adjusted Min": 373.33333,
                        "Competition Adjusted Max": 660,
                        "Competition Adjusted Avg": 547.77778,
                        "Competition Adjusted Med": 610
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 211,
                        "Maximum": 241,
                        "Average": 226,
                        "Median": 226,
                        "Competition Adjusted Min": 70.33333,
                        "Competition Adjusted Max": 241,
                        "Competition Adjusted Avg": 134.33333,
                        "Competition Adjusted Med": 113
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 2110,
                        "Maximum": 2410,
                        "Average": 2260,
                        "Median": 2260,
                        "Competition Adjusted Min": 703.33333,
                        "Competition Adjusted Max": 2410,
                        "Competition Adjusted Avg": 1343.33333,
                        "Competition Adjusted Med": 1130
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 212,
                        "Maximum": 242,
                        "Average": 227,
                        "Median": 227,
                        "Competition Adjusted Min": 70.66667,
                        "Competition Adjusted Max": 242,
                        "Competition Adjusted Avg": 134.91667,
                        "Competition Adjusted Med": 113.5
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 2120,
                        "Maximum": 2420,
                        "Average": 2270,
                        "Median": 2270,
                        "Competition Adjusted Min": 706.66667,
                        "Competition Adjusted Max": 2420,
                        "Competition Adjusted Avg": 1349.16667,
                        "Competition Adjusted Med": 1135
                    }
                ]
            },
            {
                "headers": ["Banner Name", "Trade Area", "Demographic", "Description", "Minimum", "Maximum", "Average", "Median",
                            "Competition Adjusted Min", "Competition Adjusted Max", "Competition Adjusted Avg", "Competition Adjusted Med"],
                "label": "t1 - all stores",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 111,
                        "Maximum": 151,
                        "Average": 134.33333,
                        "Median": 141,
                        "Competition Adjusted Min": 55.5,
                        "Competition Adjusted Max": 151,
                        "Competition Adjusted Avg": 92.33333,
                        "Competition Adjusted Med": 70.5
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1110,
                        "Maximum": 1510,
                        "Average": 1343.33333,
                        "Median": 1410,
                        "Competition Adjusted Min": 555,
                        "Competition Adjusted Max": 1510,
                        "Competition Adjusted Avg": 923.33333,
                        "Competition Adjusted Med": 705
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 112,
                        "Maximum": 152,
                        "Average": 135.33333,
                        "Median": 142,
                        "Competition Adjusted Min": 56,
                        "Competition Adjusted Max": 152,
                        "Competition Adjusted Avg": 93,
                        "Competition Adjusted Med": 71
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1120,
                        "Maximum": 1520,
                        "Average": 1353.33333,
                        "Median": 1420,
                        "Competition Adjusted Min": 560,
                        "Competition Adjusted Max": 1520,
                        "Competition Adjusted Avg": 930,
                        "Competition Adjusted Med": 710
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 211,
                        "Maximum": 241,
                        "Average": 226,
                        "Median": 226,
                        "Competition Adjusted Min": 70.33333,
                        "Competition Adjusted Max": 241,
                        "Competition Adjusted Avg": 134.33333,
                        "Competition Adjusted Med": 113
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 2110,
                        "Maximum": 2410,
                        "Average": 2260,
                        "Median": 2260,
                        "Competition Adjusted Min": 703.33333,
                        "Competition Adjusted Max": 2410,
                        "Competition Adjusted Avg": 1343.33333,
                        "Competition Adjusted Med": 1130
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 212,
                        "Maximum": 242,
                        "Average": 227,
                        "Median": 227,
                        "Competition Adjusted Min": 70.66667,
                        "Competition Adjusted Max": 242,
                        "Competition Adjusted Avg": 134.91667,
                        "Competition Adjusted Med": 113.5
                    },
                    {
                        "Banner Name": "Company 2",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 2120,
                        "Maximum": 2420,
                        "Average": 2270,
                        "Median": 2270,
                        "Competition Adjusted Min": 706.66667,
                        "Competition Adjusted Max": 2420,
                        "Competition Adjusted Avg": 1349.16667,
                        "Competition Adjusted Med": 1135
                    }
                ]
            },
            {
                "headers": ["Banner Name", "Trade Area", "Demographic", "Description", "Minimum", "Maximum", "Average", "Median",
                            "Competition Adjusted Min", "Competition Adjusted Max", "Competition Adjusted Avg", "Competition Adjusted Med"],
                "label": "t1 - closings",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 121,
                        "Maximum": 131,
                        "Average": 126,
                        "Median": 126,
                        "Competition Adjusted Min": 60.5,
                        "Competition Adjusted Max": 65.5,
                        "Competition Adjusted Avg": 63,
                        "Competition Adjusted Med": 63
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1210,
                        "Maximum": 1310,
                        "Average": 1260,
                        "Median": 1260,
                        "Competition Adjusted Min": 605,
                        "Competition Adjusted Max": 655,
                        "Competition Adjusted Avg": 630,
                        "Competition Adjusted Med": 630
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 122,
                        "Maximum": 132,
                        "Average": 127,
                        "Median": 127,
                        "Competition Adjusted Min": 61,
                        "Competition Adjusted Max": 66,
                        "Competition Adjusted Avg": 63.5,
                        "Competition Adjusted Med": 63.5
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1220,
                        "Maximum": 1320,
                        "Average": 1270,
                        "Median": 1270,
                        "Competition Adjusted Min": 610,
                        "Competition Adjusted Max": 660,
                        "Competition Adjusted Avg": 635,
                        "Competition Adjusted Med": 635
                    }
                ]
            },
            {
                "headers": ["Banner Name", "Trade Area", "Demographic", "Description", "Minimum", "Maximum", "Average", "Median",
                            "Competition Adjusted Min", "Competition Adjusted Max", "Competition Adjusted Avg", "Competition Adjusted Med"],
                "label": "t1 - openings",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 141,
                        "Maximum": 151,
                        "Average": 146,
                        "Median": 146,
                        "Competition Adjusted Min": 70.5,
                        "Competition Adjusted Max": 151,
                        "Competition Adjusted Avg": 110.75,
                        "Competition Adjusted Med": 110.75
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "5 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1410,
                        "Maximum": 1510,
                        "Average": 1460,
                        "Median": 1460,
                        "Competition Adjusted Min": 705,
                        "Competition Adjusted Max": 1510,
                        "Competition Adjusted Avg": 1107.5,
                        "Competition Adjusted Med": 1107.5
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTPOP_CY",
                        "Description": "2011 Total Population",
                        "Minimum": 142,
                        "Maximum": 152,
                        "Average": 147,
                        "Median": 147,
                        "Competition Adjusted Min": 71,
                        "Competition Adjusted Max": 152,
                        "Competition Adjusted Avg": 111.5,
                        "Competition Adjusted Med": 111.5
                    },
                    {
                        "Banner Name": "Company 1",
                        "Trade Area": "10 Miles",
                        "Demographic": "TOTHH_CY",
                        "Description": "2011 Total Households",
                        "Minimum": 1420,
                        "Maximum": 1520,
                        "Average": 1470,
                        "Median": 1470,
                        "Competition Adjusted Min": 710,
                        "Competition Adjusted Max": 1520,
                        "Competition Adjusted Avg": 1115,
                        "Competition Adjusted Med": 1115
                    }
                ]
            }
        ])