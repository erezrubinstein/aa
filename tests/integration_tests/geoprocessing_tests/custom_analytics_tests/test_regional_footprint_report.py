import pprint
import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from common.utilities.misc_utilities import DataAccessNamedRow
from geoprocessing.custom_analytics.reports.custom_analytics_regional_footprint_report import CustomAnalyticsRegionalFootprintReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import *

__author__ = 'erezrubinstein'

class RegionalFootprintReportTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # register the dependencies
        register_concrete_dependencies()

        # define three dates
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

        # create several addresses for different states from different divisions
        cls.address_east_north_central_division = insert_test_address(-1, 1, governing_district = "WI")
        cls.address_west_north_central_division = insert_test_address(-1, 1, governing_district = "SD")
        cls.address_middle_atlantic_division = insert_test_address(-1, 1, governing_district = "PA")
        cls.address_new_england_division = insert_test_address(-1, 1, governing_district = "VT")
        cls.address_east_south_central_division = insert_test_address(-1, 1, governing_district = "TN")
        cls.address_south_atlantic_division = insert_test_address(-1, 1, governing_district = "WV")
        cls.address_west_south_central_division = insert_test_address(-1, 1, governing_district = "TX")
        cls.address_mountain_division = insert_test_address(-1, 1, governing_district = "WY")
        cls.address_pacific_division = insert_test_address(-1, 1, governing_district = "WA")

        # for company 1, create a store for every division in t0, then for only 1 division in t1
        # t0
        insert_test_store(cls.company_id_1, cls.address_east_north_central_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_west_north_central_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_middle_atlantic_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_new_england_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_east_south_central_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_south_atlantic_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_west_south_central_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_mountain_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_1, cls.address_pacific_division, assumed_opened_date = date_1)
        # t1
        insert_test_store(cls.company_id_1, cls.address_east_north_central_division, assumed_opened_date = date_2)

        # for company 2, create a store in two divisions for t0, then close 1 and open 3 for t1.
        # t0
        insert_test_store(cls.company_id_2, cls.address_east_north_central_division, assumed_opened_date = date_1)
        insert_test_store(cls.company_id_2, cls.address_east_north_central_division, assumed_opened_date = date_1, assumed_closed_date = date_2)
        insert_test_store(cls.company_id_2, cls.address_west_north_central_division, assumed_opened_date = date_1)
        # t1
        cls.store_id_1 = insert_test_store(cls.company_id_2, cls.address_east_north_central_division, assumed_opened_date = date_2)
        insert_test_store(cls.company_id_2, cls.address_east_north_central_division, assumed_opened_date = date_2)

        # company 3 has no stores... blah!

        # insert a cbsa and a community for one of the stores
        insert_cbsa_store_match(1, cls.store_id_1)

        # insert a county match for one of the stores
        insert_county_store_match(1, cls.store_id_1)

        # get all cbsas and all counties
        cls.cbsas = select_all_cbsas()
        cls.counties = select_all_counties_with_state()


    @classmethod
    def tearDownClass(cls):

        # delete test data (backwards)
        delete_all_from_cbsa_store_matches()
        delete_all_from_county_store_matches()
        delete_all_stores(cls.company_id_1)
        delete_all_stores(cls.company_id_2)
        delete_all_stores(cls.company_id_3)
        delete_test_address(cls.address_east_north_central_division)
        delete_test_address(cls.address_west_north_central_division)
        delete_test_address(cls.address_middle_atlantic_division)
        delete_test_address(cls.address_new_england_division)
        delete_test_address(cls.address_east_south_central_division)
        delete_test_address(cls.address_south_atlantic_division)
        delete_test_address(cls.address_west_south_central_division)
        delete_test_address(cls.address_mountain_division)
        delete_test_address(cls.address_pacific_division)
        delete_test_company(cls.company_id_1)
        delete_test_company(cls.company_id_2)
        delete_test_company(cls.company_id_3)

        # clear the dependencies
        dependencies.clear()


    def test_regional_footprint(self):

        # create the report
        report = CustomAnalyticsRegionalFootprintReport(self.time_series)

        # truncate the report
        report.lets_make_a_run_for_the_border()

        # run the report
        report.taco_flavored_kisses()

        # query the report
        results = report.omg_they_killed_kenny()

        # group the results nicely, according to the excel logic
        excel_results = report._get_excel_data_sets(results)

        # use a regular assert, not the built in self.assertEquals.
        # this is because an error would take forever to format since these dictionaries are huge...
        # DON'T CHANGE WITHOUT TALKING TO EREZ
        assert excel_results == [
            {
                "headers": ["Banner Name", "Street Number", "Street", "City", "State", "Zip Code", "Region", "Division", "CBSA", "County", "Community Code", "Community Description"],
                "label": "t0 - all - detail",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "SD",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "West North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "PA",
                        "Zip Code": "11111",
                        "Region": "Northeast Region",
                        "Division": "Middle Atlantic Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "VT",
                        "Zip Code": "11111",
                        "Region": "Northeast Region",
                        "Division": "New England Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "TN",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "East South Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WV",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "South Atlantic Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "TX",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "West South Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WY",
                        "Zip Code": "11111",
                        "Region": "West Region",
                        "Division": "Mountain Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WA",
                        "Zip Code": "11111",
                        "Region": "West Region",
                        "Division": "Pacific Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "SD",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "West North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    }
                ]
            },
            {
                "label": "t0 - all - region summary",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Store Counts",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 1,
                                "West North Central Division": 1,
                                "Middle Atlantic Division": 1,
                                "New England Division": 1,
                                "East South Central Division": 1,
                                "South Atlantic Division": 1,
                                "West South Central Division": 1,
                                "Mountain Division": 1,
                                "Pacific Division": 1,
                                "Total": 9
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 2,
                                "West North Central Division": 1,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 3
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    },
                    {
                        "header": "Percent of Total Stores",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 11.11111,
                                "West North Central Division": 11.11111,
                                "Middle Atlantic Division": 11.11111,
                                "New England Division": 11.11111,
                                "East South Central Division": 11.11111,
                                "South Atlantic Division": 11.11111,
                                "West South Central Division": 11.11111,
                                "Mountain Division": 11.11111,
                                "Pacific Division": 11.11111,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 66.66667,
                                "West North Central Division": 33.33333,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    }
                ]
            },
            {
                "label": "t0 - all - cbsa summary",
                "type": "multi_table",
                "tables": self._get_cbsa_rows({
                    "Company 1": {
                        "N/A": 9
                    },
                    "Company 2": {
                        "N/A": 3
                    },
                    "Company 3": {}
                })
            },
            {
                "label": "t0 - all - county summary",
                "type": "multi_table",
                "tables": self._get_county_rows({
                    "Company 1": {
                        "N/A": 9
                    },
                    "Company 2": {
                        "N/A": 3
                    },
                    "Company 3": {}
                })
            },
            {
                "headers": ["Banner Name", "Street Number", "Street", "City", "State", "Zip Code", "Region", "Division", "CBSA", "County", "Community Code", "Community Description"],
                "label": "t1 - all - detail",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "SD",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "West North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "PA",
                        "Zip Code": "11111",
                        "Region": "Northeast Region",
                        "Division": "Middle Atlantic Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "VT",
                        "Zip Code": "11111",
                        "Region": "Northeast Region",
                        "Division": "New England Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "TN",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "East South Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WV",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "South Atlantic Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "TX",
                        "Zip Code": "11111",
                        "Region": "South Region",
                        "Division": "West South Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WY",
                        "Zip Code": "11111",
                        "Region": "West Region",
                        "Division": "Mountain Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WA",
                        "Zip Code": "11111",
                        "Region": "West Region",
                        "Division": "Pacific Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "Rochester, MN Metro Area",
                        "County": "Cuming County, NE",
                        "Community Code": 7,
                        "Community Description": "Nonmetro - Urban population of 2,500 to 19,999, not adjacent to a metro area"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "SD",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "West North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    }
                ]
            },
            {
                "label": "t1 - all - region summary",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Store Counts",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 2,
                                "West North Central Division": 1,
                                "Middle Atlantic Division": 1,
                                "New England Division": 1,
                                "East South Central Division": 1,
                                "South Atlantic Division": 1,
                                "West South Central Division": 1,
                                "Mountain Division": 1,
                                "Pacific Division": 1,
                                "Total": 10
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 3,
                                "West North Central Division": 1,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 4
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    },
                    {
                        "header": "Percent of Total Stores",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 20,
                                "West North Central Division": 10,
                                "Middle Atlantic Division": 10,
                                "New England Division": 10,
                                "East South Central Division": 10,
                                "South Atlantic Division": 10,
                                "West South Central Division": 10,
                                "Mountain Division": 10,
                                "Pacific Division": 10,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 75,
                                "West North Central Division": 25,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    }
                ]
            },
            {
                "label": "t1 - all - cbsa summary",
                "type": "multi_table",
                "tables": self._get_cbsa_rows({
                    "Company 1": {
                        "N/A": 10
                    },
                    "Company 2": {
                        "N/A": 3,
                        "Rochester, MN Metro Area": 1
                    },
                    "Company 3": {}
                })
            },
            {
                "label": "t1 - all - county summary",
                "type": "multi_table",
                "tables": self._get_county_rows({
                    "Company 1": {
                        "N/A": 10
                    },
                    "Company 2": {
                        "N/A": 3,
                        "Cuming County, NE": 1
                    },
                    "Company 3": {}
                })
            },
            {
                "headers": ["Banner Name", "Street Number", "Street", "City", "State", "Zip Code", "Region", "Division", "CBSA", "County", "Community Code", "Community Description"],
                "label": "t1 - closings - detail",
                "rows": [
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    }
                ]
            },
            {
                "label": "t1 - closings - region summary",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Store Counts",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 1,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 1
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    },
                    {
                        "header": "Percent of Total Stores",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 100,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    }
                ]
            },
            {
                "label": "t1 - closings - cbsa summary",
                "type": "multi_table",
                "tables": self._get_cbsa_rows({
                    "Company 1": {},
                    "Company 2": {
                        "N/A": 1
                    },
                    "Company 3": {}
                })
            },
            {
                "label": "t1 - closings - county summary",
                "type": "multi_table",
                "tables": self._get_county_rows({
                    "Company 1": {},
                    "Company 2": {
                        "N/A": 1
                    },
                    "Company 3": {}
                })
            },
            {
                "headers": ["Banner Name", "Street Number", "Street", "City", "State", "Zip Code", "Region", "Division", "CBSA", "County", "Community Code", "Community Description"],
                "label": "t1 - openings - detail",
                "rows": [
                    {
                        "Banner Name": "Company 1",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "Rochester, MN Metro Area",
                        "County": "Cuming County, NE",
                        "Community Code": 7,
                        "Community Description": "Nonmetro - Urban population of 2,500 to 19,999, not adjacent to a metro area"
                    },
                    {
                        "Banner Name": "Company 2",
                        "Street Number": "0",
                        "Street": "UNITTEST",
                        "City": "UNITTEST",
                        "State": "WI",
                        "Zip Code": "11111",
                        "Region": "Midwest Region",
                        "Division": "East North Central Division",
                        "CBSA": "N/A",
                        "County": "N/A",
                        "Community Code": "N/A",
                        "Community Description": "N/A"
                    }
                ]
            },
            {
                "label": "t1 - openings - region summary",
                "type": "multi_table",
                "tables": [
                    {
                        "header": "Store Counts",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 1,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 1
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 2,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 2
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    },
                    {
                        "header": "Percent of Total Stores",
                        "headers": [
                            ["", "Midwest Region", "Midwest Region", "Northeast Region", "Northeast Region", "South Region", "South Region", "South Region", "West Region", "West Region", ""],
                            ["Banner Name", "East North Central Division", "West North Central Division", "Middle Atlantic Division", "New England Division", "East South Central Division", "South Atlantic Division", "West South Central Division", "Mountain Division", "Pacific Division", "Total"]
                        ],
                        "rows": [
                            {
                                "Banner Name": "Company 1",
                                "East North Central Division": 100,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 2",
                                "East North Central Division": 100,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 100
                            },
                            {
                                "Banner Name": "Company 3",
                                "East North Central Division": 0,
                                "West North Central Division": 0,
                                "Middle Atlantic Division": 0,
                                "New England Division": 0,
                                "East South Central Division": 0,
                                "South Atlantic Division": 0,
                                "West South Central Division": 0,
                                "Mountain Division": 0,
                                "Pacific Division": 0,
                                "Total": 0
                            }
                        ]
                    }
                ]
            },
            {
                "label": "t1 - openings - cbsa summary",
                "type": "multi_table",
                "tables": self._get_cbsa_rows({
                    "Company 1": {
                        "N/A": 1
                    },
                    "Company 2": {
                        "N/A": 1,
                        "Rochester, MN Metro Area": 1
                    },
                    "Company 3": {}
                })
            },
            {
                "label": "t1 - openings - county summary",
                "type": "multi_table",
                "tables": self._get_county_rows({
                    "Company 1": {
                        "N/A": 1
                    },
                    "Company 2": {
                        "N/A": 1,
                        "Cuming County, NE": 1
                    },
                    "Company 3": {}
                })
            }
        ], "results don't match.  Not including results because the unit test print difference method takes FOREVVVVVVVVER to print this (like 15 minutes sucka)"

    def _get_cbsa_rows(self, companies):

        # get all cbsas and make into a list
        cbsas = list(self.cbsas)

        # add "N/A" to cbsas
        cbsas.append(DataAccessNamedRow(cbsa_name = "N/A", population = "N/A", pci = "N/A", agg_income = "N/A"))

        # sort cbsas
        cbsas = sorted(cbsas, key = lambda cbsa: cbsa.cbsa_name)

        # create the base total row and total percent row
        total_row = {
            "CBSA Name": "Total",
            "Population": "N/A",
            "Per Capita Income": "N/A",
            "Aggregate Income": "N/A",
            "Total": 0,
            "meta":  { "bold": True }
        }
        total_row_percent = {
            "CBSA Name": "Total",
            "Population": "N/A",
            "Per Capita Income": "N/A",
            "Aggregate Income": "N/A",
            "Total": 100,
            "meta":  { "bold": True }
        }

        # set company totals to zero for the regular total and 100 for the percent
        for company in companies:
            total_row[company] = 0
            total_row_percent[company] = 100

        # start with empty rows
        rows = []
        percent_rows = []

        # loop through every cbsa
        for cbsa in cbsas:

            # create the static row fields
            row = {
                "CBSA Name": cbsa.cbsa_name,
                "Population": cbsa.population,
                "Per Capita Income": cbsa.pci,
                "Aggregate Income": cbsa.agg_income,
                "Total": 0
            }

            # loop through every company
            for company in companies:

                # get num stores (if company has any here)
                num_stores = companies[company].get(cbsa.cbsa_name, 0)
                row[company] = num_stores
                row["Total"] += num_stores
                total_row[company] += num_stores
                total_row["Total"] += num_stores

            # create percent row, which will be set the raw number now.  We'll divide by the total store count at the end
            percent_row = {
                company: row[company]
                for company in companies
            }
            percent_row["CBSA Name"] = cbsa.cbsa_name
            percent_row["Population"] = cbsa.population
            percent_row["Per Capita Income"] = cbsa.pci
            percent_row["Aggregate Income"] = cbsa.agg_income
            percent_row["Total"] = row["Total"]

            # add to rows
            rows.append(row)
            percent_rows.append(percent_row)


        # figure out the percents (after we have all the store counts totalled)
        for row in percent_rows:

            # calculate % for every company
            for company in companies:
                row[company] = self._get_percent_of(row[company], total_row[company])

            # get the total for this region compared with all the stores
            row["Total"] = self._get_percent_of(row["Total"], total_row["Total"])

        # add the total rows
        rows.append(total_row)
        percent_rows.append(total_row_percent)

        # booya
        return [
            {
                "header": "Store Counts",
                "headers": ["CBSA Name", "Population", "Per Capita Income", "Aggregate Income", "Company 1", "Company 2", "Company 3", "Total"],
                "headers_format": "vertical",
                "headers_indexes_to_ignore_format": [0, 1, 2, 3],
                "rows": rows
            },
            {
                "header": "Percent of Total Stores",
                "headers_format": "vertical",
                "headers_indexes_to_ignore_format": [0, 1, 2, 3],
                "headers": ["CBSA Name", "Population", "Per Capita Income", "Aggregate Income", "Company 1", "Company 2", "Company 3", "Total"],
                "rows": percent_rows
            }
        ]


    def _get_county_rows(self, companies):

        # get all counties and make into a list
        counties = list(self.counties)

        # add "N/A" to counties
        counties.append(DataAccessNamedRow(community_code = "N/A", community_description = "N/A", county_name = "N/A", population = "N/A", pci = "N/A", agg_income = "N/A"))

        # sort counties
        counties = sorted(counties, key = lambda county: county.county_name)

        # create the base total row and total percent row
        total_row = {
            "County Name": "Total",
            "Population": "N/A",
            "Per Capita Income": "N/A",
            "Aggregate Income": "N/A",
            "Community Code": "N/A",
            "Community Description": "N/A",
            "Total": 0,
            "meta":  { "bold": True }
        }
        total_row_percent = {
            "County Name": "Total",
            "Population": "N/A",
            "Per Capita Income": "N/A",
            "Aggregate Income": "N/A",
            "Community Code": "N/A",
            "Community Description": "N/A",
            "Total": 100,
            "meta":  { "bold": True }
        }

        # set company totals to zero for the regular total and 100 for the percent
        for company in companies:
            total_row[company] = 0
            total_row_percent[company] = 100

        # start with empty rows
        rows = []
        percent_rows = []

        # loop through every county
        for county in counties:

            # create the static row fields
            row = {
                "County Name": county.county_name,
                "Population": county.population,
                "Per Capita Income": county.pci,
                "Aggregate Income": county.agg_income,
                "Community Code": county.community_code,
                "Community Description": county.community_description,
                "Total": 0
            }

            # loop through every company
            for company in companies:

                # get num stores (if company has any here)
                num_stores = companies[company].get(county.county_name, 0)
                row[company] = num_stores
                row["Total"] += num_stores
                total_row[company] += num_stores
                total_row["Total"] += num_stores

            # create percent row, which will be set the raw number now.  We'll divide by the total store count at the end
            percent_row = {
                company: row[company]
                for company in companies
            }
            percent_row["Community Code"] = county.community_code
            percent_row["Community Description"] = county.community_description
            percent_row["County Name"] = county.county_name
            percent_row["Population"] = county.population
            percent_row["Per Capita Income"] = county.pci
            percent_row["Aggregate Income"] = county.agg_income
            percent_row["Total"] = row["Total"]

            # add to rows
            rows.append(row)
            percent_rows.append(percent_row)


        # figure out the percents (after we have all the store counts totalled)
        for row in percent_rows:

            # calculate % for every company
            for company in companies:
                row[company] = self._get_percent_of(row[company], total_row[company])

            # get the total for this region compared with all the stores
            row["Total"] = self._get_percent_of(row["Total"], total_row["Total"])

        # add the total rows
        rows.append(total_row)
        percent_rows.append(total_row_percent)

        # booya
        return [
            {
                "header": "Store Counts",
                "headers": ["County Name", "Community Code", "Community Description", "Population", "Per Capita Income", "Aggregate Income", "Company 1", "Company 2", "Company 3", "Total"],
                "headers_format": "vertical",
                "headers_indexes_to_ignore_format": [0, 1, 2, 3, 4, 5],
                "rows": rows
            },
            {
                "header": "Percent of Total Stores",
                "headers": ["County Name", "Community Code", "Community Description", "Population", "Per Capita Income", "Aggregate Income", "Company 1", "Company 2", "Company 3", "Total"],
                "headers_format": "vertical",
                "headers_indexes_to_ignore_format": [0, 1, 2, 3, 4, 5],
                "rows": percent_rows
            }
        ]

    def _get_percent_of(self, value, total):

        if total:
            return round((value / float(total)) * 100, 5)

        else:
            return 0

