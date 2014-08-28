from core.service.svc_main.implementation.service_endpoints.export_endpoints import ExportEndpoints
from core.common.business_logic.service_entity_logic import address_helper, company_helper, industry_helper_clean
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
import datetime
import unittest
import mox


__author__ = 'erezrubinstein'



class TestMainExport(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestMainExport, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params_builder = Dependency("CoreAPIParamsBuilder").value

        # create endpoint object
        self.endpoint = ExportEndpoints(None, None)

        # various needed data
        self.context = { "user": "chicken_woot" }


    def doCleanups(self):
        # call parent clean up
        super(TestMainExport, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_get_geoprocessing_loader_files__one_date(self):
        """
        Test that sending in one date and a few companies will break down the data correctly
        """

        # create expected values
        dates = [datetime.datetime(2012, 1, 1)]

        # mock companies
        mock_company_ids = [1, 2]

        # create mock industries (and companies belonging to them)
        # map company 3 maps to industry 1 and company 4 to industry 2
        mock_industries = [1, 2]
        mock_company_to_industry_dict = { 3: 1, 4: 2 }

        # create list of all companies and company to name mappings
        # company 1 and 2 are distinct.  companies 3 and 4 belong to the same industry
        mock_all_company_ids = { 1, 2, 3, 4 }
        mock_company_ids_to_file_name_dict = { 1: "woot", 2: "chicken", 3: "danger_zone_industry", 4: "danger_zone_industry" }

        # create mock stores for the companies
        # stores 1 and 12 belong to the same company.  store 2 belongs to a second company.  stores 3 and 4 belong to the same industry
        mock_store_1 = self.__create_mock_store(1, 1, [datetime.datetime(2010, 1, 1), datetime.datetime(2013, 2, 1)])
        mock_store_12 = self.__create_mock_store(12, 1, [datetime.datetime(2010, 1, 1), datetime.datetime(2013, 2, 1)])
        mock_store_2 = self.__create_mock_store(2, 2, [None, datetime.datetime(2013, 2, 1)])
        mock_store_3 = self.__create_mock_store(3, 3, [datetime.datetime(2010, 1, 1), None])
        mock_store_4 = self.__create_mock_store(4, 4, None)
        mock_stores = [mock_store_1, mock_store_12, mock_store_2, mock_store_3, mock_store_4]

        # create mock addresses
        mock_address_1 = self.__create_mock_address(1)
        mock_address_12 = self.__create_mock_address(12)
        mock_address_2 = self.__create_mock_address(2)
        mock_address_3 = self.__create_mock_address(3)
        mock_address_4 = self.__create_mock_address(4)
        mock_address_ids = { 1, 12, 2, 3, 4 }
        mock_addresses = [mock_address_1, mock_address_12, mock_address_2, mock_address_3, mock_address_4]
        mock_address_dictionary = convert_entity_list_to_dictionary(mock_addresses)

        # stub out various queries
        self.mox.StubOutWithMock(self.endpoint, "_get_company_ids_from_industries")
        self.mox.StubOutWithMock(self.endpoint, "_get_stores_by_companies_and_dates")
        self.mox.StubOutWithMock(address_helper, "get_addresses_by_id")
        self.mox.StubOutWithMock(self.endpoint, "_get_file_name_dictionary_from_raw_stores_list")
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")

        # start recording
        self.endpoint._get_company_ids_from_industries(mock_industries, mock_company_ids).AndReturn(mock_company_to_industry_dict)
        self.endpoint._get_stores_by_companies_and_dates(mock_all_company_ids, dates, "context").AndReturn(mock_stores)
        address_helper.get_addresses_by_id(mock_address_ids, "context").AndReturn(mock_addresses)
        self.endpoint._get_file_name_dictionary_from_raw_stores_list(mock_stores, mock_company_to_industry_dict, "context").AndReturn(mock_company_ids_to_file_name_dict)

        # replay
        self.mox.ReplayAll()

        # run the test
        response = self.endpoint.get_geoprocessing_loader_files(mock_company_ids, mock_industries, dates, "context")

        # response should look like this
        flatten_method = self.endpoint._get_flat_get_processing_loader_dictionary
        expected_response = {
            "2012-01-01": {
                "woot": [flatten_method(mock_store_1, mock_address_dictionary), flatten_method(mock_store_12, mock_address_dictionary)],
                "chicken": [flatten_method(mock_store_2, mock_address_dictionary)],
                "danger_zone_industry": [flatten_method(mock_store_3, mock_address_dictionary), flatten_method(mock_store_4, mock_address_dictionary)]
            }
        }

        # make sure the response is correct
        self.assertEqual(response, expected_response)


    def test_get_geoprocessing_loader_files__two_dates(self):
        """
        Test that sending in one date and a few companies will break down the data correctly
        """

        # create expected values
        dates = [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1)]

        # mock companies
        mock_company_ids = [1, 2]

        # create mock industries (and companies belonging to them)
        # map company 3 maps to industry 1 and company 4 to industry 2
        mock_industries = [1, 2]
        mock_company_to_industry_dict = { 3: 1, 4: 2 }

        # create list of all companies and company to name mappings
        # company 1 and 2 are distinct.  companies 3 and 4 belong to the same industry
        mock_all_company_ids = { 1, 2, 3, 4 }
        mock_company_ids_to_file_name_dict = { 1: "woot", 2: "chicken", 3: "danger_zone_industry", 4: "danger_zone_industry" }

        # create mock stores for the companies
        # stores 1 and 12 belong to the same company.  store 2 belongs to a second company.  stores 3 and 4 belong to the same industry
        mock_store_1 = self.__create_mock_store(1, 1, [datetime.datetime(2010, 1, 1), datetime.datetime(2012, 2, 1)])
        mock_store_12 = self.__create_mock_store(12, 1, [datetime.datetime(2010, 1, 1), datetime.datetime(2013, 2, 1)])
        mock_store_2 = self.__create_mock_store(2, 2, [None, datetime.datetime(2012, 2, 1)])
        mock_store_3 = self.__create_mock_store(3, 3, [datetime.datetime(2010, 1, 1), datetime.datetime(2012, 2, 1)])
        mock_store_4 = self.__create_mock_store(4, 4, None)
        mock_stores = [mock_store_1, mock_store_12, mock_store_2, mock_store_3, mock_store_4]

        # create mock addresses
        mock_address_1 = self.__create_mock_address(1)
        mock_address_12 = self.__create_mock_address(12)
        mock_address_2 = self.__create_mock_address(2)
        mock_address_3 = self.__create_mock_address(3)
        mock_address_4 = self.__create_mock_address(4)
        mock_address_ids = { 1, 12, 2, 3, 4 }
        mock_addresses = [mock_address_1, mock_address_12, mock_address_2, mock_address_3, mock_address_4]
        mock_address_dictionary = convert_entity_list_to_dictionary(mock_addresses)

        # stub out various queries
        self.mox.StubOutWithMock(self.endpoint, "_get_company_ids_from_industries")
        self.mox.StubOutWithMock(self.endpoint, "_get_stores_by_companies_and_dates")
        self.mox.StubOutWithMock(address_helper, "get_addresses_by_id")
        self.mox.StubOutWithMock(self.endpoint, "_get_file_name_dictionary_from_raw_stores_list")
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")

        # start recording
        self.endpoint._get_company_ids_from_industries(mock_industries, mock_company_ids).AndReturn(mock_company_to_industry_dict)
        self.endpoint._get_stores_by_companies_and_dates(mock_all_company_ids, dates, "context").AndReturn(mock_stores)
        address_helper.get_addresses_by_id(mock_address_ids, "context").AndReturn(mock_addresses)
        self.endpoint._get_file_name_dictionary_from_raw_stores_list(mock_stores, mock_company_to_industry_dict, "context").AndReturn(mock_company_ids_to_file_name_dict)

        # replay
        self.mox.ReplayAll()

        # run the test
        response = self.endpoint.get_geoprocessing_loader_files(mock_company_ids, mock_industries, dates, "context")

        # response should look like this
        flatten_method = self.endpoint._get_flat_get_processing_loader_dictionary
        expected_response = {
            "2012-01-01": {
                "woot": [flatten_method(mock_store_1, mock_address_dictionary), flatten_method(mock_store_12, mock_address_dictionary)],
                "chicken": [flatten_method(mock_store_2, mock_address_dictionary)],
                "danger_zone_industry": [flatten_method(mock_store_3, mock_address_dictionary), flatten_method(mock_store_4, mock_address_dictionary)]
            },
            "2013-01-01": {
                "woot": [flatten_method(mock_store_12, mock_address_dictionary)],
                "chicken": [],
                "danger_zone_industry": [flatten_method(mock_store_4, mock_address_dictionary)]
            }
        }

        # make sure the response is correct
        self.assertEqual(response, expected_response)


    def test_get_company_ids_from_industries(self):

        # create fake data
        mock_industry_ids = [1, 2]
        mock_company_to_industry_dict = {
            1: 1,
            2: 1,
            3: 1,
            4: 2,
            5: 2
        }
        mock_company_ids_to_exclude = [3, 5]

        # stub out methods
        self.mox.StubOutWithMock(company_helper, "select_company_ids_by_primary_industry_ids")

        # start recording
        company_helper.select_company_ids_by_primary_industry_ids(mock_industry_ids).AndReturn(mock_company_to_industry_dict)

        # replay all
        self.mox.ReplayAll()

        # go
        results = self.endpoint._get_company_ids_from_industries(mock_industry_ids, mock_company_ids_to_exclude)

        # make sure we get companies minus the ones to exclude
        self.assertEqual(results, {
            1: 1,
            2: 1,
            4: 2
        })

    def test_get_file_name_dictionary_from_raw_stores_list(self):

        # create 5 mock stores
        mock_raw_stores = [
            self.__create_mock_store(1, 1, None),
            self.__create_mock_store(2, 1, None),
            self.__create_mock_store(3, 3, None),
            self.__create_mock_store(4, 4, None),
            self.__create_mock_store(4, 5, None)
        ]

        # map companies (and stores) 4 and 5 to industry 1
        mock_company_to_industry_ids = {
            4: 1,
            5: 1
        }

        # mock company and industry names
        mock_company_names = [
            { "_id": 1, "name": "chicken" },
            { "_id": 3, "name": "woot" }
        ]
        mock_industry_names = [{ "_id": 1, "name": "chilly_willy" }]

        # stub out methods
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")
        self.mox.StubOutWithMock(industry_helper_clean, "select_industry_names_by_ids")

        # start recording
        company_helper.select_companies_by_id([1, 3], self.context).AndReturn(mock_company_names)
        industry_helper_clean.select_industry_names_by_ids({ 1 }).AndReturn(mock_industry_names)

        # replay all
        self.mox.ReplayAll()

        # go
        results = self.endpoint._get_file_name_dictionary_from_raw_stores_list(mock_raw_stores, mock_company_to_industry_ids, self.context)

        # make sure results are mapped correctly
        self.assertEqual(results, {
            1: "chicken",
            3: "woot",
            4: "chilly_willy",
            5: "chilly_willy"
        })

    # ------------------------------------------ Private Methods ------------------------------------------ #

    def __create_mock_store(self, store_id, company_id, interval):
        return {
            "_id": store_id,
            "data": {
                "company_id": company_id,
                "phone": "woot",
                "company_name": company_id,
                "store_format": "chicken",
                "store_number": "danger_zone",
                "note": "yoyoma"
            },
            "links": {
                "address": {
                    "address_assignment": [
                        {
                            "entity_id_to": store_id
                        }
                    ]
                }
            },
            "interval": interval
        }

    def __create_mock_address(self, address_id):
        return {
            "_id": address_id,
            "data": {
                "street_number": "woot",
                "street": "woot",
                "city": "woot",
                "state": "woot",
                "zip": "woot",
                "shopping_center": "woot",
                "suite": "woot",
                "latitude": "woot",
                "longitude": "woot"
            }
        }


if __name__ == '__main__':
    unittest.main()
