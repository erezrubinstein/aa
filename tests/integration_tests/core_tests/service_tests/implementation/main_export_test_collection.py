from __future__ import division
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.utilities.helpers import ensure_id
from core.service.svc_main.implementation.service_endpoints.export_endpoints import ExportEndpoints
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir,\
    insert_test_trade_area, insert_test_address, insert_test_store, insert_test_industry, create_store_with_rir
from core.common.utilities.include import *
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import *
from tests.integration_tests.utilities.testing_utilities import convert_entity_list_to_dictionary

class MainExportTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "main_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

        # no diff!!
        self.test_case.maxDiff = None

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def main_export_test_companies(self):

        # add a company
        data = {
            "type": "retail_parent",
            "status": "operating",
            "ticker": "****",
            "exchange": "NYSE",
            "workflow": { "current": { "status":"new" }},
            "valid" : {
                "v1_2" : {
                    "analytics" : {
                        "demographics" : True,
                        "competition" : False,
                        "stores" : True,
                        "monopolies" : False,
                        "economics" : True,
                        "white_space" : False
                    }
                }
            }
        }
        company_id = self.mds_access.call_add_entity(entity_type="company",
                                                     name="Provi Company 123",
                                                     data=data,
                                                     context_rec=self.context)

        # add an industry
        data = {
            "source_vendor": "Nexus",
            "source_version": "2007",
            "industry_code": "000",
            "industry_name": "Test Industry",
            "industry_level": "1"
        }
        industry_id = self.mds_access.call_add_entity(entity_type="industry",
                                                      name="Provi Industry 123",
                                                      data=data,
                                                      context_rec=self.context)

        # link company to industry
        self.main_access.mds.call_add_link(entity_type_from="company",
                                           entity_id_from=company_id,
                                           entity_role_from="primary_industry_classification",
                                           entity_type_to="industry",
                                           entity_id_to=industry_id,
                                           entity_role_to="primary_industry",
                                           relation_type="industry_classification",
                                           context_rec=self.context)


        # add a store and link it to the company
        store_id = insert_test_store(company_id, [None,None])
        self.main_access.mds.call_add_link(entity_type_from="company",
                                           entity_id_from=company_id,
                                           entity_role_from="retail_parent",
                                           entity_type_to="store",
                                           entity_id_to=store_id,
                                           entity_role_to="store",
                                           relation_type="store_ownership",
                                           context_rec=self.context)

        expected_results_list = [u'Provi Company 123', u'****', None, None, u'NYSE', u'Operating', u'Retail Parent', u'New', u'Provi Industry 123', "Not Published", 1, 1,
                                 "Valid", "Invalid", "Valid", "Invalid", "Valid", "Invalid"]
        expected_field_list = ["Company ID", "Name", "Ticker", "Parent Name", "Parent Ticker", "Exchange", "Operating Status",
                               "Type", "Workflow Status", "Primary Industry", "Industry Competition Status", "Total Store Count", "Open Store Count",
                               "Demographics Status", "Competition Status", "Stores Status", "Monopolies Status", "Economics Status", "White Space Status"]
        expected_field_meta = {}

        params = {"entity_types": ["company"], "data_type": "data"}
        self.main_access.call_delete_preset_cache(params=params)

        params = {"sortIndex": 0,
                  "sortDirection": 1,
                  "fieldFilters": None,
                  "pageIndex": 0,
                  "pageSize": 20}

        response = self.main_access.call_get_preset(resource="/export/preset/companies", params=params, context=self.context)

        self.test_case.assertIsNotNone(response)
        self.test_case.assertIsInstance(response, dict)

        self.test_case.assertIn("results", response)
        pprint.pprint(response["results"][0][1:])
        self.test_case.assertEqual(response["results"][0][1:], expected_results_list)

        self.test_case.assertIn("field_list", response)
        self.test_case.assertEqual(response["field_list"], expected_field_list)

        self.test_case.assertIn("field_meta", response)
        self.test_case.assertEqual(response["field_meta"], expected_field_meta)


    def main_export_test_companies_invalid_analytics(self):

        # create 6 companies (6 with invalid analytics, 1 with all valid, 1 with nothing)
        company_id_1 = insert_test_company(valid_status = self._create_valid_analytics(False, True, True, True, True, True))
        company_id_2 = insert_test_company(valid_status = self._create_valid_analytics(True, False, True, True, True, True))
        company_id_3 = insert_test_company(valid_status = self._create_valid_analytics(True, True, False, True, True, True))
        company_id_4 = insert_test_company(valid_status = self._create_valid_analytics(True, True, True, False, True, True))
        company_id_5 = insert_test_company(valid_status = self._create_valid_analytics(True, True, True, True, False, True))
        company_id_6 = insert_test_company(valid_status = self._create_valid_analytics(True, True, True, True, True, False))
        insert_test_company(valid_status = self._create_valid_analytics(True, True, True, True, True, True))
        insert_test_company()

        resource = "/export/preset/companies_invalid_analytics"
        companies = self.main_access.call_get_preset(resource, None, self.context)

        self.test_case.assertEqual(companies, {
             "id_field": None,
             "id_index": None,
             "field_list": ["ID", "Company Name", "Ticker", "Demographics", "Competition", "Stores", "Monopolies", "Economics", "White Space"],
             "results": [
                 [company_id_1, "UNITTESTCOMPANY", "", "Invalid", "Valid", "Valid", "Valid", "Valid", "Valid"],
                 [company_id_2, "UNITTESTCOMPANY", "", "Valid", "Invalid", "Valid", "Valid", "Valid", "Valid"],
                 [company_id_3, "UNITTESTCOMPANY", "", "Valid", "Valid", "Invalid", "Valid", "Valid", "Valid"],
                 [company_id_4, "UNITTESTCOMPANY", "", "Valid", "Valid", "Valid", "Invalid", "Valid", "Valid"],
                 [company_id_5, "UNITTESTCOMPANY", "", "Valid", "Valid", "Valid", "Valid", "Invalid", "Valid"],
                 [company_id_6, "UNITTESTCOMPANY", "", "Valid", "Valid", "Valid", "Valid", "Valid", "Invalid"],
             ],
             "field_meta": {},
             "meta": {
                "num_rows": 6,
                "page_index": 0,
                "sort_direction": 1,
                "page_size": 6,
                "sort_index": 0
             }
        })


    def main_export_test_retail_input_records(self):

        company_id = insert_test_company()
        rir_id_A = insert_test_rir(self.context, company_id, '1')
        rir_id_B = insert_test_rir(self.context, company_id, '2')

        resource = "/export/preset/retail_input_records"
        rirs = self.main_access.call_get_preset(resource, None, self.context)

        rir_export_meta = {"has_header": True,
                           "has_metadata": True,
                           "num_rows": 2,
                           "row_format": "list"}

        # self.test_case.assertEqual(rirs["meta"], rir_export_meta)
        self.test_case.assertEqual(rirs["meta"]["num_rows"], rir_export_meta["num_rows"])
        self.test_case.assertEqual(rirs["id_field"], None)
        self.test_case.assertEqual(rirs["id_index"], None)
        self.test_case.assertEqual(rirs["field_list"], RETAIL_INPUT_RECORD_EXPORT_CLEAN_FIELDS)
        self.test_case.assertEqual(rirs["field_meta"], RETAIL_INPUT_RECORD_EXPORT_FIELD_META)

        self.test_case.assertEqual(len(rirs["results"]), 2)
        for rir in rirs["results"]:
            self.test_case.assertEqual(len(rir), len(RETAIL_INPUT_RECORD_EXPORT_DB_FIELDS))
            self.test_case.assertTrue(rir[0] in [rir_id_A, rir_id_B])

    def main_export_stores(self):

        store_helper = StoreHelper()

        company_id = insert_test_company()
        rir_id_A = insert_test_rir(self.context, company_id, '1')
        store_id_A = store_helper.create_new_store(self.context, rir_id_A, async=False)
        rir_id_B = insert_test_rir(self.context, company_id, '2')
        store_id_B = store_helper.create_new_store(self.context, rir_id_B, async=False)

        resource = "/export/preset/stores"
        stores = self.main_access.call_get_preset(resource, None, self.context)

        store_export_meta = {'num_rows': 2,
                             'page_index': 0,
                             'page_size': 2,
                             'sort_direction': 1,
                             'sort_index': 0}

        self.test_case.assertEqual(stores["meta"], store_export_meta)
        self.test_case.assertEqual(stores["id_field"], None)
        self.test_case.assertEqual(stores["id_index"], None)
        self.test_case.assertEqual(stores["field_list"], STORE_EXPORT_CLEAN_FIELDS)
        self.test_case.assertEqual(stores["field_meta"], STORE_EXPORT_FIELD_META)

        self.test_case.assertEqual(len(stores["results"]), 2)
        for store in stores["results"]:
            self.test_case.assertEqual(len(store), len(STORE_EXPORT_FINAL_DB_FIELDS))
            self.test_case.assertTrue(store[0] in [store_id_A, store_id_B])

    def main_export_get_stores_by_companies_and_dates__two_companies(self):
        # create three companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()
        company_id_3 = insert_test_company()

        # create three rirs
        rir_id_1 = insert_test_rir(self.context, company_id_1, '1')
        rir_id_2 = insert_test_rir(self.context, company_id_2, '2')
        rir_id_3 = insert_test_rir(self.context, company_id_3, '3')

        # create three stores
        store_helper = StoreHelper()
        store_id_1 = ensure_id(store_helper.create_new_store(self.context, rir_id_1, async=False))
        store_id_2 = ensure_id(store_helper.create_new_store(self.context, rir_id_2, async=False))
        store_id_3 = ensure_id(store_helper.create_new_store(self.context, rir_id_3, async=False))

        # update all stores to null intervals
        # do batch update since normal update doesn't let us set to null........
        query = {"_id": { "$in": [store_id_1, store_id_2, store_id_3]}}
        self.mds_access.call_batch_update_entities("store", query, {"$set": { "interval": None }}, self.context)

        # select the stores for two companies only
        companies = [company_id_1, company_id_2]
        dates = [datetime.datetime.utcnow()]
        stores = ExportEndpoints(None, None)._get_stores_by_companies_and_dates(companies, dates, self.context)

        # verify that only the first and second stores are there
        stores = convert_entity_list_to_dictionary(stores)
        self.test_case.assertEqual(len(stores), 2)
        self.test_case.assertIn(store_id_1, stores)
        self.test_case.assertIn(store_id_2, stores)

    def main_export_get_stores_by_companies_and_dates__date_queries(self):
        # create company
        company_id = insert_test_company()

        # create several rirs with different as of dates
        rir_id_1 = insert_test_rir(self.context, company_id, '1', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_2 = insert_test_rir(self.context, company_id, '2', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_3 = insert_test_rir(self.context, company_id, '3', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_4 = insert_test_rir(self.context, company_id, '4', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_5 = insert_test_rir(self.context, company_id, '5', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_6 = insert_test_rir(self.context, company_id, '6', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_7 = insert_test_rir(self.context, company_id, '7', as_of_date = datetime.datetime(2010, 1, 1))
        rir_id_8 = insert_test_rir(self.context, company_id, '8', as_of_date = datetime.datetime(2010, 1, 1))

        # create a store for each rir
        store_helper = StoreHelper()
        store_id_1 = ensure_id(store_helper.create_new_store(self.context, rir_id_1, async=False))
        store_id_2 = ensure_id(store_helper.create_new_store(self.context, rir_id_2, async=False))
        store_id_3 = ensure_id(store_helper.create_new_store(self.context, rir_id_3, async=False))
        store_id_4 = ensure_id(store_helper.create_new_store(self.context, rir_id_4, async=False))
        store_id_5 = ensure_id(store_helper.create_new_store(self.context, rir_id_5, async=False))
        store_id_6 = ensure_id(store_helper.create_new_store(self.context, rir_id_6, async=False))
        store_id_7 = ensure_id(store_helper.create_new_store(self.context, rir_id_7, async=False))
        store_id_8 = ensure_id(store_helper.create_new_store(self.context, rir_id_8, async=False))

        # manually update the store intervals to match the model I'm trying to make
        self.mds_access.call_update_entity("store", store_id_1, self.context, "interval", [datetime.datetime(2010, 1, 1), datetime.datetime(2010, 2, 1)]) # outside the range
        self.mds_access.call_update_entity("store", store_id_2, self.context, "interval", [datetime.datetime(2010, 1, 1), datetime.datetime(2013, 2, 1)]) # encompasses entire range
        self.mds_access.call_update_entity("store", store_id_3, self.context, "interval", [datetime.datetime(2013, 1, 1), datetime.datetime(2013, 2, 1)]) # outside the range
        self.mds_access.call_update_entity("store", store_id_4, self.context, "interval", [None, datetime.datetime(2013, 2, 1)])                          # inside the range
        self.mds_access.call_update_entity("store", store_id_5, self.context, "interval", [datetime.datetime(2010, 1, 1), None])                          # inside the range
        self.mds_access.call_update_entity("store", store_id_6, self.context, "interval", [None, datetime.datetime(2011, 2, 1)])                          # outside the range
        self.mds_access.call_update_entity("store", store_id_7, self.context, "interval", [datetime.datetime(2013, 1, 1), None])                          # outside the range
        # do batch update since normal update doesn't let us set to null........
        self.mds_access.call_batch_update_entities("store", {"_id": store_id_8 }, {"$set": { "interval": None }}, self.context)                           # inside the range


        # run query for one date
        dates = [datetime.datetime(2012, 1, 1)]
        companies = [company_id]
        endpoint = ExportEndpoints(None, None)
        stores = endpoint._get_stores_by_companies_and_dates(companies, dates, self.context)

        # verify that only those points within the date come up
        stores = convert_entity_list_to_dictionary(stores)
        self.test_case.assertEqual(len(stores), 4)
        self.test_case.assertIn(store_id_2, stores)
        self.test_case.assertIn(store_id_4, stores)
        self.test_case.assertIn(store_id_5, stores)
        self.test_case.assertIn(store_id_8, stores)

        # run the query again with two dates
        dates = [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1)]
        stores = endpoint._get_stores_by_companies_and_dates(companies, dates, self.context)

        # verify that the correct sores make it with two dates
        stores = convert_entity_list_to_dictionary(stores)
        self.test_case.assertEqual(len(stores), 6)
        self.test_case.assertIn(store_id_2, stores)
        self.test_case.assertIn(store_id_3, stores)
        self.test_case.assertIn(store_id_4, stores)
        self.test_case.assertIn(store_id_5, stores)
        self.test_case.assertIn(store_id_7, stores)
        self.test_case.assertIn(store_id_8, stores)

    def get_geoprocessing_trade_area_competition(self):

        # create mock competitive stores for both trade_areas
        competitive_stores_1 = [
            {
                "end_date": "3000-01-01T00:00:00",
                "start_date": "1900-01-01T00:00:00",
                "away_company_id": "51db29ebf3d31ba33440d86f",
                "weight": 1,
                "away_store_id": 1
            },
            {
                "end_date": "3000-01-01T00:00:00",
                "start_date": "2012-01-01T00:00:00",
                "away_company_id": "51db29ebf3d31ba33440d86f",
                "weight": 1,
                "away_store_id": 2
            }
        ]
        competitive_stores_2 = [
            {
                "end_date": "3000-01-01T00:00:00",
                "start_date": "1900-01-01T00:00:00",
                "away_company_id": "51db29ebf3d31ba33440d86f",
                "weight": 1,
                "away_store_id": 3
            },
            {
                "end_date": "2013-01-01T00:00:00",
                "start_date": "1900-01-01T00:00:00",
                "away_company_id": "51db29ebf3d31ba33440d86f",
                "weight": .5,
                "away_store_id": 4
            }
        ]

        # insert two trade areas, each one having multiple competitions
        trade_area_id_1 = insert_test_trade_area(1, 1, "test company 1", competitive_stores = competitive_stores_1)
        trade_area_id_2 = insert_test_trade_area(2, 2, "test company 2", competitive_stores = competitive_stores_2)

        # create url parameters for sorting/paging
        url_params = '?params={"pageSize":3,"pageIndex":0,"sortIndex":12,"sortDirection":-1}'

        # export the geoprocessing competitive stores
        export_results = self.main_access.call_get_preset("/export/preset/geoprocessing_trade_area_competition" + url_params, None, self.context)

        # verify the results
        self.test_case.assertEqual(export_results, {
            'field_list': ['Trade Area ID', 'Home Store ID', 'Company', 'Threshold', 'Street Number', 'Street', 'City', 'State', 'Zip', 'Phone Number', 'Latitude', 'Longitude', 'Away Store ID', 'Strength', 'Start Date', 'End Date'],
            'field_meta': {},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 4,
                'page_index': 0,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 12
            },
            'results': [
                [trade_area_id_2, 2, "test company 2", "DistanceMiles10", "street_number", "street", "city", "state", "zip", 111, 1, 1, 4, .5, "1900-01-01T00:00:00", "2013-01-01T00:00:00"],
                [trade_area_id_2, 2, "test company 2", "DistanceMiles10", "street_number", "street", "city", "state", "zip", 111, 1, 1, 3, 1, "1900-01-01T00:00:00", "3000-01-01T00:00:00"],
                [trade_area_id_1, 1, "test company 1", "DistanceMiles10", "street_number", "street", "city", "state", "zip", 111, 1, 1, 2, 1, "2012-01-01T00:00:00", "3000-01-01T00:00:00"]
            ]
        })


        # query the second page
        url_params = '?params={"pageSize":3,"pageIndex":1,"sortIndex":12,"sortDirection":-1}'
        export_results = self.main_access.call_get_preset("/export/preset/geoprocessing_trade_area_competition" + url_params, None, self.context)

        # verify results
        self.test_case.assertEqual(export_results, {
            'field_list': ['Trade Area ID', 'Home Store ID', 'Company', 'Threshold', 'Street Number', 'Street', 'City', 'State', 'Zip', 'Phone Number', 'Latitude', 'Longitude', 'Away Store ID', 'Strength', 'Start Date', 'End Date'],
            'field_meta': {},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 4,
                'page_index': 1,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 12
            },
            'results': [
                [trade_area_id_1, 1, "test company 1", "DistanceMiles10", "street_number", "street", "city", "state", "zip", 111, 1, 1, 1, 1, "1900-01-01T00:00:00", "3000-01-01T00:00:00"]
            ]
        })


    def get_geoprocessing_trade_area_demographics(self):

        # insert four trade areas
        trade_area_id_1 = insert_test_trade_area(1, 1, "test company 1", latitude = 1, longitude = -1)
        trade_area_id_2 = insert_test_trade_area(2, 2, "test company 2", latitude = 1, longitude = -1)
        trade_area_id_3 = insert_test_trade_area(3, 3, "test company 3", latitude = 1, longitude = -1)
        trade_area_id_4 = insert_test_trade_area(4, 4, "test company 4", latitude = 1, longitude = -1)

        # export with paging (1st page)
        url_params = '?params={"pageSize":3,"pageIndex":0,"sortIndex":2,"sortDirection":-1}'
        export_results = self.main_access.call_get_preset("/export/preset/geoprocessing_trade_area_demographics" + url_params, None, self.context)

        # verify the results
        self.test_case.assertEqual(export_results, {
            'field_list': ["Company Name", "Trade Area ID", "Store ID", "Trade Area", "Street Number", "Street", "Suite", "City", "State", "Zip Code", "Phone Number", "Latitude",
                           "Longitude", "Population", "Per Capita Income", "Aggregate Income", "Households", "&lt;&nbsp;$15K", "$15-25K", "$25-35K", "$35-50K", "$50-75K",
                           "$75-100K", "$100-150K", "$150-200K", "$200K+"],
            'field_meta': {},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 4,
                'page_index': 0,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 2
            },
            'results': [
                ["test company 4", trade_area_id_4, 4, "DistanceMiles10", "street_number", "street", "suite", "city", "state", "zip", "phone", 1, -1, 142695, 5000, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000],
                ["test company 3", trade_area_id_3, 3, "DistanceMiles10", "street_number", "street", "suite", "city", "state", "zip", "phone", 1, -1, 142695, 5000, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000],
                ["test company 2", trade_area_id_2, 2, "DistanceMiles10", "street_number", "street", "suite", "city", "state", "zip", "phone", 1, -1, 142695, 5000, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000]
            ]
        })

        # export with paging (2nd page)
        url_params = '?params={"pageSize":3,"pageIndex":1,"sortIndex":2,"sortDirection":-1}'
        export_results = self.main_access.call_get_preset("/export/preset/geoprocessing_trade_area_demographics" + url_params, None, self.context)

        # verify the results
        self.test_case.assertEqual(export_results, {
            'field_list': ["Company Name", "Trade Area ID", "Store ID", "Trade Area", "Street Number", "Street", "Suite", "City", "State", "Zip Code", "Phone Number", "Latitude",
                           "Longitude", "Population", "Per Capita Income", "Aggregate Income", "Households", "&lt;&nbsp;$15K", "$15-25K", "$25-35K", "$35-50K", "$50-75K",
                           "$75-100K", "$100-150K", "$150-200K", "$200K+"],
            'field_meta': {},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 4,
                'page_index': 1,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 2
            },
            'results': [
                ["test company 1", trade_area_id_1, 1, "DistanceMiles10", "street_number", "street", "suite", "city", "state", "zip", "phone", 1, -1, 142695, 5000, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000]
            ]
        })

    def get_dupe_stores(self):
        # create 2 companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()

        # create several stores for both companies.
        # stores 1 & 2, 3 & 4 & 5 match phone_number_clean
        # store 6 has no match
        # store 7 & 8 have empty phone numbers and are ignored
        store_1 = create_store_with_rir(company_id_1, phone = "123 456 3333")
        store_2 = create_store_with_rir(company_id_2, phone = "(123)-456-3333")
        store_3 = create_store_with_rir(company_id_1, phone = "444 535 123")
        store_4 = create_store_with_rir(company_id_1, phone = "(444) 535-123")
        store_5 = create_store_with_rir(company_id_2, phone = "444.535.123")
        store_6 = create_store_with_rir(company_id_1, phone = "45766")
        store_7 = create_store_with_rir(company_id_1, phone = "")
        store_8 = create_store_with_rir(company_id_1, phone = "")

        # run export sort by store_id desc, get first page of 3
        url_params = '?params={"pageSize":3,"pageIndex":0,"sortIndex":0,"sortDirection":-1}'
        export_results = self.main_access.call_get_preset("/export/preset/stores_duplicate_phone_numbers" + url_params, None, self.context)

        # verify the first page
        self.test_case.assertEqual(export_results, {
            'field_list': ["Store ID", "Company ID", "Company Name", "Phone Number", "Phone Stripped", "Store Format", "Store Number", "Note", "Street Number",
                           "Street Address", "Suite", "City", "State", "Zip Code", "Shopping Center", "Longitude", "Latitude", "Store Opened", "Store Closed", "# Dupes"],
            'field_meta': {
                "Store Opened": {"type": "date"},
                "Store Closed": {"type": "date"}
            },
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 5,
                'page_index': 0,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 0
            },
            'results': [
                [store_5, company_id_2, "UNITTEST_COMPANY", "444.535.123", "444535123", "UNIT_TEST_STORE_FORMAT", "UNIT_TEST_STORE_NUM", "IM A UNIT TEST", "123", "Main St", "", "UNIT_TEST_VILLE", "UT", "12345", "UNIT_TEST_MALL", -1, 1, None, None, 3],
                [store_4, company_id_1, "UNITTEST_COMPANY", "(444) 535-123", "444535123", "UNIT_TEST_STORE_FORMAT", "UNIT_TEST_STORE_NUM", "IM A UNIT TEST", "123", "Main St", "", "UNIT_TEST_VILLE", "UT", "12345", "UNIT_TEST_MALL", -1, 1, None, None, 3],
                [store_3, company_id_1, "UNITTEST_COMPANY", "444 535 123", "444535123", "UNIT_TEST_STORE_FORMAT", "UNIT_TEST_STORE_NUM", "IM A UNIT TEST", "123", "Main St", "", "UNIT_TEST_VILLE", "UT", "12345", "UNIT_TEST_MALL", -1, 1, None, None, 3]
            ]
        })

        # run export sort by store_id desc, get second page of 3
        url_params = '?params={"pageSize":3,"pageIndex":1,"sortIndex":0,"sortDirection":-1}'
        export_results = self.main_access.call_get_preset("/export/preset/stores_duplicate_phone_numbers" + url_params, None, self.context)

        # verify the second page
        self.test_case.assertEqual(export_results, {
            'field_list': ["Store ID", "Company ID", "Company Name", "Phone Number", "Phone Stripped", "Store Format", "Store Number", "Note", "Street Number",
                           "Street Address", "Suite", "City", "State", "Zip Code", "Shopping Center", "Longitude", "Latitude", "Store Opened", "Store Closed", "# Dupes"],
            'field_meta': {
                "Store Opened": {"type": "date"},
                "Store Closed": {"type": "date"}
            },
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 5,
                'page_index': 1,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 0
            },
            'results': [
                [store_2, company_id_2, "UNITTEST_COMPANY", "(123)-456-3333", "1234563333", "UNIT_TEST_STORE_FORMAT", "UNIT_TEST_STORE_NUM", "IM A UNIT TEST", "123", "Main St", "", "UNIT_TEST_VILLE", "UT", "12345", "UNIT_TEST_MALL", -1, 1, None, None, 2],
                [store_1, company_id_1, "UNITTEST_COMPANY", "123 456 3333", "1234563333", "UNIT_TEST_STORE_FORMAT", "UNIT_TEST_STORE_NUM", "IM A UNIT TEST", "123", "Main St", "", "UNIT_TEST_VILLE", "UT", "12345", "UNIT_TEST_MALL", -1, 1, None, None, 2]
            ]
        })


    def get_company_analytics_status(self):

        # create 3 test industries
        industry_id_1 = insert_test_industry("industry_1")
        industry_id_2 = insert_test_industry("industry_2")
        industry_id_3 = insert_test_industry("industry_3")

        # create three statuses for every company
        status_1 = self._create_analytics_status("status_1", datetime.datetime(2012, 1, 1), datetime.datetime(2012, 1, 2), "")
        status_2 = self._create_analytics_status("status_2", datetime.datetime(2012, 1, 1, 11, 20), datetime.datetime(2012, 1, 1, 11, 40, 30), "")
        status_3 = self._create_analytics_status("status_3", datetime.datetime(2012, 1, 1, 11, 20), None, "yo code sucks")

        # create 3 test companies.  Create different statuses per company
        company_id_1 = insert_test_company(name = "company_1", ctype = "retail_banner", analytics_status = status_1, workflow_status = "published")
        company_id_2 = insert_test_company(name = "company_2", ctype = "retail_banner", analytics_status = status_2, workflow_status = "woot")
        company_id_3 = insert_test_company(name = "company_3", ctype = "retail_parent", analytics_status = status_3, workflow_status = "chicken")

        # add a fourth company which is not a parent/banner and thus should filtered out
        insert_test_company(name = "company_4", ctype = "coop", analytics_status = status_3, workflow_status = "chicken")

        # associate 2 secondaries, and one primary industries to company 1
        self.main_access.mds.call_add_link("company", company_id_1, "secondary_industry_classification", "industry", industry_id_3, "secondary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id_1, "secondary_industry_classification", "industry", industry_id_2, "secondary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id_1, "primary_industry_classification", "industry", industry_id_1, "primary_industry", "industry_classification", self.context)

        # associate 2 secondaries industries to company 2
        self.main_access.mds.call_add_link("company", company_id_2, "secondary_industry_classification", "industry", industry_id_3, "secondary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id_2, "secondary_industry_classification", "industry", industry_id_2, "secondary_industry", "industry_classification", self.context)

        # no industries for company 3, sucka!

        # get first page sorted by company id desc
        params = {
            "sortIndex": 1,
            "sortDirection": -1,
            "pageIndex": 0,
            "pageSize": 2
        }
        response = self.main_access.call_get_preset(resource="/export/preset/company_analytics_status", params=params, context=self.context)

        # make sure results are good
        self.test_case.assertEqual(response, {
            "results": [
                [company_id_3, "company_3", "retail_parent", "", "chicken", "status_3", "2012-01-01T11:20:00", None, "N/A", "yo code sucks"],
                [company_id_2, "company_2", "retail_banner", "", "woot", "status_2", "2012-01-01T11:20:00", "2012-01-01T11:40:30", "20.5", ""]
            ],
            "meta": {
                'has_header': True,
                'has_metadata': True,
                'num_pages': 2,
                'num_rows': 3,
                'page_index': 0,
                'page_size': 2,
                'sort_direction': -1,
                'sort_index': 1,
                'row_format': 'list'
            },
            "field_list": ["ID", "Name", "Type", "Primary Industry", "Workflow Status", "Last Analytics Status", "Last Analytics Start", "Last Analytics End", "Analytics Duration (minutes)", "Exception"],
            "field_meta": {},
            "id_field": None,
            "id_index": None
        })

        # get second page sorted by company id desc
        params = {
            "sortIndex": 1,
            "sortDirection": -1,
            "pageIndex": 1,
            "pageSize": 2
        }
        response = self.main_access.call_get_preset(resource="/export/preset/company_analytics_status", params=params, context=self.context)

        # make sure results are good
        self.test_case.assertEqual(response, {
            "results": [
                [company_id_1, "company_1", "retail_banner", "industry_1", "published", "status_1", "2012-01-01T00:00:00", "2012-01-02T00:00:00", "1440.0", ""]
            ],
            "meta": {
                'has_header': True,
                'has_metadata': True,
                'num_pages': 2,
                'num_rows': 3,
                'page_index': 1,
                'page_size': 2,
                'sort_direction': -1,
                'sort_index': 1,
                'row_format': 'list'
            },
            "field_list": ["ID", "Name", "Type", "Primary Industry", "Workflow Status", "Last Analytics Status", "Last Analytics Start", "Last Analytics End", "Analytics Duration (minutes)", "Exception"],
            "field_meta": {},
            "id_field": None,
            "id_index": None
        })



    def get_geoprocessing_store_trade_area_checks(self):

        #create 2 companies, one is new and other is published (workflow statues)
        new_company_id = insert_test_company("NEW", "New Company", "retail_parent", "new")
        published_company_id = insert_test_company("PUB", "Published Company", "retail_parent", "published")
        test_address_id = insert_test_address(0, 90, "1225", "Santa Street", "North Pole", "AC", "53110")

        store_new_id_1 = insert_test_store(new_company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])
        store_published_id_1 = insert_test_store(published_company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])
        store_published_id_2 = insert_test_store(published_company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])
        store_published_id_3 = insert_test_store(published_company_id, [datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1)])

        #link trade area's to addresses because we want to test data export also which needs store addresses
        self.mds_access.call_add_link("store", store_new_id_1, "subject",
                "address", test_address_id, "location", "address_assignment", self.context)
        self.mds_access.call_add_link("store", store_published_id_1, "subject",
                "address", test_address_id, "location", "address_assignment", self.context)
        self.mds_access.call_add_link("store", store_published_id_2, "subject",
                 "address", test_address_id, "location", "address_assignment", self.context)
        self.mds_access.call_add_link("store", store_published_id_3, "subject",
                 "address", test_address_id, "location", "address_assignment", self.context)

        #assign good (with demographics) trade area to one store
        trade_area_id_1 = insert_test_trade_area(store_published_id_1, published_company_id, "Published Company")
        self.mds_access.call_add_link("store", store_published_id_1, "home_store",
                "trade_area", trade_area_id_1, "trade_area", "store_trade_area", self.context)

        #problem trade area (without demographics)
        problem_trade_area = self.mds_access.call_get_entity("trade_area", trade_area_id_1)
        problem_trade_area[u"data"][u"store_id"] = store_published_id_2
        problem_trade_area[u"data"][u"demographics"] = {}
        #insert problem trade area
        problem_trade_area_id = self.mds_access.call_add_entity("trade_area", "problem trade area",
                                                                problem_trade_area[u"data"], self.context)
        #link problem trade area with a store
        self.mds_access.call_add_link("store", store_published_id_2, "home_store",
                "trade_area", problem_trade_area_id, "trade_area", "store_trade_area", self.context)

        params = {"sortIndex": 0,
                  "sortDirection": 1,
                  "fieldFilters": None,
                  "pageIndex": 0,
                  "pageSize": 20}


        CHECK_MISSING_TRADE_AREA = 1
        CHECK_MISSING_THRESHOLD_DISTANCE_10_MILES = 2
        CHECK_MISSING_THRESHOLD_DISTANCE_10_MINUTES = 3
        CHECK_MISSING_DEMOGRAPHICS = 4

        response = self.main_access.call_get_preset(resource="/export/preset/geoprocessing_store_trade_area_checks/%d" % \
                    CHECK_MISSING_TRADE_AREA, params=params, context=self.context)

        self.test_case.assertIsNotNone(response)
        self.test_case.assertIsInstance(response, dict)
        self.test_case.assertIn("results", response)
        self.test_case.assertIsInstance(response["results"], list)

        #get list of returned store_ids
        response_store_ids = [row[0] for row in response["results"]]

        #store_new_id_1 is in new company, so should not be returned
        self.test_case.assertNotIn(store_new_id_1, response_store_ids)

        #store_published_id_1 has good trade area so should not be returned
        self.test_case.assertNotIn(store_published_id_1, response_store_ids)

        #store_published_id_2 has trade area without demographics, so should be returned
        #self.test_case.assertIn(store_published_id_2, response_store_ids)

        #store_published_id_3 has has no trade area link, so should be returned
        self.test_case.assertIn(store_published_id_3, response_store_ids)


        response = self.main_access.call_get_preset(resource="/export/preset/geoprocessing_store_trade_area_checks/%d" % \
                    CHECK_MISSING_THRESHOLD_DISTANCE_10_MILES, params=params, context=self.context)

        self.test_case.assertIsNotNone(response)
        self.test_case.assertIsInstance(response, dict)
        self.test_case.assertIn("results", response)
        self.test_case.assertIsInstance(response["results"], list)

        #get list of returned store_ids
        response_store_ids = [row[0] for row in response["results"]]

        #store_new_id_1 is in new company, so should not be returned
        self.test_case.assertNotIn(store_new_id_1, response_store_ids)

        #store_published_id_1 has good trade area so should not be returned
        self.test_case.assertNotIn(store_published_id_1, response_store_ids)

        #store_published_id_2 has trade area without demographics, so should be returned
        #self.test_case.assertIn(store_published_id_2, response_store_ids)

        #store_published_id_3 has has no trade area link, so should be returned
        self.test_case.assertIn(store_published_id_3, response_store_ids)

    def main_export_industry_competition(self):

        inds = [
            insert_test_industry(name="Industry %s" % i)
            for i in range(5)
        ]

        link_data = {
            "home_to_away": {
                "weight": 0.8
            },
            "away_to_home": {
                "weight": 0.4
            }
        }

        for i in range(len(inds)):
            self.mds_access.call_add_link("industry", inds[0], "competitor", "industry", inds[i], "competitor",
                                          "industry_competition", self.context, link_data=link_data,
                                          link_interval=[datetime.datetime(2011, 1, i+1), None])

            self.mds_access.call_add_link("industry", inds[0], "competitor", "industry", inds[i], "competitor",
                                          "industry_competition", self.context, link_data=link_data,
                                          link_interval=[None, datetime.datetime(2011, 1, i+1)])

        params = {
            "pageSize": 100
        }
        results = self.main_access.call_get_data_preset_industry_competition(params, self.context)

        # Add link endpoint is called 15 times, each creating 2 links, except linking industry to itself,
        # which creates 1 link, for a total of 18. The endpoint should show all duplicate links.
        self.test_case.assertEqual(len(results["results"]), 18)

    def main_export_industry_coverage(self):

        preset_url = "export/preset/industry_coverage"
        results = self.main_access.call_get_preset(preset_url, params=None, context=self.context)

        # to be continued...
        # pprint.pprint(results)



    # -------------------------------- Private Helpers -------------------------------- #

    def _create_valid_analytics(self, demographics, competition, stores, monopolies, economics, white_space):

        return {
            "v1_2": {
                "analytics": {
                    "demographics": demographics,
                    "competition": competition,
                    "stores": stores,
                    "monopolies": monopolies,
                    "economics": economics,
                    "white_space": white_space
                }
            }
        }


    def _create_analytics_status(self, status, start_time, end_time, exception):

        return {
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "exception": exception
        }

        #"data.workflow.analytics.status", "data.workflow.analytics.start_time", "data.workflow.analytics.end_time", "data.workflow.analytics.exception"