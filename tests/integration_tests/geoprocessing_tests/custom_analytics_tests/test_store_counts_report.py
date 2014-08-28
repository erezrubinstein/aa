import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from geoprocessing.custom_analytics.reports.custom_analytics_store_counts_report import CustomAnalyticsStoreCountReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class StoreCountReportTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # define three dates
        date_1 = datetime.datetime(1900, 1, 1)
        date_2 = datetime.datetime(2012, 1, 1)
        date_3 = datetime.datetime(2013, 1, 1)

        # define the time series for this report
        cls.time_series = [
            {
                "label": "t0",
                "date": date_1
            },
            {
                "label": "t1",
                "date": date_2
            },
            {
                "label": "t2",
                "date": date_3
            }
        ]

        # insert 3 companies
        cls.company_id_1 = insert_test_company(name = "Company 1")
        cls.company_id_2 = insert_test_company(name = "Company 2")
        cls.company_id_3 = insert_test_company(name = "Company 3")

        # company four will test a very specific bug we saw in production with a company that opens in the middle and closes that same period
        cls.company_id_4 = insert_test_company(name = "Company 4")

        # create one address to be used by all stores (we don't care what it is)
        cls.address_id = insert_test_address(-1, 1)

        # create three stores for company 1, each opening in each period.
        insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_2)
        insert_test_store(cls.company_id_1, cls.address_id, assumed_opened_date = date_3)

        # create 4 stores for company 2 and close a few for each date
        insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_3)
        insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_3)
        insert_test_store(cls.company_id_2, cls.address_id, assumed_opened_date = date_1)

        # create 6 stores for company 3 and close and open some for each date
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_2)
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_1, assumed_closed_date = date_3)
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_2, assumed_closed_date = date_3)
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_2)
        insert_test_store(cls.company_id_3, cls.address_id, assumed_opened_date = date_3)

        # company 4 has 1 store that opens in t1 and closes in t2
        insert_test_store(cls.company_id_4, cls.address_id, assumed_opened_date = date_2, assumed_closed_date = date_3)


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_stores(cls.company_id_1)
        delete_all_stores(cls.company_id_2)
        delete_all_stores(cls.company_id_3)
        delete_all_stores(cls.company_id_4)
        delete_test_address(cls.address_id)
        delete_test_company(cls.company_id_1)
        delete_test_company(cls.company_id_2)
        delete_test_company(cls.company_id_3)
        delete_test_company(cls.company_id_4)

        # clear the dependencies
        dependencies.clear()


    def test_store_count(self):

        # create the report
        report = CustomAnalyticsStoreCountReport(self.time_series)

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
                "headers": ["Banner Name", "t0", "t1 - Openings", "t1 - Closings", "t1", "t2 - Openings", "t2 - Closings", "t2", "t1 - Growth Rate", "t2 - Growth Rate"],
                "label": "Summary",
                "description": "Store Count Summary",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "t0": 1,
                        "t1 - Openings": 1,
                        "t1 - Closings": 0,
                        "t1": 2,
                        "t2 - Openings": 1,
                        "t2 - Closings": 0,
                        "t2": 3,
                        "t1 - Growth Rate": 100,
                        "t2 - Growth Rate": 50
                    },
                    {
                        "Banner Name": "Company 2",
                        "t0": 4,
                        "t1 - Openings": 0,
                        "t1 - Closings": 1,
                        "t1": 3,
                        "t2 - Openings": 0,
                        "t2 - Closings": 2,
                        "t2": 1,
                        "t1 - Growth Rate": -25,
                        "t2 - Growth Rate": -66.66667
                    },
                    {
                        "Banner Name": "Company 3",
                        "t0": 3,
                        "t1 - Openings": 2,
                        "t1 - Closings": 1,
                        "t1": 4,
                        "t2 - Openings": 1,
                        "t2 - Closings": 2,
                        "t2": 3,
                        "t1 - Growth Rate": 33.33333,
                        "t2 - Growth Rate": -25
                    },
                    {
                        "Banner Name": "Company 4",
                        "t0": 0,
                        "t1 - Openings": 1,
                        "t1 - Closings": 0,
                        "t1": 1,
                        "t2 - Openings": 0,
                        "t2 - Closings": 1,
                        "t2": 0,
                        "t1 - Growth Rate": 0,
                        "t2 - Growth Rate": -100
                    },
                    {
                        "Banner Name": "Total",
                        "t0": 8,
                        "t1 - Openings": 4,
                        "t1 - Closings": 2,
                        "t1": 10,
                        "t2 - Openings": 2,
                        "t2 - Closings": 5,
                        "t2": 7,
                        "t1 - Growth Rate": 25,
                        "t2 - Growth Rate": -30,
                        "meta": {
                            "bold": True
                        }
                    }
                ]
            },
            {
                "headers" : ["Banner Name", "t0", "t1", "t2"],
                "label": "all stores",
                "rows": [

                    # t0
                    {
                        "Banner Name": "Company 1",
                        "t0": 1,
                        "t1": 2,
                        "t2": 3
                    },
                    {
                        "Banner Name": "Company 2",
                        "t0": 4,
                        "t1": 3,
                        "t2": 1
                    },
                    {
                        "Banner Name": "Company 3",
                        "t0": 3,
                        "t1": 4,
                        "t2": 3
                    },
                    {
                        "Banner Name": "Company 4",
                        "t0": 0,
                        "t1": 1,
                        "t2": 0
                    },
                    {
                        "Banner Name": "Total",
                        "t0": 8,
                        "t1": 10,
                        "t2": 7,
                        "meta": {
                            "bold": True
                        }
                    }
                ]
            },
            {
                "headers" : ["Banner Name", "t0", "t1", "t2"],
                "label": "openings",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "t0": 0,
                        "t1": 1,
                        "t2": 1
                    },
                    {
                        "Banner Name": "Company 2",
                        "t0": 0,
                        "t1": 0,
                        "t2": 0
                    },
                    {
                        "Banner Name": "Company 3",
                        "t0": 0,
                        "t1": 2,
                        "t2": 1
                    },
                    {
                        "Banner Name": "Company 4",
                        "t0": 0,
                        "t1": 1,
                        "t2": 0
                    },
                    {
                        "Banner Name": "Total",
                        "t0": 0,
                        "t1": 4,
                        "t2": 2,
                        "meta": {
                            "bold": True
                        }
                    }
                ]
            },
            {
                "headers" : ["Banner Name", "t0", "t1", "t2"],
                "label": "closings",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "t0": 0,
                        "t1": 0,
                        "t2": 0
                    },
                    {
                        "Banner Name": "Company 2",
                        "t0": 0,
                        "t1": 1,
                        "t2": 2
                    },
                    {
                        "Banner Name": "Company 3",
                        "t0": 0,
                        "t1": 1,
                        "t2": 2
                    },
                    {
                        "Banner Name": "Company 4",
                        "t0": 0,
                        "t1": 0,
                        "t2": 1
                    },
                    {
                        "Banner Name": "Total",
                        "t0": 0,
                        "t1": 2,
                        "t2": 5,
                        "meta": {
                            "bold": True
                        }
                    }
                ]
            }
        ])