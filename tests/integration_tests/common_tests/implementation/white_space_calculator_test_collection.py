from datetime import timedelta

from bson.objectid import ObjectId

from core.common.business_logic.service_entity_logic.white_space_grid_helper import select_cell_matches_for_banners
from geoprocessing.geoprocessors.white_space.gp14_core_whitespace_competition import GP14CoreWhitespaceCompetition
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_white_space_grid, insert_test_white_space_grid_cell, insert_test_store, insert_test_trade_area, select_trade_area, insert_test_company
from common.business_logic.white_space.white_space_calculator import AGG_INCOME, WHITE_SPACE_GRID_CELL_FIELD_META
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from infrastructure.caching.load_white_space_redis_cache import WhiteSpaceRedisLoader
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import get_start_date_of_previous_month, get_first_day_of_month_one_year_ago, LAST_ANALYTICS_DATE


__author__ = 'erezrubinstein'


class WhiteSpaceCalculatorTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            "user_id": ObjectId(),
            "source": "white_space_analytics_integration_tests"
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()

        # show all
        self.test_case.maxDiff = None

    # ---------------------------------- Begin Testing ---------------------------------- #

    def test_calculator_complete_run(self):

        # create a grid
        grid_name = "10 Mile Squares"
        grid_threshold = "SquareMiles10"
        grid_id = insert_test_white_space_grid(grid_threshold, grid_name)

        # some helper dates
        recent_date = get_start_date_of_previous_month(LAST_ANALYTICS_DATE)
        one_year_ago_first_day = get_first_day_of_month_one_year_ago(LAST_ANALYTICS_DATE)
        old_date = one_year_ago_first_day - timedelta(days=1)

        # create four cells within the grid
        grid_cell_1_id = insert_test_white_space_grid_cell(grid_id, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], grid_threshold, grid_name, 0.5, 0.5, agg_income=10000)
        grid_cell_2_id = insert_test_white_space_grid_cell(grid_id, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], grid_threshold, grid_name, 1.5, 1.5, agg_income=3500)
        grid_cell_3_id = insert_test_white_space_grid_cell(grid_id, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], grid_threshold, grid_name, 2.5, 2.5, agg_income=2700)
        grid_cell_4_id = insert_test_white_space_grid_cell(grid_id, [[[4, 4], [3, 4], [3, 3], [4, 3], [4, 4]]], grid_threshold, grid_name, 3.5, 3.5, agg_income=25)
        
        # create two companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()

        # create several stores.
        # grid 1: two recently opened stores.
        # grid 2: one store opened on the first day of the month that was one year ago.
        # grid 3: one store opened more than a year ago (by one day)
        # grid 4: no openings
        store_id_1 = insert_test_store(company_id_1, [recent_date, None])
        store_id_2 = insert_test_store(company_id_1, [recent_date, None])
        store_id_3 = insert_test_store(company_id_1, None)
        store_id_4 = insert_test_store(company_id_1, [one_year_ago_first_day, None])
        store_id_5 = insert_test_store(company_id_1, None)
        store_id_6 = insert_test_store(company_id_1, None)
        store_id_7 = insert_test_store(company_id_1, None)
        store_id_8 = insert_test_store(company_id_1, [old_date, None])
        store_id_9 = insert_test_store(company_id_1, None)
        store_id_10 = insert_test_store(company_id_1, None)
        store_id_11 = insert_test_store(company_id_1, None)
        store_id_12 = insert_test_store(company_id_1, None)

        # create one store for a different company (to test that it doesn't get included)
        store_id_13 = insert_test_store(company_id_2, None)

        # insert a bunch of trade areas:
        #  - 3 in grid 1 = + 7  | (10000)
        #  - 4 in grid 2 = - 1  | (3500)
        #  - 2 in grid 3 = 0    | (2700)
        #  - 3 in grid 4 = - 3  | (25)

        # current medians = 8.3333 x3, 875 x4, 1350 x2, 3333.333 x3 = 875
        # openings medians = 1000. x7                               = 1000
        # closings medians = 25/3 x3, 3500/4                        = 8.333333...
        # net medians = 1350 x2, 3500/3 x3, 1000 x10                = 1000

        trade_area_id_1 = insert_test_trade_area(store_id_1, company_id_1, longitude=0.1, latitude=0.1)
        trade_area_id_2 = insert_test_trade_area(store_id_2, company_id_1, longitude=0.2, latitude=0.2)
        trade_area_id_3 = insert_test_trade_area(store_id_3, company_id_1, longitude=0.3, latitude=0.3)
        trade_area_id_4 = insert_test_trade_area(store_id_4, company_id_1, longitude=1.1, latitude=1.3)
        trade_area_id_5 = insert_test_trade_area(store_id_5, company_id_1, longitude=1.5, latitude=1.5)
        trade_area_id_6 = insert_test_trade_area(store_id_6, company_id_1, longitude=1.4, latitude=1.4)
        trade_area_id_7 = insert_test_trade_area(store_id_7, company_id_1, longitude=1.5, latitude=1.5)
        trade_area_id_8 = insert_test_trade_area(store_id_8, company_id_1, longitude=2.1, latitude=2.1)
        trade_area_id_9 = insert_test_trade_area(store_id_9, company_id_1, longitude=2.5, latitude=2.5)
        trade_area_id_10 = insert_test_trade_area(store_id_10, company_id_1, longitude=3.4, latitude=3.4)
        trade_area_id_11 = insert_test_trade_area(store_id_11, company_id_1, longitude=3.5, latitude=3.5)
        trade_area_id_12 = insert_test_trade_area(store_id_12, company_id_1, longitude=3.1, latitude=3.1)

        # create a trade area for the the second company (to test that it's not included)
        trade_area_id_13 = insert_test_trade_area(store_id_13, company_id_2, longitude=3.1, latitude=3.1)

        # run gp14 on all trade areas
        gp = GP14CoreWhitespaceCompetition()
        gp.process_object(select_trade_area(trade_area_id_1))
        gp.process_object(select_trade_area(trade_area_id_2))
        gp.process_object(select_trade_area(trade_area_id_3))
        gp.process_object(select_trade_area(trade_area_id_4))
        gp.process_object(select_trade_area(trade_area_id_5))
        gp.process_object(select_trade_area(trade_area_id_6))
        gp.process_object(select_trade_area(trade_area_id_7))
        gp.process_object(select_trade_area(trade_area_id_8))
        gp.process_object(select_trade_area(trade_area_id_9))
        gp.process_object(select_trade_area(trade_area_id_10))
        gp.process_object(select_trade_area(trade_area_id_11))
        gp.process_object(select_trade_area(trade_area_id_12))
        gp.process_object(select_trade_area(trade_area_id_13))

        # reset the redis cache (which the calc is dependent on)
        # this is totally a hack...  Let me know if you have a better suggestion.
        # But don't refactor without talking to me. - ER
        WhiteSpaceRedisLoader("localhost", "itest_mds", "localhost").fo_shizzle()

        # run analytics on all the grids in the db (everything synchronous)
        self.main_access.call_run_white_space_analytics(True, False)

        # run an analytics calculator for company 1
        results = self.main_access.call_calculate_company_white_space(company_id_1, grid_threshold, AGG_INCOME, 1000,
                                                                      include_cells=True)

        # some expected values (makes the division easier below) :)
        current_demographic_median = 875.0
        openings_demographic_median = 1000.0
        closing_demographic_median = 25.0 / 3
        churn_saturation_demographic_median = 1000.0

        # make sure results (i.e. totals) are correct
        self.test_case.assertEqual(results, {
            "stores_total": {
                "current": 12,
                "potential_openings": 7,
                "potential_closings": 4,
                "potential_churn_net": 3,
                "potential_churn_saturation": 15
            },
            "stores_percent_change": {
                "current": 100.0,
                "potential_openings": 7 / 12.0 * 100,
                "potential_closings": -4 / 12.0 * 100,
                "potential_churn_net": 3 / 12.0 * 100,
                "potential_churn_saturation": 3 / 12.0 * 100
            },
            "median_demographic_total": {
                "current": current_demographic_median,
                "potential_openings": openings_demographic_median,
                "potential_closings": closing_demographic_median,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": churn_saturation_demographic_median
            },
            "median_demographic_change": {
                "current": 100.0,
                "potential_openings": (openings_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_closings": (closing_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": (churn_saturation_demographic_median - current_demographic_median) / current_demographic_median * 100
            },
            "cell_results": {
                "min_churn": -3,
                "max_churn": 7,
                "meta": {
                    "num_rows": 4
                },
                "field_list": [
                    "Cell ID",
                    "Coordinates",
                    "# Stores - Target Banner",
                    "# Weighted Stores - All",
                    "Churn Potential",
                    "Saturation",
                    "Current Aggregate Income per Store ($M)",
                    "Incremental Aggregate Income per Store ($M)",
                    "Saturation Aggregate Income per Store ($M)"
                ],
                "field_meta": WHITE_SPACE_GRID_CELL_FIELD_META,
                "results": [
                    self._create_cell_match_calc_result(grid_cell_1_id, 7, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], 10000, 3, 3),
                    self._create_cell_match_calc_result(grid_cell_2_id, -1, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], 3500, 4, 4),
                    self._create_cell_match_calc_result(grid_cell_3_id, 0, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], 2700, 2, 2),
                    self._create_cell_match_calc_result(grid_cell_4_id, -3, [[[4, 4], [3, 4], [3, 3], [4, 3], [4, 4]]], 25, 3, 3)
                ]
            }
        })

        # run an analytics again, but set a threshold for the cells
        results = self.main_access.call_calculate_company_white_space(company_id_1, grid_threshold, AGG_INCOME, 1000,
                                                                      include_cells=True, cell_threshold=3)

        # make sure results (i.e. totals) are correct
        self.test_case.assertEqual(results, {
            "stores_total": {
                "current": 12,
                "potential_openings": 7,
                "potential_closings": 4,
                "potential_churn_net": 3,
                "potential_churn_saturation": 15
            },
            "stores_percent_change": {
                "current": 100.0,
                "potential_openings": 7 / 12.0 * 100,
                "potential_closings": -4 / 12.0 * 100,
                "potential_churn_net": 3 / 12.0 * 100,
                "potential_churn_saturation": 3 / 12.0 * 100
            },
            "median_demographic_total": {
                "current": current_demographic_median,
                "potential_openings": openings_demographic_median,
                "potential_closings": closing_demographic_median,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": churn_saturation_demographic_median
            },
            "median_demographic_change": {
                "current": 100.0,
                "potential_openings": (openings_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_closings": (closing_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": (churn_saturation_demographic_median - current_demographic_median) / current_demographic_median * 100
            },
            "cell_results": {
                "min_churn": -3,
                "max_churn": 7,
                "meta": {
                    "num_rows": 4
                },
                "field_list": [
                    "Cell ID",
                    "Coordinates",
                    "# Stores - Target Banner",
                    "# Weighted Stores - All",
                    "Churn Potential",
                    "Saturation",
                    "Current Aggregate Income per Store ($M)",
                    "Incremental Aggregate Income per Store ($M)",
                    "Saturation Aggregate Income per Store ($M)"
                ],
                "field_meta": WHITE_SPACE_GRID_CELL_FIELD_META,
                "results": [
                    # everything still included because there are stores there
                    self._create_cell_match_calc_result(grid_cell_1_id, 7, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], 10000, 3, 3),
                    self._create_cell_match_calc_result(grid_cell_2_id, -1, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], 3500, 4, 4),
                    self._create_cell_match_calc_result(grid_cell_3_id, 0, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], 2700, 2, 2),
                    self._create_cell_match_calc_result(grid_cell_4_id, -3, [[[4, 4], [3, 4], [3, 3], [4, 3], [4, 4]]], 25, 3, 3)
                ]
            }
        })

        # query all the grid cell matches and make sure they're correct
        matches = select_cell_matches_for_banners([company_id_1], grid_threshold)

        # remove ids for each match to make the Equal be easier
        for match in matches:
            del match["_id"]

        # make sure all the matches are the same as we expect them
        self.test_case.assertEqual(sorted(matches), sorted([
            self._create_cell(grid_cell_1_id, 3, True, company_id_1),
            self._create_cell(grid_cell_2_id, 4, True, company_id_1),
            self._create_cell(grid_cell_3_id, 2, False, company_id_1),
            self._create_cell(grid_cell_4_id, 3, False, company_id_1)
        ]))


    def test_calculator_complete_run__with_competition(self):

        # create a grid
        grid_name = "10 Mile Squares"
        grid_threshold = "SquareMiles10"
        grid_id = insert_test_white_space_grid(grid_threshold, grid_name)

        # create a few cells
        grid_cell_1_id = insert_test_white_space_grid_cell(grid_id, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], grid_threshold, grid_name, 0.5, 0.5, agg_income=1000)
        grid_cell_2_id = insert_test_white_space_grid_cell(grid_id, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], grid_threshold, grid_name, 1.5, 1.5, agg_income=2000)
        grid_cell_3_id = insert_test_white_space_grid_cell(grid_id, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], grid_threshold, grid_name, 2.5, 2.5, agg_income=3000)

        # create three companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()
        company_id_3 = insert_test_company()

        # create competition structure for white space
        competition = {
            company_id_1: 1,
            company_id_2: 1,
            company_id_3: 0.5
        }

        # create a few stores per each company
        store_id_1_1 = insert_test_store(company_id_1, None)
        store_id_1_2 = insert_test_store(company_id_1, None)
        store_id_2_1 = insert_test_store(company_id_2, None)
        store_id_2_2 = insert_test_store(company_id_2, None)
        store_id_3_1 = insert_test_store(company_id_3, None)
        store_id_3_2 = insert_test_store(company_id_3, None)

        # create a trade area per each store
        trade_area_id_1_1 = insert_test_trade_area(store_id_1_1, company_id_1, longitude=0.2, latitude=0.2) # cell 1
        trade_area_id_1_2 = insert_test_trade_area(store_id_1_2, company_id_1, longitude=1.1, latitude=1.3) # cell 2
        trade_area_id_2_1 = insert_test_trade_area(store_id_2_1, company_id_2, longitude=1.5, latitude=1.5) # cell 2
        trade_area_id_2_2 = insert_test_trade_area(store_id_2_2, company_id_2, longitude=1.4, latitude=1.1) # cell 2
        trade_area_id_3_1 = insert_test_trade_area(store_id_3_1, company_id_3, longitude=2.5, latitude=2.5) # cell 3
        trade_area_id_3_2 = insert_test_trade_area(store_id_3_2, company_id_3, longitude=2.4, latitude=2.4) # cell 3

        # run gp14 on all trade areas
        gp = GP14CoreWhitespaceCompetition()
        gp.process_object(select_trade_area(trade_area_id_1_1))
        gp.process_object(select_trade_area(trade_area_id_1_2))
        gp.process_object(select_trade_area(trade_area_id_2_1))
        gp.process_object(select_trade_area(trade_area_id_2_2))
        gp.process_object(select_trade_area(trade_area_id_3_1))
        gp.process_object(select_trade_area(trade_area_id_3_2))

        # reset the redis cache (which the calc is dependent on)
        # this is totally a hack...  Let me know if you have a better suggestion.
        # But don't refactor without talking to me. - ER
        WhiteSpaceRedisLoader("localhost", "itest_mds", "localhost").fo_shizzle()

        # run analytics on all the grids in the db (everything synchronous)
        self.main_access.call_run_white_space_analytics(True, False)

        # run an analytics calculator for company 1
        results = self.main_access.call_calculate_company_white_space(company_id_1, grid_threshold, AGG_INCOME, 1000, include_cells=True, competition=competition)

        # some expected values (makes the division easier below) :)
        current_demographic_median = (1000.0 + 2000.0 / 3.0) / 2.0
        openings_demographic_median = 1000
        closings_demographic_median = 2000 / 3.0
        churn_saturation_demographic_median = 1000.0

        # make sure results (i.e. totals) are correct
        self.test_case.assertEqual(results, {
            "stores_total": {
                "current": 2,
                "potential_openings": 2,
                "potential_closings": 1,
                "potential_churn_net": 1,
                "potential_churn_saturation": 3
            },
            "stores_percent_change": {
                "current": 100.0,
                "potential_openings": 2 / 2.0 * 100,
                "potential_closings": -1 / 2.0 * 100,
                "potential_churn_net": 1 / 2.0 * 100,
                "potential_churn_saturation": 1 / 2.0 * 100
            },
            "median_demographic_total": {
                "current": current_demographic_median,
                "potential_openings": openings_demographic_median,
                "potential_closings": closings_demographic_median,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": churn_saturation_demographic_median
            },
            "median_demographic_change": {
                "current": 100.0,
                "potential_openings": (openings_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_closings": (closings_demographic_median - current_demographic_median) / current_demographic_median * 100,
                "potential_churn_net": "N/A",
                "potential_churn_saturation": (churn_saturation_demographic_median - current_demographic_median) / current_demographic_median * 100
            },
            "cell_results": {
                "min_churn": -1,
                "max_churn": 2,
                "meta": {
                    "num_rows": 3
                },
                "field_list": [
                    "Cell ID",
                    "Coordinates",
                    "# Stores - Target Banner",
                    "# Weighted Stores - All",
                    "Churn Potential",
                    "Saturation",
                    "Current Aggregate Income per Store ($M)",
                    "Incremental Aggregate Income per Store ($M)",
                    "Saturation Aggregate Income per Store ($M)"
                ],
                "field_meta": WHITE_SPACE_GRID_CELL_FIELD_META,
                "results": [
                    # everything still included because there are stores there
                    self._create_cell_match_calc_result(grid_cell_1_id, 0, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], 1000, 1, 1),
                    self._create_cell_match_calc_result(grid_cell_2_id, -1, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], 2000, 1, 3),
                    self._create_cell_match_calc_result(grid_cell_3_id, 2, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], 3000, 0, 1)
                ]
            }
        })

    # -------------------------- Private Helpers -------------------------- #

    def _create_cell_match_calc_result(self, cell_id, churn_potential, coordinates, demographic, store_count_target, store_count_all):

        increment = 1.0 if churn_potential > -1.0 else -1.0

        return [
            cell_id,
            coordinates,
            store_count_target,
            store_count_all,
            churn_potential,
            churn_potential + store_count_target,
            demographic / float(store_count_all) if store_count_all > 0 else demographic,
            demographic / float(abs(store_count_all + increment)) if abs(store_count_all + increment) > 0 else demographic,
            demographic / float(abs(churn_potential + store_count_all)) if abs(churn_potential + store_count_all) > 0 else demographic
        ]

    def _create_cell(self, cell_id, store_count, has_openings, company_id):

        return {
            "data": {
                "cell_id": cell_id,
                "store_count": store_count,
                "has_openings": has_openings,
                "company_id": company_id
            }
        }
