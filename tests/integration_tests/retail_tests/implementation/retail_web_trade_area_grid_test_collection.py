from __future__ import division
import pprint
from tests.integration_tests.utilities.entity_hierarchy_test_helper import link_company_to_company
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store, insert_test_trade_area, insert_test_company_analytics
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.helpers.retail_store_grid_helper import RetailStoreGridHelper
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, get_datetime_months_ago, ANALYTICS_TARGET_YEAR, get_start_date_of_previous_month
from common.utilities.time_series import get_start_of_same_month, get_monthly_time_series
from requests.cookies import RequestsCookieJar
import datetime
import json


class RetailWebTradeAreaGridTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ Tests --------------------------------------##

    def retail_test_trade_area_grids(self):
        self.test_case.maxDiff = None

        per_capita_income = 1234
        dem_total_households = 2345
        dem_total_population = 3456
        aggregate_income = 4567
        pop_per_comp_store = 5678
        agg_inc_per_comp_store = 6789
        hh_per_comp_store = 7890

        format_date = lambda x: get_start_of_same_month(x).isoformat().rsplit(".", 1)[0]
        format_date_short = lambda x: get_start_of_same_month(x).isoformat().rsplit("T", 1)[0]
        time_series = get_monthly_time_series(end=LAST_ANALYTICS_DATE)

        cid1 = insert_test_company(name="Company 1", type="retail_banner")

        sids1 = [
            insert_test_store(cid1, [None, None]),
            insert_test_store(cid1, [None, datetime.datetime(2012, 1, 1)]),
            insert_test_store(cid1, [datetime.datetime(2012, 2, 1), None]),
            insert_test_store(cid1, [LAST_ANALYTICS_DATE, None])
        ]

        ta1_analytics = {
            "competition_adjusted_demographics": {
                "monthly": {
                    "TOTPOP_CY": [
                        {
                            "target_year": ANALYTICS_TARGET_YEAR,
                            "series": [
                                {
                                    "date": format_date(month),
                                    "value": pop_per_comp_store - i
                                }
                                for i, month in enumerate(time_series)
                            ]
                        }
                    ],
                    "TOTHH_CY": [
                        {
                            "target_year": ANALYTICS_TARGET_YEAR,
                            "series": [
                                {
                                    "date": format_date(month),
                                    "value": hh_per_comp_store - i
                                }
                                for i, month in enumerate(time_series)
                            ]
                        }
                    ],
                    "AGG_INCOME_CY": [
                        {
                            "target_year": ANALYTICS_TARGET_YEAR,
                            "series": [
                                {
                                    "date": format_date(month),
                                    "value": agg_inc_per_comp_store - i
                                }
                                for i, month in enumerate(time_series)
                            ]
                        }
                    ]
                }
            }
        }

        taids1 = [
            insert_test_trade_area(sids1[0], cid1, "Company 1", per_capita_income=per_capita_income,
                                   dem_total_households=dem_total_households, dem_total_population=dem_total_population,
                                   aggregate_income=aggregate_income, analytics=ta1_analytics),
            insert_test_trade_area(sids1[1], cid1, "Company 1", closed_date=datetime.datetime(2012, 1, 1)),
            insert_test_trade_area(sids1[2], cid1, "Company 1", opened_date=datetime.datetime(2012, 2, 1)),
            insert_test_trade_area(sids1[3], cid1, "Company 1", opened_date=LAST_ANALYTICS_DATE)
        ]

        cid2 = insert_test_company(name="Company 2", type="retail_banner")

        sids2 = [
            insert_test_store(cid2, [None, None]),
            insert_test_store(cid2, [None, datetime.datetime(2012, 1, 1)]),
            insert_test_store(cid2, [datetime.datetime(2012, 2, 1), None])
        ]

        taids2 = [
            insert_test_trade_area(sids2[0], cid2, "Company 2"),
            insert_test_trade_area(sids2[1], cid2, "Company 2", closed_date=datetime.datetime(2013, 1, 1)),
            insert_test_trade_area(sids2[2], cid2, "Company 2", opened_date=datetime.datetime(2013, 2, 1))
        ]

        pid = insert_test_company(name="Parent", type="retail_parent")

        link_company_to_company(self, pid, cid1, rel_type="retailer_branding")
        link_company_to_company(self, pid, cid2, rel_type="retailer_branding")

        # Test all stores grid with latest date
        params = {
            "company_ids": [cid1],
            "company_name": "Company 1",
            "grid_id": "stores",
            "show_competition": True,
            "date_filter": format_date_short(LAST_ANALYTICS_DATE),
            "all_stores_date_state": "first_date",
            "analytics_date_filter": format_date_short(LAST_ANALYTICS_DATE),
            "last_store_date": format_date_short(LAST_ANALYTICS_DATE)
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        self.test_case.assertEqual(len(results["results"]), 3)
        self.test_case.assertItemsEqual([taids1[0], taids1[2], taids1[3]], [r[-1] for r in results["results"]])

        for result in results["results"]:
            if result[-1] == taids1[0]:
                self.test_case.assertListEqual(
                    result[:10],
                    [
                        "Company 1",
                        "state",
                        "city",
                        per_capita_income,
                        dem_total_households,
                        dem_total_population,
                        aggregate_income,
                        hh_per_comp_store,
                        pop_per_comp_store,
                        agg_inc_per_comp_store
                    ]
                )

        # Test all stores grid with older date
        params = {
            "company_ids": [cid1],
            "company_name": "Company 1",
            "grid_id": "stores",
            "show_competition": True,
            "date_filter": format_date_short(get_datetime_months_ago(5, start=LAST_ANALYTICS_DATE)),
            "all_stores_date_state": "first_date",
            "analytics_date_filter": format_date_short(LAST_ANALYTICS_DATE),
            "last_store_date": format_date_short(LAST_ANALYTICS_DATE)
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        self.test_case.assertEqual(len(results["results"]), 2)
        self.test_case.assertItemsEqual([taids1[0], taids1[2]], [r[-1] for r in results["results"]])

        for result in results["results"]:
            if result[-1] == taids1[0]:
                self.test_case.assertListEqual(
                    result[:10],
                    [
                        "Company 1",
                        "state",
                        "city",
                        per_capita_income,
                        dem_total_households,
                        dem_total_population,
                        aggregate_income,
                        hh_per_comp_store - 5,
                        pop_per_comp_store - 5,
                        agg_inc_per_comp_store - 5
                    ]
                )

        # Test all stores grid without first_date logic
        params = {
            "company_ids": [cid1],
            "company_name": "Company 1",
            "grid_id": "stores",
            "show_competition": True,
            "date_filter": format_date_short(LAST_ANALYTICS_DATE),
            "all_stores_date_state": "",
            "analytics_date_filter": format_date_short(LAST_ANALYTICS_DATE),
            "last_store_date": format_date_short(LAST_ANALYTICS_DATE)
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        self.test_case.assertEqual(len(results["results"]), 3)
        self.test_case.assertItemsEqual([taids1[0], taids1[2], taids1[3]], [r[-1] for r in results["results"]])

        for result in results["results"]:
            if result[-1] == taids1[0]:
                self.test_case.assertListEqual(
                    result[:10],
                    [
                        "Company 1",
                        "state",
                        "city",
                        per_capita_income,
                        dem_total_households,
                        dem_total_population,
                        aggregate_income,
                        hh_per_comp_store,
                        pop_per_comp_store,
                        agg_inc_per_comp_store
                    ]
                )

        # Test store openings grid
        params = {
            "company_ids": [cid1],
            "company_name": "Company 1",
            "grid_id": "opening_stores",
            "show_competition": True,
            "date_filter": ["2012-01-01", "2012-09-09"],
            "all_stores_date_state": "first_date"
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        self.test_case.assertEqual(len(results["results"]), 1)
        self.test_case.assertItemsEqual(taids1[2], results["results"][0][-1])

        # Test store closings grid
        params = {
            "company_ids": [cid1],
            "company_name": "Company 1",
            "grid_id": "closing_stores",
            "show_competition": True,
            "date_filter": ["2012-01-01", "2012-09-09"],
            "all_stores_date_state": "first_date"
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        self.test_case.assertEqual(len(results["results"]), 1)
        self.test_case.assertItemsEqual(taids1[1], results["results"][0][-1])

        ################################################

        month_before_analytics_end = get_start_date_of_previous_month(LAST_ANALYTICS_DATE).isoformat()
        c1_analytics = self.__make_analytics_dict(month_before_analytics_end, 12)
        c2_analytics = self.__make_analytics_dict(month_before_analytics_end, 20)
        p_analytics = self.__make_analytics_dict(month_before_analytics_end, 16)

        self.mds_access.call_update_entity("company", cid1, self.context, field_name="data.analytics",
                                           field_value=c1_analytics)
        self.mds_access.call_update_entity("company", cid2, self.context, field_name="data.analytics",
                                           field_value=c2_analytics)
        self.mds_access.call_update_entity("company", pid, self.context, field_name="data.analytics",
                                           field_value=p_analytics)

        can_data = self.__make_can_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        can_data_comp = self.__make_can_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "competition_adjusted_demographics")

        insert_test_company_analytics(cid1, datetime.datetime(2013, 1, 1), analytics=can_data)
        insert_test_company_analytics(cid1, datetime.datetime(2013, 1, 1), analytics=can_data_comp,
                                      engine="competition_adjusted_demographics")

        can_data = self.__make_can_data([11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        can_data_comp = self.__make_can_data([11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "competition_adjusted_demographics")
        insert_test_company_analytics(cid2, datetime.datetime(2013, 1, 1), analytics=can_data)
        insert_test_company_analytics(cid2, datetime.datetime(2013, 1, 1), analytics=can_data_comp,
                                      engine="competition_adjusted_demographics")

        can_data = self.__make_can_data([6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        can_data_comp = self.__make_can_data([6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "competition_adjusted_demographics")
        insert_test_company_analytics(pid, datetime.datetime(2013, 1, 1), analytics=can_data)
        insert_test_company_analytics(pid, datetime.datetime(2013, 1, 1), analytics=can_data_comp,
                                      engine="competition_adjusted_demographics")

        # Test summary grids
        params = {
            "banner_ids": [cid1, cid2],
            "parent_id": pid,
            "company_name": "Parent",
            "stat_type": "avg",
            "grid_id": "summary",
            "show_competition": True,
            "date_filter": ["2013-01-01", format_date_short(LAST_ANALYTICS_DATE)],
            "all_stores_date_state": "first_date"
        }
        query_string = "params=%s" % json.dumps(params)
        results = self.web_access.get("/api/stores", query_string, cookies=self.cooks).json()["stores"]

        openings = results["openings"]["grid"]
        closings = results["closings"]["grid"]
        t0 = results["t0"]["grid"]
        t1 = results["t1"]["grid"]

        self.test_case.assertEqual(len(openings["results"]), 3)
        self.test_case.assertListEqual(sorted(openings["results"]), sorted([
            [u"All Banners", 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, pid],
            [u"Company 1", 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, cid1],
            [u"Company 2", 15.5, 15.5, 15.5, 15.5, 15.5, 15.5, 15.5, cid2]
        ]))

        self.test_case.assertEqual(len(closings["results"]), 3)
        self.test_case.assertListEqual(sorted(closings["results"]), sorted([
            [u"All Banners", 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, pid],
            [u"Company 1", 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, cid1],
            [u"Company 2", 15.5, 15.5, 15.5, 15.5, 15.5, 15.5, 15.5, cid2]
        ]))

        self.test_case.assertEqual(len(t0["results"]), 3)
        self.test_case.assertListEqual(sorted(t0["results"]), sorted([
            [u"All Banners", None, None, None, None, None, None, None, pid],
            [u"Company 1", None, None, None, None, None, None, None, cid1],
            [u"Company 2", None, None, None, None, None, None, None, cid2]
        ]))

        self.test_case.assertEqual(len(t1["results"]), 3)
        self.test_case.assertListEqual(sorted(t1["results"]), sorted([
            [u"All Banners", 16, 16, 16, 16, 16, 16, 16, pid],
            [u"Company 1", 12, 12, 12, 12, 12, 12, 12, cid1],
            [u"Company 2", 20, 20, 20, 20, 20, 20, 20, cid2]
        ]))

    def test_retail_store_grid_helper__all_stores(self, web_app):

        company_id = insert_test_company(ctype="retail_banner")

        # always opened never closed
        trade_area_1 = insert_test_trade_area(company_id=company_id,
                                              opened_date=None,
                                              closed_date=None)

        # opened sept 1 2012, closed sept 1 2013
        trade_area_2 = insert_test_trade_area(company_id=company_id,
                                              opened_date=datetime.datetime(2012, 9, 1),
                                              closed_date=datetime.datetime(2013, 9, 1))

        # opened aug 1 2012, closed sept 1 2012
        trade_area_3 = insert_test_trade_area(company_id=company_id,
                                              opened_date=datetime.datetime(2012, 8, 1),
                                              closed_date=datetime.datetime(2012, 9, 1))

        # opened sept 1 2013
        trade_area_4 = insert_test_trade_area(company_id=company_id,
                                              opened_date=datetime.datetime(2013, 9, 1),
                                              closed_date=None)

        # opened aug 25 2013
        trade_area_5 = insert_test_trade_area(company_id=company_id,
                                              opened_date=datetime.datetime(2013, 8, 25),
                                              closed_date=None)

        # opened aug 1 2012, closed oct 1 2013
        trade_area_6 = insert_test_trade_area(company_id=company_id,
                                              opened_date=datetime.datetime(2012, 8, 1),
                                              closed_date=datetime.datetime(2013, 10, 1))

        # ____ test sept 1 2012
        grid_id = "stores"
        date_filter = datetime.datetime(2012, 9, 1).isoformat()
        all_stores_date_state = "first_date"

        params = {
            "grid_id": grid_id,
            "all_stores_date_state": all_stores_date_state,
            "date_filter": date_filter,
            "company_ids": [company_id],
            "show_competition": True
        }

        rsgh = RetailStoreGridHelper(web_app, params, None)
        rsgh._parse_params()
        rsgh._get_stores_for_grid()

        # these stores are really trade areas
        results = rsgh.to_dict()["stores"]
        trade_areas = results["results"]
        ta_id_index = results["field_list"].index("Trade Area ID")

        trade_area_ids = [ta[ta_id_index] for ta in trade_areas]

        self.test_case.assertEqual(3, len(trade_area_ids))
        self.test_case.assertSetEqual({trade_area_1, trade_area_2, trade_area_6}, set(trade_area_ids))

        # ____ test aug 2012 (end of month, really)
        grid_id = "stores"
        date_filter = datetime.datetime(2013, 8, 1).isoformat()
        all_stores_date_state = "second_date"

        params = {
            "grid_id": grid_id,
            "all_stores_date_state": all_stores_date_state,
            "date_filter": date_filter,
            "company_ids": [company_id],
            "show_competition": True
        }

        rsgh = RetailStoreGridHelper(web_app, params, None)
        rsgh._parse_params()
        rsgh._get_stores_for_grid()

        # these stores are really trade areas
        trade_areas = rsgh.to_dict()["stores"]["results"]
        trade_area_ids = [ta[ta_id_index] for ta in trade_areas]

        self.test_case.assertEqual(4, len(trade_area_ids))
        self.test_case.assertEqual({trade_area_1, trade_area_2, trade_area_5, trade_area_6}, set(trade_area_ids))

    #-----------------------------------# Private Helpers #-----------------------------------#

    def __make_analytics_dict(self, date, value):

        return {
            "demographics": {
                "monthly": {
                    "DistanceMiles10": {
                        key: {
                            "mean": [
                                {
                                    "target_year": ANALYTICS_TARGET_YEAR,
                                    "series": [
                                        {
                                            "date": date,
                                            "value": value
                                        }
                                    ]
                                }
                            ]
                        }
                        for key in [
                            "aggregate_trade_area_per_capita_income",
                            "aggregate_trade_area_households",
                            "aggregate_trade_area_population",
                            "aggregate_trade_area_income"
                        ]
                    }
                }
            },
            "competition_adjusted_demographics": {
                "monthly": {
                    "DistanceMiles10": {
                        key: {
                            "mean": [
                                {
                                    "target_year": ANALYTICS_TARGET_YEAR,
                                    "series": [
                                        {
                                            "date": date,
                                            "value": value
                                        }
                                    ]
                                }
                            ]
                        }
                        for key in [
                            "aggregate_trade_area_households",
                            "aggregate_trade_area_population",
                            "aggregate_trade_area_income"
                        ]
                    }
                }
            }
        }

    def __make_can_data(self, data, engine="demographics"):

        if engine == "demographics":
            return {
                "aggregate_trade_area_per_capita_income_for_store_openings": data,
                "aggregate_trade_area_households_for_store_openings": data,
                "aggregate_trade_area_population_for_store_openings": data,
                "aggregate_trade_area_income_for_store_openings": data,
                "aggregate_trade_area_per_capita_income_for_store_closings": data,
                "aggregate_trade_area_households_for_store_closings": data,
                "aggregate_trade_area_population_for_store_closings": data,
                "aggregate_trade_area_income_for_store_closings": data
            }
        elif engine == "competition_adjusted_demographics":
            return {
                "aggregate_trade_area_households_for_store_openings": data,
                "aggregate_trade_area_population_for_store_openings": data,
                "aggregate_trade_area_income_for_store_openings": data,
                "aggregate_trade_area_households_for_store_closings": data,
                "aggregate_trade_area_population_for_store_closings": data,
                "aggregate_trade_area_income_for_store_closings": data
            }
        else:
            return {}