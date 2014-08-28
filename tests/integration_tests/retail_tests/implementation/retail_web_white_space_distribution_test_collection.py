from __future__ import division
import json

from scipy import stats
from requests.cookies import RequestsCookieJar

from common.utilities.date_utilities import LAST_ANALYTICS_DATE
from retail.v010.data_access.controllers.white_space_competition_set_controller import WhiteSpaceCompetitionSetController
from geoprocessing.geoprocessors.white_space.gp14_core_whitespace_competition import GP14CoreWhitespaceCompetition
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_white_space_grid, insert_test_white_space_grid_cell, insert_test_store, insert_test_trade_area, select_trade_area, insert_test_company
from common.business_logic.white_space.white_space_calculator import AGG_INCOME
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from infrastructure.caching.load_white_space_redis_cache import WhiteSpaceRedisLoader
from retail.v010.data_access.controllers.user_controller import UserController


class RetailWebWhiteSpaceDistributionTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_controller = UserController()
        self.wscomp_controller = WhiteSpaceCompetitionSetController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}

    def setUp(self):
        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])

    def tearDown(self):
        pass

    ##------------------------------------ Private helpers --------------------------------------##

    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params, time_out=1000)
        assert response.ok and isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __get_default_users(self):
        self.user_test = self.user_controller.User.get("test@nexusri.com")
        self.user_client_support = self.user_controller.User.get("client_support@nexusri.com")
        self.user_normal = self.user_controller.User.get("user@nexusri.com")

    ##------------------------------------ Tests --------------------------------------##

    def retail_test_get_white_space_competition_demographic_distribution(self):
        self.test_case.maxDiff = None

        # create a grid
        grid_name = "10 Mile Squares"
        grid_threshold = "SquareMiles10"
        grid_id = insert_test_white_space_grid(grid_threshold, grid_name)

        # create a few cells
        grid_cell_1_id = insert_test_white_space_grid_cell(str(grid_id), [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], grid_threshold, grid_name, 0.5, 0.5, agg_income=1000)
        grid_cell_2_id = insert_test_white_space_grid_cell(str(grid_id), [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], grid_threshold, grid_name, 1.5, 1.5, agg_income=2000)
        grid_cell_3_id = insert_test_white_space_grid_cell(str(grid_id), [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], grid_threshold, grid_name, 2.5, 2.5, agg_income=3000)
        grid_cell_4_id = insert_test_white_space_grid_cell(str(grid_id), [[[5, 5], [4, 5], [4, 4], [5, 4], [5, 5]]], grid_threshold, grid_name, 4.5, 4.5, agg_income=4000)

        # create three companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()
        company_id_3 = insert_test_company()

        # create a few stores per each company
        store_id_1_1 = insert_test_store(company_id_1, None)
        store_id_1_2 = insert_test_store(company_id_1, None)
        store_id_1_3 = insert_test_store(company_id_1, None)
        store_id_1_4 = insert_test_store(company_id_1, [LAST_ANALYTICS_DATE, None])
        store_id_2_1 = insert_test_store(company_id_2, None)
        store_id_3_1 = insert_test_store(company_id_3, None)
        store_id_3_2 = insert_test_store(company_id_3, None)

        # create a trade area per each store
        trade_area_id_1_1 = insert_test_trade_area(store_id_1_1, company_id_1, longitude=0.2, latitude=0.2)  # cell 1
        trade_area_id_1_2 = insert_test_trade_area(store_id_1_2, company_id_1, longitude=1.1, latitude=1.3)  # cell 2
        trade_area_id_2_1 = insert_test_trade_area(store_id_2_1, company_id_2, longitude=1.5, latitude=1.5)  # cell 2
        trade_area_id_1_3 = insert_test_trade_area(store_id_1_3, company_id_1, longitude=2.4, latitude=2.5)  # cell 3
        trade_area_id_3_1 = insert_test_trade_area(store_id_3_1, company_id_3, longitude=2.5, latitude=2.5)  # cell 3
        trade_area_id_3_2 = insert_test_trade_area(store_id_3_2, company_id_3, longitude=2.4, latitude=2.4)  # cell 3
        trade_area_id_1_4 = insert_test_trade_area(store_id_1_4, company_id_1, longitude=4.5, latitude=4.5)  # cell 4

        # run gp14 on all trade areas
        gp = GP14CoreWhitespaceCompetition()
        gp.process_object(select_trade_area(trade_area_id_1_1))
        gp.process_object(select_trade_area(trade_area_id_1_2))
        gp.process_object(select_trade_area(trade_area_id_1_3))
        gp.process_object(select_trade_area(trade_area_id_1_4))
        gp.process_object(select_trade_area(trade_area_id_2_1))
        gp.process_object(select_trade_area(trade_area_id_3_1))
        gp.process_object(select_trade_area(trade_area_id_3_2))

        # reset the redis cache (which the calc is dependent on)
        # this is totally a hack...  Let me know if you have a better suggestion.
        # But don't refactor without talking to me. - ER
        WhiteSpaceRedisLoader("localhost", "itest_mds", "localhost").fo_shizzle()

        # run analytics on all the grids in the db (everything synchronous)
        self.main_access.call_run_white_space_analytics(True, False)

        data = json.dumps({
            "banner_id": company_id_1,
            "demographic": AGG_INCOME,
            "threshold": grid_threshold,
            "competition": {
                company_id_1: 1,
                company_id_2: 1,
                company_id_3: 0.5
            },
            "as_of_date": LAST_ANALYTICS_DATE.isoformat() # for now...
        })
        response = self.web_access.put("/api/whitespace/competition_demographic_distributions", data,
                                       headers=self.json_headers, cookies=self.admin_cooks).json()

        expected_results = {
            # manually calculated, sucka
            'current': self._get_distribution([1000, 1000, 1500, 4000]),
            'openings': self._get_distribution([4000])
        }

        self.test_case.assertDictEqual(response, {
            "current": response["current"],
            "openings": expected_results["openings"]
        })

        self.test_case.assertListEqual(response["openings"], expected_results["openings"])
        self.test_case.assertEqual(len(response["current"]), 10)

        for i, curr in enumerate(expected_results["current"]):
            self.test_case.assertAlmostEqual(curr, response["current"][i], places=5)


    # ----------------- Private Helpers ----------------- #

    def _get_distribution(self, values):

        deciles = []

        # it's possible to have no demographics.  This happens when a company has no openings at all.
        if values:

            for i in range(1, 11):
                decile = stats.scoreatpercentile(values, 10*i)
                deciles.append(decile)

        return deciles