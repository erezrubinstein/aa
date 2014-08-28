import datetime
import mox
from common.business_logic.company_info import Competitor
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import parse_date
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import time_interval_helper
from geoprocessing.custom_analytics.custom_analytics_loader import CustomAnalyticsLoader
from geoprocessing.data_access import company_handler, address_handler, store_handler, company_competition_handler


__author__ = "erezrubinstein"

class TestCustomAnalyticsLoader(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsLoader, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)


    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsLoader, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_complete_run(self):

        # create mocks and helpers
        loader = CustomAnalyticsLoader("test_db", {})

        # stub some stuff
        self.mox.StubOutWithMock(loader, "_insert_companies")
        self.mox.StubOutWithMock(loader, "_get_stores_by_company")
        self.mox.StubOutWithMock(loader, "_insert_addresses")
        self.mox.StubOutWithMock(loader, "_get_time_period_dates")
        self.mox.StubOutWithMock(loader, "_insert_stores")
        self.mox.StubOutWithMock(loader, "_insert_competitive_companies")

        # begin recording
        loader._insert_companies().AndReturn("chicken_woot")
        loader._get_stores_by_company().AndReturn("chilly_willy")
        loader._insert_addresses("chilly_willy")
        loader._get_time_period_dates().AndReturn("dates_sucka")
        loader._insert_stores("chilly_willy", "chicken_woot", "dates_sucka")
        loader._insert_competitive_companies("chicken_woot")

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(loader.load(), "dates_sucka")


    def test_insert_companies(self):

        # create mocks and helpers
        mock_company_settings = {
            "chicken": {
                "company_name": "woot"
            },
            "chilly": {
                "company_name": "willy"
            }
        }
        loader = CustomAnalyticsLoader("test_db", mock_company_settings)

        # begin stubbing
        self.mox.StubOutWithMock(company_handler, "select_company_id_force_insert")

        # begin recording
        company_handler.select_company_id_force_insert("woot", "test_db").InAnyOrder().AndReturn("chicken_woot")
        company_handler.select_company_id_force_insert("willy", "test_db").InAnyOrder().AndReturn("chilly_willy")

        # replay all
        self.mox.ReplayAll()

        # go for gold
        results = loader._insert_companies()

        # verify results
        self.assertEqual(results, {
            "chicken": "chicken_woot",
            "chilly": "chilly_willy"
        })


    def test_get_stores_by_company(self):

        # create a complex mock settings with a bunch of different date set ups
        # NOTE: T4 will be the same date as T3.  That will make sure we're not double querying the same dates twice (i.e. treat as if it's null).
        mock_company_settings = {
            "chicken": {
                "time_periods": {
                    "t0": "2012-01-01T00:00:00",
                    "t1": "2013-01-01T00:00:00",
                    "t2": "2014-01-01T00:00:00",
                    "t3": "2014-03-01T00:00:00",
                    "t4": "2014-03-01T00:00:00"
                }
            },
            "woot": {
                "time_periods": {
                    "t0": None,
                    "t1": None,
                    "t2": "2014-01-01T00:00:00",
                    "t3": None,
                    "t4": None
                }
            },
            "chilly": {
                "time_periods": {
                    "t0": None,
                    "t1": "2013-01-01T00:00:00",
                    "t2": "2014-01-01T00:00:00",
                    "t3": "2014-03-01T00:00:00",
                    "t4": "2014-03-01T00:00:00"
                }
            },
            "willy": {
                "time_periods": {
                    "t0": None,
                    "t1": "2013-01-01T00:00:00",
                    "t2": "2014-01-01T00:00:00",
                    "t3": None,
                    "t4": None
                }
            }
        }
        loader = CustomAnalyticsLoader("test_db", mock_company_settings)

        # begin stubbing out things
        self.mox.StubOutWithMock(time_interval_helper, "active_as_of_analytics_date")
        self.mox.StubOutWithMock(time_interval_helper, "live_entity_filter")
        self.mox.StubOutWithMock(loader, "_query_stores")

        # begin recording
        # not that the order is weird, but consistent, since dictionary looping has a strange order...
        time_interval_helper.live_entity_filter([parse_date("2013-01-01T00:00:00"), parse_date("2014-01-01T00:00:00")], "interval", '$lte', '$gte').AndReturn("query_4")
        loader._query_stores({ "$or": "query_4", "data.company_id": "willy" }).AndReturn("willy")
        time_interval_helper.live_entity_filter([parse_date("2013-01-01T00:00:00"), parse_date("2014-03-01T00:00:00")], "interval", '$lte', '$gte').AndReturn("query_3")
        loader._query_stores({ "$or": "query_3", "data.company_id": "chilly" }).AndReturn("chilly")
        time_interval_helper.live_entity_filter([parse_date("2012-01-01T00:00:00"), parse_date("2014-03-01T00:00:00")], "interval", '$lte', '$gte').AndReturn("query_1")
        loader._query_stores({ "$or": "query_1", "data.company_id": "chicken" }).AndReturn("chicken")
        time_interval_helper.active_as_of_analytics_date(parse_date("2014-01-01T00:00:00")).AndReturn({ "query_2": True })
        loader._query_stores({ "query_2": True, "data.company_id": "woot" }).AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # show me the money!
        results = loader._get_stores_by_company()

        # make sure results are good
        self.assertEqual(results, {
            "chicken": "chicken",
            "woot": "woot",
            "chilly": "chilly",
            "willy": "willy"
        })


    def test_insert_addresses(self):

        # create mocks and helper
        mock_stores_by_company = {
            "company_1": [
                self._create_test_trade_area(1),
                self._create_test_trade_area(2)
            ],
            "company_2": [
                self._create_test_trade_area(3),
                self._create_test_trade_area(4)
            ],
            "company_3": [],
            "company_4": [
                self._create_test_trade_area(5)
            ]
        }
        mock_addresses = [
            self._create_test_address(1),
            self._create_test_address(2),
            self._create_test_address(3),
            self._create_test_address(4),
            self._create_test_address(5)
        ]

        # stub out some stuff
        self.mox.StubOutWithMock(address_handler, "batch_insert_addresses")

        # begin recording
        address_handler.batch_insert_addresses(mock_addresses, "yo_mama")

        # replay all
        self.mox.ReplayAll()

        # go!
        CustomAnalyticsLoader("yo_mama", {})._insert_addresses(mock_stores_by_company)


    def test_get_time_period_dates(self):

        # create mocks
        mock_company_settings = {
            "company_id": {
                "time_periods": {

                    # have a crazy order for the time periods, to test the sorting...
                    "t0": "woot",
                    "t2": "woot",
                    "t3": "woot",
                    "t1": "woot"
                }
            }
        }

        # call the method (no need to stub/record)
        date_mapping = CustomAnalyticsLoader("yo_mama", mock_company_settings)._get_time_period_dates()

        # verify
        self.assertEqual(date_mapping, {
            "t0": datetime.datetime(1900, 1, 1),
            "t1": datetime.datetime(1900, 2, 1),
            "t2": datetime.datetime(1900, 3, 1),
            "t3": datetime.datetime(1900, 4, 1)
        })


    def test_insert_stores(self):

        # create three companies with different date setups
        # NOTE: T4 will be the same date as T3.  That will make sure we're not double querying the same dates twice (i.e. treat as if it's null).
        mock_company_settings = {
            "company_1": {
                "time_periods": {
                    "t0": "2012-01-01T00:00:00",
                    "t1": "2013-01-01T00:00:00",
                    "t2": "2014-01-01T00:00:00",
                    "t3": "2014-01-01T00:00:00",
                }
            },
            "company_2": {
                "time_periods": {
                    "t0": None,
                    "t1": "2013-06-01T00:00:00",
                    "t2": None,
                    "t3": None
                }
            },
            "company_3": {
                "time_periods": {
                    "t0": None,
                    "t1": "2013-03-01T00:00:00",
                    "t2": "2014-03-01T00:00:00",
                    "t3": "2014-03-01T00:00:00"
                }
            }
        }

        # create a bunch of different date scenarios for the stores
        mock_stores_to_insert = {
            "company_1": [

                # three stores starting at the collection dates
                self._create_test_trade_area(1, "2012-01-01T00:00:00"),
                self._create_test_trade_area(2, "2013-01-01T00:00:00"),
                self._create_test_trade_area(3, "2014-01-01T00:00:00"),

                # a store starting and closing between the same collection dates
                self._create_test_trade_area(4, "2012-05-01T00:00:00", "2012-06-01T00:00:00"),

                # a store starting before the collection and ending after
                self._create_test_trade_area(5, "2011-01-01T00:00:00", "2014-03-01T00:00:00"),

                # a store starting between t0 and t1 and closing between t1 and t2
                self._create_test_trade_area(6, "2012-05-01T00:00:00", "2013-05-01T00:00:00")
            ],
            "company_2": [

                # two stores created before the time period.  One stays open, one closes
                self._create_test_trade_area(7, "2012-01-01T00:00:00"),
                self._create_test_trade_area(8, "2012-01-01T00:00:00", "2014-01-01T00:00:00"),

                # one store created exactly on the date
                self._create_test_trade_area(9, "2013-06-01T00:00:00")
            ],
            "company_3": [

                # created and closed in between the dates
                self._create_test_trade_area(10, "2013-04-01T00:00:00", "2014-01-01T00:00:00"),

                # created between and closed after
                self._create_test_trade_area(11, "2013-04-01T00:00:00", "2014-03-09T00:00:00"),

                # created before, never closed
                self._create_test_trade_area(12, "2010-01-01T00:00:00"),

                # created after (this should not make it in, but if it does, let's just make sure it doesn't qualify)
                self._create_test_trade_area(13, "2014-03-09T00:00:00"),

                # all dates are null...
                self._create_test_trade_area(14)
            ]
        }

        # mock core id to sql id mappings
        mock_core_to_sql_id_mappings = {
            "company_1": 1,
            "company_2": 2,
            "company_3": 3
        }

        # create time period date mappings
        mock_time_period_dates = {
            "t0": datetime.datetime(1900, 01, 01),
            "t1": datetime.datetime(1900, 02, 01),
            "t2": datetime.datetime(1900, 03, 01),
            "t3": datetime.datetime(1900, 04, 01)
        }

        # create the mock formatted stores
        # I'm ordering it the way that the dict.values() spits out the company_ids, which is weird but consistent.
        mock_formatted_stores = [

            # company 1 (store 4 doesn't qualify)
            self._create_test_formatted_store(1, 1, datetime.datetime(1900, 01, 01)),
            self._create_test_formatted_store(1, 2, datetime.datetime(1900, 02, 01)),
            self._create_test_formatted_store(1, 3, datetime.datetime(1900, 03, 01)),
            self._create_test_formatted_store(1, 5, datetime.datetime(1900, 01, 01)),
            self._create_test_formatted_store(1, 6, datetime.datetime(1900, 02, 01), datetime.datetime(1900, 03, 01)),

            # company 3 (store 10, 13 don't qualify)
            self._create_test_formatted_store(3, 11, datetime.datetime(1900, 03, 01)),
            self._create_test_formatted_store(3, 12, datetime.datetime(1900, 02, 01)),
            self._create_test_formatted_store(3, 14, datetime.datetime(1900, 02, 01)),

            # company 2
            self._create_test_formatted_store(2, 7, datetime.datetime(1900, 02, 01)),
            self._create_test_formatted_store(2, 8, datetime.datetime(1900, 02, 01)),
            self._create_test_formatted_store(2, 9, datetime.datetime(1900, 02, 01)),
        ]

        # stub out stuff
        self.mox.StubOutWithMock(store_handler, "batch_insert_stores__auto_get_addresses")

        # begin recording
        store_handler.batch_insert_stores__auto_get_addresses(mock_formatted_stores, "test_db")

        # replay all
        self.mox.ReplayAll()

        # show me the monay (misspelled on purpose)
        CustomAnalyticsLoader("test_db", mock_company_settings)._insert_stores(mock_stores_to_insert, mock_core_to_sql_id_mappings, mock_time_period_dates)




    def test_insert_stores__opens_closes_same_time_period__RET_3476(self):
        """
        This tests the bug from ret 3476, where a store can be inputed to SQL as opened and closed at the same date.
        """

        # create three companies with different date setups
        # NOTE: T4 will be the same date as T3.  That will make sure we're not double querying the same dates twice (i.e. treat as if it's null).
        mock_company_settings = {
            "company_1": {
                "time_periods": {
                    "t0": "2012-01-01T00:00:00",
                    "t1": "2013-01-01T00:00:00"
                }
            }
        }

        # create a bunch of different date scenarios for the stores
        mock_stores_to_insert = {
            "company_1": [

                # this store should not be counted since it closes at t0
                self._create_test_trade_area(1, None, "2012-01-01T00:00:00"),

                # this store should be counted
                self._create_test_trade_area(2, "2013-01-01T00:00:00")
            ]
        }

        # mock core id to sql id mappings
        mock_core_to_sql_id_mappings = {
            "company_1": 1
        }

        # create time period date mappings
        mock_time_period_dates = {
            "t0": datetime.datetime(1900, 01, 01),
            "t1": datetime.datetime(1900, 02, 01)
        }

        # only have one store
        mock_formatted_stores = [
            self._create_test_formatted_store(1, 2, datetime.datetime(1900, 02, 01))
        ]

        # stub out stuff
        self.mox.StubOutWithMock(store_handler, "batch_insert_stores__auto_get_addresses")

        # begin recording
        store_handler.batch_insert_stores__auto_get_addresses(mock_formatted_stores, "test_db")

        # replay all
        self.mox.ReplayAll()

        # show me the monay (misspelled on purpose)
        CustomAnalyticsLoader("test_db", mock_company_settings)._insert_stores(mock_stores_to_insert, mock_core_to_sql_id_mappings, mock_time_period_dates)


    def test_insert_competitive_companies(self):

        # create mock settings
        mock_company_settings = {
            "company_1": {
                "weight": 0.5
            },
            "company_2": {
                "weight": 1.0
            },
            "company_3": {
                "weight": 2.7
            }
        }
        mock_core_id_to_sql_ids = {
            "company_1": 1,
            "company_2": 2,
            "company_3": 3
        }

        # create mocked results
        mock_competitor_objects = [

            # this is a strange order, but it's the order of the map function, and it's consistent
            Competitor.simple_init(1, 1, .5, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(1, 3, 2.7, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(1, 2, 1, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(3, 1, .5, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(3, 3, 2.7, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(3, 2, 1, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(2, 1, .5, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(2, 3, 2.7, datetime.datetime(1900, 1, 1), None),
            Competitor.simple_init(2, 2, 1, datetime.datetime(1900, 1, 1), None)
        ]

        # stub out some stuff
        self.mox.StubOutWithMock(company_competition_handler, "insert_company_competition")

        # begin recording
        company_competition_handler.insert_company_competition(mock_competitor_objects, "test_db")

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsLoader("test_db", mock_company_settings)._insert_competitive_companies(mock_core_id_to_sql_ids)



    # ---------------------------- Private Helpers ---------------------------- #

    def _create_test_trade_area(self, store_id, opened_date = None, closed_date = None):

        return {
            "_id": store_id,
            "data": {
                "store_id": store_id,
                "street_number": str(store_id),
                "street": str(store_id),
                "city": str(store_id),
                "state": str(store_id),
                "zip": str(store_id),
                "suite": str(store_id),
                "latitude": str(store_id),
                "longitude": str(store_id),
                "shopping_center": str(store_id),
                "phone": str(store_id),
                "store_opened_date": opened_date,
                "store_closed_date": closed_date
            }
        }

    def _create_test_formatted_store(self, company_sql_id, store_id, opened_date = None, closed_date = None):
        return {
            "company_id": company_sql_id,
            "core_store_id": store_id,
            "trade_area_id": store_id,
            "phone_number": str(store_id),
            "opened_date": opened_date,
            "closed_date": closed_date,
            "assumed_opened_date": opened_date,
            "assumed_closed_date": closed_date
        }


    def _create_test_address(self, store_id):

        return {
            "street_number": str(store_id),
            "street": str(store_id),
            "city": str(store_id),
            "state": str(store_id),
            "zip": str(store_id),
            "suite": str(store_id),
            "latitude": str(store_id),
            "longitude": str(store_id),
            "shopping_center_name": str(store_id),
            "unique_store_identifier":store_id
        }