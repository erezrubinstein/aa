from __future__ import division
from common.utilities.date_utilities import ANALYTICS_TARGET_YEAR
from common.utilities.inversion_of_control import Dependency
from common.utilities.time_series import get_monthly_time_series
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area, insert_test_store, \
    insert_test_company
import datetime
import time
import random


__author__ = 'vgold'


class MainAnalyticsExportTestCollection(ServiceTestCollection):

    def initialize(self):

        random.seed(1)

        self.main_param = Dependency("CoreAPIParamsBuilder").value

        self.user_id = 'test@nexusri.com'
        self.source = "main_analytics_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        self.letters = [chr(c) for c in range(ord("a"), ord("z") + 1)]

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def main_analytics_export_test_trade_area_to_trade_area(self):

        # insert a bunch of somewhat realistic data
        companies = []
        stores = []
        trade_areas = []

        num_companies = 10
        num_stores_per_company = 3
        num_trade_areas_per_store = 2

        for c in range(num_companies):

            company_id = insert_test_company(name="Company %s" % c)
            companies.append(company_id)

            for s in range(num_stores_per_company):

                store_id = insert_test_store(company_id, [datetime.datetime(2010, 1, 1), None])
                stores.append(store_id)

                random_street = self.__get_random_street_name()

                for t in range(num_trade_areas_per_store):

                    series_1 = self.__get_random_series()
                    series_2 = self.__get_random_series()

                    analytics = {
                        "demographics": {
                            "monthly": {
                                "TOTPOP_CY": [
                                    {
                                        "target_year": ANALYTICS_TARGET_YEAR,
                                        "series": series_1
                                    },
                                    {
                                        "target_year": 2016,
                                        "series": series_2
                                    }
                                ]
                            }
                        }
                    }

                    trade_area_id = insert_test_trade_area(store_id, company_id, street=random_street, analytics=analytics)
                    trade_areas.append(trade_area_id)

        # make sure everything's in there
        self.test_case.assertEqual(len(companies), num_companies)
        self.test_case.assertEqual(len(stores), num_companies * num_stores_per_company)
        self.test_case.assertEqual(len(trade_areas), num_companies * num_stores_per_company * num_trade_areas_per_store)

        # search all, sort by street name

        num_stores = len(stores)
        num_trade_areas = len(trade_areas)

        params = {
            "sortIndex": 6,
            "sortDirection": 1,
            "fieldFilters": None,
            "pageIndex": 0,
            "pageSize": 20
        }

        preset_url = "export/preset/analytics/trade_area_to_trade_area"

        t0 = time.time()

        results = self.main_access.call_get_preset(preset_url, params, self.context)

        t1 = time.time()

        #print "\n\n\n"
        #print "Got {} results for {} companies, {} stores, {} trade areas " \
        #    "in {} seconds.".format(len(results), num_companies, num_stores, num_trade_areas, t1 - t0)
        #print "\n\n\n"

        # Unwound 200 trade areas in 0.0790259838104 seconds.


        # search for single company and unwind data

        filter_company_id = random.choice(companies)

        params = {
            "sortIndex": 6,
            "sortDirection": 1,
            "fieldFilters": {"data.company_id": filter_company_id},
            "pageIndex": 0,
            "pageSize": 20
        }

        preset_url = "export/preset/analytics/trade_area_to_trade_area"
        self.main_access.call_get_preset(preset_url, params, self.context)


    def __get_random_street_name(self, words=4):

        random_street = []

        for i in range(words):
            n_letters = 4
            random_street.append("".join([random.choice(self.letters) for i in range(n_letters)]))

        return " ".join(random_street)

    def __get_random_series(self):

        months = get_monthly_time_series()
        return [{"date": m.date(), "value": random.randrange(100)} for m in months]


    def main_analytics_export_test_trade_area_monthly_demographics(self):

        companies = [
            insert_test_company(name="Company 0"),
            insert_test_company(name="Company 1"),
            insert_test_company(name="Company 2"),
            insert_test_company(name="Company 3")
        ]

        stores = [
            insert_test_store(co_id, [datetime.datetime(2010, 1, 1), None])
            for co_id in companies
        ]

        num_trade_areas = 100

        for _ in range(num_trade_areas):
            insert_test_trade_area(stores[0], companies[0],
                                   analytics=self.__get_sample_analytics_dict(companies, stores))

        params = {
            "sortIndex": 0,
            "sortDirection": 1,
            "fieldFilters": None,
            "pageIndex": 0,
            "pageSize": 20
        }

        preset_url = "export/preset/analytics/%s/trade_area/monthly_total_population" % companies[0]

        self.main_access.call_get_preset(preset_url, params, self.context)


    def main_analytics_export_test_trade_area_competition(self):

        # create mock competitive stores for both trade_areas
        competitive_stores_1 = [
            {
				"end_date" : "3000-01-01T00:00:00",
				"start_date" : "1900-01-01T00:00:00",
				"away_company_id" : 11,
				"weight" : 1,
				"away_store_id" : 1
			},
			{
				"end_date" : "3000-01-01T00:00:00",
				"start_date" : "2012-01-01T00:00:00",
				"away_company_id" : 22,
				"weight" : 1,
				"away_store_id" : 2
			}
        ]
        competitive_stores_2 = [
            {
				"end_date" : "3000-01-01T00:00:00",
				"start_date" : "1900-01-01T00:00:00",
				"away_company_id" : 33,
				"weight" : 1,
				"away_store_id" : 3
			},
			{
				"end_date" : "2013-01-01T00:00:00",
				"start_date" : "1900-01-01T00:00:00",
				"away_company_id" : 44,
				"weight" : .5,
				"away_store_id" : 4
			}
        ]
        competitive_stores_3 = [
            {
				"end_date" : "3000-01-01T00:00:00",
				"start_date" : "1900-01-01T00:00:00",
				"away_company_id" : 55,
				"weight" : 1,
				"away_store_id" : 5
			},
			{
				"end_date" : "2013-01-01T00:00:00",
				"start_date" : "1900-01-01T00:00:00",
				"away_company_id" : 66,
				"weight" : .5,
				"away_store_id" : 6
			}
        ]

        # insert three trade areas, each one having multiple competitions.
        trade_area_id_1 = insert_test_trade_area(1, "1", "test company 1", competitive_stores = competitive_stores_1)
        trade_area_id_2 = insert_test_trade_area(2, "1", "test company 1", competitive_stores = competitive_stores_2)
        trade_area_id_3 = insert_test_trade_area(3, "2", "test company 2", competitive_stores = competitive_stores_3)

        # export the page 1
        preset_url = "export/preset/analytics/1/trade_area/competition"
        params = { "sortIndex": 14, "sortDirection": -1, "fieldFilters": None, "pageIndex": 0, "pageSize": 3 }
        export_results = self.main_access.call_get_preset(preset_url, params, self.context)


        self.test_case.maxDiff = None



        # verify the results
        self.test_case.assertEqual(export_results, {
            'field_list': ['ID', 'Company ID', 'Store ID', 'Company Name', 'Street Number', 'Street', 'City', 'State',
                           'Zip', 'Phone Number', 'Trade Area Threshold', 'Start Date', 'End Date', 'Weight',
                           'Away Store ID', 'Away Company ID', "Away Company Name", "Away Street Number", "Away Street",
                           "Away City", "Away State", "Away Zip", "Away Longitude", "Away Latitude"],
            'field_meta': { 'End Date': 'date', 'Start Date': 'date', 'Weight': 'number',"Away Longitude": "number","Away Latitude": "number"},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 3,
                'page_index': 0,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 14
            },
            'results': [
                [trade_area_id_2, "1", 2, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "2013-01-01T00:00:00", .5, 4, 44, None, None, None, None, None, None, None, None],
                [trade_area_id_2, "1", 2, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "3000-01-01T00:00:00", 1, 3, 33, None, None, None, None, None, None, None, None],
                [trade_area_id_1, "1", 1, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "2012-01-01T00:00:00", "3000-01-01T00:00:00", 1, 2, 22, None, None, None, None, None, None, None, None]
            ]
        })

        # export the page 2
        preset_url = "export/preset/analytics/1/trade_area/competition"
        params = { "sortIndex": 14, "sortDirection": -1, "fieldFilters": None, "pageIndex": 1, "pageSize": 3 }
        export_results = self.main_access.call_get_preset(preset_url, params, self.context)

        # verify results
        self.test_case.assertEqual(export_results, {
            'field_list': ['ID', 'Company ID', 'Store ID', 'Company Name', 'Street Number', 'Street', 'City', 'State',
                           'Zip', 'Phone Number', 'Trade Area Threshold', 'Start Date', 'End Date', 'Weight',
                           'Away Store ID', 'Away Company ID', "Away Company Name", "Away Street Number", "Away Street",
                           "Away City", "Away State", "Away Zip", "Away Longitude", "Away Latitude"],
            'field_meta': { 'End Date': 'date', 'Start Date': 'date', 'Weight': 'number',"Away Longitude": "number","Away Latitude": "number"},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 1,
                'page_index': 1,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 14
            },
            'results': [
                [trade_area_id_1, "1", 1, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "3000-01-01T00:00:00", 1, 1, 11, None, None, None, None, None, None, None, None]
            ]
        })


    def main_analytics_export_test_trade_area_monopolies(self):

        # create mock competitive stores for both trade_areas
        monopolies_1 = [
            {
                "end_date" : "3000-01-01T00:00:00",
                "start_date" : "1900-01-01T00:00:00",
                "monopoly_type" : "Type1"
            },
            {
                "end_date" : "3000-01-01T00:00:00",
                "start_date" : "2012-01-01T00:00:00",
                "monopoly_type" : "Type2"
            }
        ]
        monopolies_2 = [
            {
                "end_date" : "3000-01-01T00:00:00",
                "start_date" : "1900-01-01T00:00:00",
                "monopoly_type" : "Type3"
            },
            {
                "end_date" : "2013-01-01T00:00:00",
                "start_date" : "1900-01-01T00:00:00",
                "monopoly_type" : "Type4"
            }
        ]
        monopolies_3 = [
            {
                "end_date" : "3000-01-01T00:00:00",
                "start_date" : "1900-01-01T00:00:00",
                "monopoly_type" : "Type5"
            },
            {
                "end_date" : "2013-01-01T00:00:00",
                "start_date" : "1900-01-01T00:00:00",
                "monopoly_type" : "Type6"
            }
        ]

        # insert two trade areas, each one having multiple competitions
        trade_area_id_1 = insert_test_trade_area(1, "1", "test company 1", monopolies = monopolies_1)
        trade_area_id_2 = insert_test_trade_area(2, "1", "test company 1", monopolies = monopolies_2)
        trade_area_id_3 = insert_test_trade_area(3, "2", "test company 2", monopolies = monopolies_3)

        # export page 1
        preset_url = "export/preset/analytics/1/trade_area/monopolies"
        params = { "sortIndex": 13, "sortDirection": -1, "fieldFilters": None, "pageIndex": 0, "pageSize": 3 }
        export_results = self.main_access.call_get_preset(preset_url, params, self.context)

        # verify the results
        self.test_case.assertEqual(export_results, {
            'field_list': ['ID', 'Company ID', 'Store ID', 'Company Name', 'Street Number', 'Street', 'City', 'State', 'Zip', 'Phone Number', 'Trade Area Threshold',
                           'Start Date', 'End Date', 'Monopoly Type'],
            'field_meta': { 'End Date': 'date', 'Start Date': 'date', 'Weight': 'number'},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 3,
                'page_index': 0,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 13
            },
            'results': [
                [trade_area_id_2, "1", 2, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "2013-01-01T00:00:00", "Type4"],
                [trade_area_id_2, "1", 2, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "3000-01-01T00:00:00", "Type3"],
                [trade_area_id_1, "1", 1, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "2012-01-01T00:00:00", "3000-01-01T00:00:00", "Type2"]
            ]
        })

        # export page 2
        preset_url = "export/preset/analytics/1/trade_area/monopolies"
        params = { "sortIndex": 13, "sortDirection": -1, "fieldFilters": None, "pageIndex": 1, "pageSize": 3 }
        export_results = self.main_access.call_get_preset(preset_url, params, self.context)

        # verify results
        self.test_case.assertEqual(export_results, {
            'field_list': ['ID', 'Company ID', 'Store ID', 'Company Name', 'Street Number', 'Street', 'City', 'State', 'Zip', 'Phone Number', 'Trade Area Threshold',
                           'Start Date', 'End Date', 'Monopoly Type'],
            'field_meta': { 'End Date': 'date', 'Start Date': 'date', 'Weight': 'number'},
            'id_field': None,
            'id_index': None,
            'meta': {
                'num_rows': 1,
                'page_index': 1,
                'page_size': 3,
                'sort_direction': -1,
                'sort_index': 13
            },
            'results': [
                [trade_area_id_1, "1", 1, "test company 1", "street_number", "street", "city", "state", "zip", 111, "DistanceMiles10", "1900-01-01T00:00:00", "3000-01-01T00:00:00", "Type1"]
            ]
        })




    #------------------# Private Helpers #------------------#

    def __get_sample_analytics_dict(self, companies, stores):

        return {
            "demographics": {
                "monthly": {
                    "TOTPOP_CY": [
                        {
                            "target_year": ANALYTICS_TARGET_YEAR,
                            "series": [
                                {
                                    "date": datetime.datetime(2010, 2, 1),
                                    "value": 15
                                },
                                {
                                    "date": datetime.datetime(2010, 1, 1),
                                    "value": 10
                                }
                            ]
                        },
                        {
                            "target_year": 2016,
                            "series": [
                                {
                                    "date": datetime.datetime(2010, 2, 1),
                                    "value": 15
                                },
                                {
                                    "date": datetime.datetime(2010, 1, 1),
                                    "value": 10
                                }
                            ]
                        }
                    ]
                }
            },
            "competition": {
                "monthly": {
                    "competitive_stores": [
                        {
                            "date": datetime.datetime(2010, 2, 1),
                            "value": [
                                {
                                    "company_id": companies[1],
                                    "store_id": stores[1],
                                    "weight": 0.8
                                },
                                {
                                    "company_id": companies[2],
                                    "store_id": stores[2],
                                    "weight": 0.3
                                },
                                {
                                    "company_id": companies[3],
                                    "store_id": stores[3],
                                    "weight": 1.0
                                },
                                {
                                    "company_id": companies[0],
                                    "store_id": stores[0],
                                    "weight": 1.0
                                }
                            ]
                        },
                        {
                            "date": datetime.datetime(2010, 1, 1),
                            "value": [
                                {
                                    "company_id": companies[1],
                                    "store_id": stores[1],
                                    "weight": 0.8
                                },
                                {
                                    "company_id": companies[2],
                                    "store_id": stores[2],
                                    "weight": 0.3
                                }
                            ]
                        }
                    ],
                    "away_store_count": {
                        "raw": [
                            {
                                "date": datetime.datetime(2010, 2, 1),
                                "value": 4
                            },
                            {
                                "date": datetime.datetime(2010, 1, 1),
                                "value": 2
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2010, 2, 1),
                                "value": 3.1
                            },
                            {
                                "date": datetime.datetime(2010, 1, 1),
                                "value": 1.1
                            }
                        ]
                    }
                }
            },
            "competition_adjusted_demographics": {
                "monthly": {
                    "TOTPOP_CY": [
                        {
                            "target_year": ANALYTICS_TARGET_YEAR,
                            "series": [
                                {
                                    "date": datetime.datetime(2010, 2, 1),
                                    "value": 15
                                },
                                {
                                    "date": datetime.datetime(2010, 1, 1),
                                    "value": 10
                                }
                            ]
                        },
                        {
                            "target_year": 2016,
                            "series": [
                                {
                                    "date": datetime.datetime(2010, 2, 1),
                                    "value": 15
                                },
                                {
                                    "date": datetime.datetime(2010, 1, 1),
                                    "value": 10
                                }
                            ]
                        }
                    ]
                }
            }
        }
