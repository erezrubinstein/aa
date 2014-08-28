import pprint
import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.reports.custom_analytics_comp_stores_report import CustomAnalyticsCompStoresReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *


__author__ = 'erezrubinstein'

class CompStoreReportTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # define period dates
        cls.date_1 = datetime.datetime(2012, 1, 1)
        cls.date_2 = datetime.datetime(2012, 9, 1)
        cls.date_3 = datetime.datetime(2013, 1, 1)

        # define time dates that are before or after the period
        cls.date_before = datetime.datetime(1900, 1, 1)
        cls.date_after = datetime.datetime(2014, 1, 1)


        # define the time series for this report
        cls.time_series = [
            {
                "label": "t0",
                "date": cls.date_1
            },
            {
                "label": "t1",
                "date": cls.date_2
            },
            {
                "label": "t2",
                "date": cls.date_3
            }
        ]

        # create the comp store settings
        cls.comp_store_settings = [
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            }
        ]

    @classmethod
    def tearDownClass(cls):

        # delete the data (backwards order of inserting)
        #delete_all_competitive_stores([cls.test_store_1_1, cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4, cls.test_store_3_1, cls.test_store_3_2, cls.test_store_4_1])
        #delete_all_trade_areas([cls.test_store_1_1, cls.test_store_2_1, cls.test_store_2_2, cls.test_store_2_3, cls.test_store_2_4, cls.test_store_3_1, cls.test_store_3_2, cls.test_store_4_1])
        #delete_all_stores(cls.company_id_1)
        #delete_all_stores(cls.company_id_2)
        #delete_all_stores(cls.company_id_3)
        #delete_all_stores(cls.company_id_4)
        #delete_test_address(cls.address_id)
        #delete_test_competitors(cls.company_id_1)
        #delete_test_competitors(cls.company_id_2)
        #delete_test_competitors(cls.company_id_3)
        #delete_test_competitors(cls.company_id_4)
        #delete_test_company(cls.company_id_1)
        #delete_test_company(cls.company_id_2)
        #delete_test_company(cls.company_id_3)
        #delete_test_company(cls.company_id_4)

        # clear the dependencies
        dependencies.clear()


    def test_comp_store_settings(self):

        # run the reports without any data
        report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
        report.lets_make_a_run_for_the_border()
        report.taco_flavored_kisses()
        results = report.omg_they_killed_kenny()
        excel_results = report._get_excel_data_sets(results)

        # get the settings and verify them
        comp_store_settings = excel_results[0]
        self.assertEqual(comp_store_settings, {
            "headers": ["Period", "Current Period (CP)", "Prior Period (PP)", "Prior Year (PY)"],
            "label": "Comparable Stores Settings",
            "description": "Comparable Stores Report Settings",
            "rows": [
                {
                    "Period": "Period 0",
                    "Current Period (CP)": "t2",
                    "Prior Period (PP)": "t1",
                    "Prior Year (PY)": "t0"
                }
            ]
        })


    def test_store_counts(self):

        try:
            # insert two companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")

            # create one address
            address_id = insert_test_address(1, 1)

            # insert different stores with different dates for company 1
            insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1, assumed_closed_date = self.date_2)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1, assumed_closed_date = self.date_3)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_2)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_3)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_3)

            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use the store count results
            store_counts_results = excel_results[1]

            # verify the results
            self.assertEqual(store_counts_results, {
                "headers": ["Company Name", "Period 0"],
                "label": "Comparable Store Counts",
                "rows": [
                    { "Company Name": "Company 1", "Period 0": 2 },
                    { "Company Name": "Company 2", "Period 0": 0 }
                ]
            })

        finally:

            # delete (in backwards order)
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_test_address(address_id)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)


    def test_competitor_competition_ratio_report(self):

        try:
            # create three companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")
            company_id_3 = insert_test_company(name = "Company 3")
            
            # have all companies compete with all
            company_competition_11 = insert_test_competitor(company_id_1, company_id_1)
            company_competition_12 = insert_test_competitor(company_id_1, company_id_2)
            company_competition_13 = insert_test_competitor(company_id_1, company_id_3)
            company_competition_21 = insert_test_competitor(company_id_2, company_id_1)
            company_competition_22 = insert_test_competitor(company_id_2, company_id_2)
            company_competition_23 = insert_test_competitor(company_id_2, company_id_3)
            company_competition_31 = insert_test_competitor(company_id_3, company_id_1)
            company_competition_32 = insert_test_competitor(company_id_3, company_id_2)
            company_competition_33 = insert_test_competitor(company_id_3, company_id_3)

            # create one address
            address_id = insert_test_address(1, 1)

            # insert a store for each number in the company.  all stores are comp stores
            store_id_1_1 = insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            store_id_2_1 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_2_2 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_3_1 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_2 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_3 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)

            # create a trade area (just one) for each store
            trade_area_1_1 = insert_test_trade_area_raw(store_id_1_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_1 = insert_test_trade_area_raw(store_id_2_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_2 = insert_test_trade_area_raw(store_id_2_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_1 = insert_test_trade_area_raw(store_id_3_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_2 = insert_test_trade_area_raw(store_id_3_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_3 = insert_test_trade_area_raw(store_id_3_3, TradeAreaThreshold.DistanceMiles10)

            # for company 1, store 1, create 5 competitions.  one before, one py, one pp, onc cp, and one after
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_1, self.date_before, self.date_3) # ends after PP period
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_2, self.date_1, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_2, self.date_3, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_3, self.date_after, None)

            # for company 2, insert one competition in date 2
            insert_test_competitive_store(company_competition_21, trade_area_2_1, store_id_2_1, store_id_1_1, self.date_2, None)

            # for company 2, insert another competition, but same company competition, which should count
            insert_test_competitive_store(company_competition_22, trade_area_2_1, store_id_2_1, store_id_2_2, self.date_before, None)

            # no competition for company 3

            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use this report
            results = excel_results[2]

            # verify results
            self.assertEqual(results, {
                "label": "Competitor Competition Ratio",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Period 0 - 10 Miles Trade Area",
                        "unique_headers_mapping": ["Company Name", "store_count", "cp_comp_instances", "cp_comp_ratio", "cp_store_base_affected", "pp_comp_instances", "pp_comp_ratio", "pp_store_base_affected", "py_comp_instances", "py_comp_ratio", "py_store_base_affected", "ccr_growth_rate"],
                        "headers": [
                            ["", "N/A", "Current Period", "Current Period", "Current Period", "Prior Period", "Prior Period", "Prior Period", "Prior Year", "Prior Year", "Prior Year", "N/A"],
                            ["Company Name", "Comp Store Count", "Comp Instances", "Comp Ratio", "% Store Base Affected", "Comp Instances", "Comp Ratio", "% Store Base Affected", "Comp Instances", "Comp Ratio", "% Store Base Affected", "CCR Growth Rate"]
                        ],
                        "headers_comments_per_index": [
                            {},
                            {
                                1: "Number of comparable stores for this period",
                                2: "Number of competitive instances (excluding same company stores) for the current period",
                                3: "Ratio of current period Comp Instances divided by the Comp Store Count",
                                4: "Percentage of the comparable stores for this period that have at least one current period competitive instance",
                                5: "Number of competitive instances (excluding same company stores) for the prior period",
                                6: "Ratio of prior period Comp Instances divided by the Comp Store Count",
                                7: "Percentage of the comparable stores for this period that have at least one prior period competitive instance",
                                8: "Number of competitive instances (excluding same company stores) for the prior year",
                                9: "Ratio of prior year Comp Instances divided by the Comp Store Count",
                                10: "Percentage of the comparable stores for this period that have at least one prior year competitive instance",
                                11: "Percent growth of the current period competitive instances compared to the prior period's competitive instances"
                            }
                        ],
                        "rows": [
                            {
                                "Company Name": "Company 1",
                                "store_count": 1,
                                "cp_comp_instances": 3,
                                "cp_comp_ratio": 3,
                                "cp_store_base_affected": 100,
                                "pp_comp_instances": 3,
                                "pp_comp_ratio": 3,
                                "pp_store_base_affected": 100,
                                "py_comp_instances": 2,
                                "py_comp_ratio": 2,
                                "py_store_base_affected": 100,
                                "ccr_growth_rate": 50
                            },
                            {
                                "Company Name": "Company 2",
                                "store_count": 2,
                                "cp_comp_instances": 1,
                                "cp_comp_ratio": .5,
                                "cp_store_base_affected": 50,
                                "pp_comp_instances": 1,
                                "pp_comp_ratio": .5,
                                "pp_store_base_affected": 50,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            },
                            {
                                "Company Name": "Company 3",
                                "store_count": 3,
                                "cp_comp_instances": 0,
                                "cp_comp_ratio": 0,
                                "cp_store_base_affected": 0,
                                "pp_comp_instances": 0,
                                "pp_comp_ratio": 0,
                                "pp_store_base_affected": 0,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            }
                        ]
                    }
                ]
            })


        finally:

            # delete (in backwards order)
            delete_all_competitive_stores([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_trade_areas([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_all_stores(company_id_3)
            delete_test_address(address_id)
            delete_test_competitors(company_id_1)
            delete_test_competitors(company_id_2)
            delete_test_competitors(company_id_3)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)
            delete_test_company(company_id_3)


    def test_percent_with_cci_net_openings_report(self):

        try:

            # create three companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")
            company_id_3 = insert_test_company(name = "Company 3")

            # have all companies compete with all
            company_competition_11 = insert_test_competitor(company_id_1, company_id_1)
            company_competition_12 = insert_test_competitor(company_id_1, company_id_2)
            company_competition_13 = insert_test_competitor(company_id_1, company_id_3)
            company_competition_21 = insert_test_competitor(company_id_2, company_id_1)
            company_competition_22 = insert_test_competitor(company_id_2, company_id_2)
            company_competition_23 = insert_test_competitor(company_id_2, company_id_3)
            company_competition_31 = insert_test_competitor(company_id_3, company_id_1)
            company_competition_32 = insert_test_competitor(company_id_3, company_id_2)
            company_competition_33 = insert_test_competitor(company_id_3, company_id_3)

            # create one address
            address_id = insert_test_address(1, 1)

            # insert a store for each number in the company.  all stores are comp stores
            store_id_1_1 = insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            store_id_2_1 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_2_2 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_3_1 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_2 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_3 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)

            # create a trade area (just one) for each store
            trade_area_1_1 = insert_test_trade_area_raw(store_id_1_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_1 = insert_test_trade_area_raw(store_id_2_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_2 = insert_test_trade_area_raw(store_id_2_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_1 = insert_test_trade_area_raw(store_id_3_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_2 = insert_test_trade_area_raw(store_id_3_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_3 = insert_test_trade_area_raw(store_id_3_3, TradeAreaThreshold.DistanceMiles10)

            # for company 1, create a few openings in each range and a few after the fact, to make sure they don't count
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_2, self.date_1, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_2, self.date_3, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_3, self.date_after, None)

            # for company 2, insert one competition in PP-PY only.
            insert_test_competitive_store(company_competition_21, trade_area_2_1, store_id_2_1, store_id_1_1, self.date_1, None)

            # for company 2, insert another competition, in the first period, but make it a "own" competition, which shouldn't count
            insert_test_competitive_store(company_competition_22, trade_area_2_1, store_id_2_1, store_id_2_2, self.date_1, None)

            # for company 3, create an opening in PY, which closes in PP, and another opening in PP.
            # this should even out to a net opening in CP-PY and 0 net openings in CP-PP
            insert_test_competitive_store(company_competition_32, trade_area_3_1, store_id_3_1, store_id_2_1, self.date_1, self.date_2)
            insert_test_competitive_store(company_competition_32, trade_area_3_1, store_id_3_1, store_id_2_2, self.date_2, None)


            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use this report
            results = excel_results[3]

            # verify results
            self.assertEqual(results, {
                "label": "Pct With Net Comp Openings",
                "description": "Percent of Stores with Net Competition Openings",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Period 0 - 10 Miles Trade Area",
                        "unique_headers_mapping": ["Company Name", "store_count", "cp_to_pp_store_count", "cp_to_pp_ratio", "cp_to_py_store_count", "cp_to_py_ratio"],
                        "headers": [
                            ["", "N/A", "Current Period to Prior Period", "Current Period to Prior Period", "Current Period to Prior Year", "Current Period to Prior Year"],
                            ["Company Name", "Store Counts", "Stores w/ Net Competitive Openings", "% w/ Net Competitive Openings", "Stores w/ Net Competitive Openings", "% w/ Net Competitive Openings"]
                        ],
                        "headers_comments_per_index": [
                            {},
                            {
                                1: "Number of comparable stores for this period",
                                2: "Number of stores with at least one competitive opening (excluding same company stores) between the prior period and the current period",
                                3: "Percent of stores with at least one competitive opening (excluding same company stores) between the prior period and the current period",
                                4: "Number of stores with at least one competitive opening (excluding same company stores) between the prior year and the current period",
                                5: "Percent of stores with at least one competitive opening (excluding same company stores) between the prior year and the current period",
                            }
                        ],
                        "rows": [
                            {
                                "Company Name": "Company 1",
                                "store_count": 1,
                                "cp_to_pp_store_count": 1,
                                "cp_to_pp_ratio": 100,
                                "cp_to_py_store_count": 1,
                                "cp_to_py_ratio": 100
                            },
                            {
                                "Company Name": "Company 2",
                                "store_count": 2,
                                "cp_to_pp_store_count": 0,
                                "cp_to_pp_ratio": 0,
                                "cp_to_py_store_count": 1,
                                "cp_to_py_ratio": 50
                            },
                            {
                                "Company Name": "Company 3",
                                "store_count": 3,
                                "cp_to_pp_store_count": 0,
                                "cp_to_pp_ratio": 0,
                                "cp_to_py_store_count": 1,
                                "cp_to_py_ratio": 33.33333
                            }
                        ]
                    }
                ]
            })

        finally:


            # delete (in backwards order)
            delete_all_competitive_stores([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_trade_areas([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_all_stores(company_id_3)
            delete_test_address(address_id)
            delete_test_competitors(company_id_1)
            delete_test_competitors(company_id_2)
            delete_test_competitors(company_id_3)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)
            delete_test_company(company_id_3)


    def test_all_raw_comp_stores_report(self):

        try:
            # insert two companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")

            # create one address
            address_id = insert_test_address(1, 1, 4, "street", "city", "NY", 77777)

            # insert different stores with different dates for company 1
            insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1, assumed_closed_date = self.date_2)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_1, assumed_closed_date = self.date_3)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_2)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_3)
            insert_test_store(company_id_1, address_id, assumed_opened_date = self.date_3)

            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use this report
            results = excel_results[4]

            # verify the results
            self.assertEqual(results, {
                "label": "All Comparable Stores",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Period 0",
                        "headers": ["Company Name", "Address", "City", "State", "Zip"],
                        "rows": [
                            {
                                "Company Name": "Company 1",
                                "Address": "4 street",
                                "City": "city",
                                "State": "NY",
                                "Zip": "77777"
                            },
                            {
                                "Company Name": "Company 1",
                                "Address": "4 street",
                                "City": "city",
                                "State": "NY",
                                "Zip": "77777"
                            }
                        ]
                    }
                ]
            })

        finally:

            # delete (in backwards order)
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_test_address(address_id)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)


    def test_raw_stores_with_net_openings_report(self):

        try:

            # create three companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")
            company_id_3 = insert_test_company(name = "Company 3")

            # have all companies compete with all
            company_competition_11 = insert_test_competitor(company_id_1, company_id_1)
            company_competition_12 = insert_test_competitor(company_id_1, company_id_2)
            company_competition_13 = insert_test_competitor(company_id_1, company_id_3)
            company_competition_21 = insert_test_competitor(company_id_2, company_id_1)
            company_competition_22 = insert_test_competitor(company_id_2, company_id_2)
            company_competition_23 = insert_test_competitor(company_id_2, company_id_3)
            company_competition_31 = insert_test_competitor(company_id_3, company_id_1)
            company_competition_32 = insert_test_competitor(company_id_3, company_id_2)
            company_competition_33 = insert_test_competitor(company_id_3, company_id_3)

            # create one address
            address_id = insert_test_address(1, 1, 4, "street", "city", "NY", 77777)

            # insert a store for each number in the company.  all stores are comp stores
            store_id_1_1 = insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            store_id_2_1 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_2_2 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_3_1 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_2 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_3 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)

            # create a trade area (just one) for each store
            trade_area_1_1 = insert_test_trade_area_raw(store_id_1_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_1 = insert_test_trade_area_raw(store_id_2_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_2 = insert_test_trade_area_raw(store_id_2_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_1 = insert_test_trade_area_raw(store_id_3_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_2 = insert_test_trade_area_raw(store_id_3_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_3 = insert_test_trade_area_raw(store_id_3_3, TradeAreaThreshold.DistanceMiles10)

            # for company 1, create a few openings in each range and a few after the fact, to make sure they don't count
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_2, self.date_1, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_2, self.date_3, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_3, self.date_after, None)

            # for company 2, insert one competition in PP-PY only.
            insert_test_competitive_store(company_competition_21, trade_area_2_1, store_id_2_1, store_id_1_1, self.date_1, None)

            # for company 2, insert another competition, in the first period, but make it a "own" competition, which shouldn't count
            insert_test_competitive_store(company_competition_22, trade_area_2_1, store_id_2_1, store_id_2_2, self.date_1, None)

            # for company 3, create an opening in PY, which closes in PP, and another opening in PP.
            # this should even out to a net opening in CP-PY and 0 net openings in CP-PP
            insert_test_competitive_store(company_competition_32, trade_area_3_1, store_id_3_1, store_id_2_1, self.date_1, self.date_2)
            insert_test_competitive_store(company_competition_32, trade_area_3_1, store_id_3_1, store_id_2_2, self.date_2, None)


            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use this report
            results = excel_results[5]

            # verify results
            self.assertEqual(results, {
                "label": "Stores Net Comp Openings",
                "description": "All Stores with Net Competition Openings",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Period 0 - 10 Miles Trade Area",
                        "headers": ["Company Name", "Address", "City", "State", "Zip", "Net Competition Openings Current Period to Prior Period", "Net Competition Openings Current Period to Prior Year"],
                        "headers_comments": {
                            "Net Competition Openings Current Period to Prior Period": "Net competition openings (openings - closings) for this store in between the prior period and the current period",
                            "Net Competition Openings Current Period to Prior Year": "Net competition openings (openings - closings) for this store in between the prior year and the current period"
                        },
                        "rows": [
                            {
                                "Company Name": "Company 1",
                                "Address": "4 street",
                                "City": "city",
                                "State": "NY",
                                "Zip": "77777",
                                "Net Competition Openings Current Period to Prior Period": 2,
                                "Net Competition Openings Current Period to Prior Year": 3
                            },
                            {
                                "Company Name": "Company 2",
                                "Address": "4 street",
                                "City": "city",
                                "State": "NY",
                                "Zip": "77777",
                                "Net Competition Openings Current Period to Prior Period": 0,
                                "Net Competition Openings Current Period to Prior Year": 1
                            },
                            {
                                "Company Name": "Company 3",
                                "Address": "4 street",
                                "City": "city",
                                "State": "NY",
                                "Zip": "77777",
                                "Net Competition Openings Current Period to Prior Period": 0,
                                "Net Competition Openings Current Period to Prior Year": 1
                            }
                        ]
                    }
                ]
            })

        finally:


            # delete (in backwards order)
            delete_all_competitive_stores([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_trade_areas([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_all_stores(company_id_3)
            delete_test_address(address_id)
            delete_test_competitors(company_id_1)
            delete_test_competitors(company_id_2)
            delete_test_competitors(company_id_3)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)
            delete_test_company(company_id_3)


    def test_ccr_attribution_report(self):

        try:
            # create three companies
            company_id_1 = insert_test_company(name = "Company 1")
            company_id_2 = insert_test_company(name = "Company 2")
            company_id_3 = insert_test_company(name = "Company 3")

            # have all companies compete with all
            company_competition_11 = insert_test_competitor(company_id_1, company_id_1)
            company_competition_12 = insert_test_competitor(company_id_1, company_id_2)
            company_competition_13 = insert_test_competitor(company_id_1, company_id_3)
            company_competition_21 = insert_test_competitor(company_id_2, company_id_1)
            company_competition_22 = insert_test_competitor(company_id_2, company_id_2)
            company_competition_23 = insert_test_competitor(company_id_2, company_id_3)
            company_competition_31 = insert_test_competitor(company_id_3, company_id_1)
            company_competition_32 = insert_test_competitor(company_id_3, company_id_2)
            company_competition_33 = insert_test_competitor(company_id_3, company_id_3)

            # create one address
            address_id = insert_test_address(1, 1)

            # insert a store for each number in the company.  all stores are comp stores
            store_id_1_1 = insert_test_store(company_id_1, address_id, assumed_opened_date = None)
            store_id_2_1 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_2_2 = insert_test_store(company_id_2, address_id, assumed_opened_date = None)
            store_id_3_1 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_2 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)
            store_id_3_3 = insert_test_store(company_id_3, address_id, assumed_opened_date = None)

            # create a trade area (just one) for each store
            trade_area_1_1 = insert_test_trade_area_raw(store_id_1_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_1 = insert_test_trade_area_raw(store_id_2_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_2_2 = insert_test_trade_area_raw(store_id_2_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_1 = insert_test_trade_area_raw(store_id_3_1, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_2 = insert_test_trade_area_raw(store_id_3_2, TradeAreaThreshold.DistanceMiles10)
            trade_area_3_3 = insert_test_trade_area_raw(store_id_3_3, TradeAreaThreshold.DistanceMiles10)

            # for company 1, store 1, create 5 competitions.  one before, one py, one pp, onc cp, and one after
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_1, self.date_before, self.date_3) # ends after PP period
            insert_test_competitive_store(company_competition_12, trade_area_1_1, store_id_1_1, store_id_2_2, self.date_1, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_1, self.date_2, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_2, self.date_3, None)
            insert_test_competitive_store(company_competition_13, trade_area_1_1, store_id_1_1, store_id_3_3, self.date_after, None)

            # for company 2, insert one competition in date 2
            insert_test_competitive_store(company_competition_21, trade_area_2_1, store_id_2_1, store_id_1_1, self.date_2, None)

            # for company 2, insert another competition, but same company competition, which should count
            insert_test_competitive_store(company_competition_22, trade_area_2_1, store_id_2_1, store_id_2_2, self.date_before, None)

            # no competition for company 3

            # run da trap
            report = CustomAnalyticsCompStoresReport(self.time_series, self.comp_store_settings)
            report.lets_make_a_run_for_the_border()
            report.taco_flavored_kisses()
            results = report.omg_they_killed_kenny()
            excel_results = report._get_excel_data_sets(results)

            # only use this report
            results = excel_results[6]

            # verify results
            self.assertEqual(results, {
                "label": "Competition Ratio Attribution",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Period 0 - 10 Miles Trade Area",
                        "unique_headers_mapping": ["Home Company", "Away Company", "store_count", "cp_comp_instances", "cp_comp_ratio", "cp_store_base_affected", "pp_comp_instances", "pp_comp_ratio", "pp_store_base_affected", "py_comp_instances", "py_comp_ratio", "py_store_base_affected", "ccr_growth_rate"],
                        "headers_comments_per_index": [
                            {},
                            {
                                2: "Number of comparable stores for this period (for the home company)",
                                3: "Number of competitive instances (excluding same company stores) for the current period",
                                4: "Ratio of current period Comp Instances divided by the Comp Store Count",
                                5: "Percentage of the comparable stores for this period that have at least one current period competitive instance",
                                6: "Number of competitive instances (excluding same company stores) for the prior period",
                                7: "Ratio of prior period Comp Instances divided by the Comp Store Count",
                                8: "Percentage of the comparable stores for this period that have at least one prior period competitive instance",
                                9: "Number of competitive instances (excluding same company stores) for the prior year",
                                10: "Ratio of prior year Comp Instances divided by the Comp Store Count",
                                11: "Percentage of the comparable stores for this period that have at least one prior year competitive instance",
                                12: "Percent growth of the current period competitive instances compared to the prior period's competitive instances"
                            }
                        ],
                        "headers": [
                            ["", "", "N/A", "Current Period", "Current Period", "Current Period", "Prior Period", "Prior Period", "Prior Period", "Prior Year", "Prior Year", "Prior Year", "N/A"],
                            ["Home Company", "Away Company", "Home Store Count", "Comp Instances", "Comp Ratio", "% Store Base Affected", "Comp Instances", "Comp Ratio", "% Store Base Affected", "Comp Instances", "Comp Ratio", "% Store Base Affected", "CCR Growth Rate"]
                        ],
                        "rows": [
                            {
                                "Home Company": "Company 1",
                                "Away Company": "Company 2",
                                "store_count": 1,
                                "cp_comp_instances": 1,
                                "cp_comp_ratio": 1,
                                "cp_store_base_affected": 100,
                                "pp_comp_instances": 2,
                                "pp_comp_ratio": 2,
                                "pp_store_base_affected": 100,
                                "py_comp_instances": 2,
                                "py_comp_ratio": 2,
                                "py_store_base_affected": 100,
                                "ccr_growth_rate": -50
                            },
                            {
                                "Home Company": "Company 1",
                                "Away Company": "Company 3",
                                "store_count": 1,
                                "cp_comp_instances": 2,
                                "cp_comp_ratio": 2,
                                "cp_store_base_affected": 100,
                                "pp_comp_instances": 1,
                                "pp_comp_ratio": 1,
                                "pp_store_base_affected": 100,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            },
                            {
                                "Home Company": "Company 2",
                                "Away Company": "Company 1",
                                "store_count": 2,
                                "cp_comp_instances": 1,
                                "cp_comp_ratio": .5,
                                "cp_store_base_affected": 50,
                                "pp_comp_instances": 1,
                                "pp_comp_ratio": .5,
                                "pp_store_base_affected": 50,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            },
                            {
                                "Home Company": "Company 2",
                                "Away Company": "Company 3",
                                "store_count": 2,
                                "cp_comp_instances": 0,
                                "cp_comp_ratio": 0,
                                "cp_store_base_affected": 0,
                                "pp_comp_instances": 0,
                                "pp_comp_ratio": 0,
                                "pp_store_base_affected": 0,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            },
                            {
                                "Home Company": "Company 3",
                                "Away Company": "Company 1",
                                "store_count": 3,
                                "cp_comp_instances": 0,
                                "cp_comp_ratio": 0,
                                "cp_store_base_affected": 0,
                                "pp_comp_instances": 0,
                                "pp_comp_ratio": 0,
                                "pp_store_base_affected": 0,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            },
                            {
                                "Home Company": "Company 3",
                                "Away Company": "Company 2",
                                "store_count": 3,
                                "cp_comp_instances": 0,
                                "cp_comp_ratio": 0,
                                "cp_store_base_affected": 0,
                                "pp_comp_instances": 0,
                                "pp_comp_ratio": 0,
                                "pp_store_base_affected": 0,
                                "py_comp_instances": 0,
                                "py_comp_ratio": 0,
                                "py_store_base_affected": 0,
                                "ccr_growth_rate": 0
                            }
                        ]
                    }
                ]
            })


        finally:

            # delete (in backwards order)
            delete_all_competitive_stores([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_trade_areas([store_id_1_1, store_id_2_1, store_id_2_2, store_id_3_1, store_id_3_2, store_id_3_3])
            delete_all_stores(company_id_1)
            delete_all_stores(company_id_2)
            delete_all_stores(company_id_3)
            delete_test_address(address_id)
            delete_test_competitors(company_id_1)
            delete_test_competitors(company_id_2)
            delete_test_competitors(company_id_3)
            delete_test_company(company_id_1)
            delete_test_company(company_id_2)
            delete_test_company(company_id_3)