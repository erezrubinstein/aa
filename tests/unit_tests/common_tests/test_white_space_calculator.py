from common.business_logic.white_space.white_space_calculator import WhiteSpaceCalculator, generate_square_threshold, TOTAL_POPULATION
from core.common.business_logic.service_entity_logic import white_space_grid_helper
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.business_logic.white_space import redis_helper
from mox import IgnoreArg
import mox


__author__ = 'erezrubinstein'


class WhiteSpaceCalculatorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WhiteSpaceCalculatorTests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # stub/record a mock redis helper
        self.mox.StubOutClassWithMocks(redis_helper, "RedisHelper")
        self.mock_redis_helper = redis_helper.RedisHelper(IgnoreArg(), IgnoreArg())

        # replay all and reset
        self.mox.ReplayAll()

        # create the calculator
        self.calculator = WhiteSpaceCalculator()

        # reset the mox
        self.mox.ResetAll()

    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(WhiteSpaceCalculatorTests, self).doCleanups()
        dependencies.clear()


    def test_calculate(self):

        # create calculator values
        banner_id = "woot"
        grid_threshold = generate_square_threshold(10)
        demographic_metric = TOTAL_POPULATION
        demographic_threshold = 1000

        # create mock cells (with various demographics)
        mock_cells = [
            self._create_mock_cell(1, 1000, [[[1,1], [1,1], [1,1], [1,1], [1,1]]]),
            self._create_mock_cell(2, 1700, [[[2,2], [2,2], [2,2], [2,2], [2,2]]]),
            self._create_mock_cell(3, 2000, [[[3,3], [3,3], [3,3], [3,3], [3,3]]]),
            self._create_mock_cell(4, 2500, [[[4,4], [4,4], [4,4], [4,4], [4,4]]]),
            self._create_mock_cell(5, 500, [[[5,5], [5,5], [5,5], [5,5], [5,5]]]),
            self._create_mock_cell(6, 125, [[[6,6], [6,6], [6,6], [6,6], [6,6]]]),
            self._create_mock_cell(7, 8000, [[[7,7], [7,7], [7,7], [7,7], [7,7]]]),
            self._create_mock_cell(8, 10000, [[[8,8], [8,8], [8,8], [8,8], [8,8]]]),
            self._create_mock_cell(9, 2000, [[[9,9], [9,9], [9,9], [9,9], [9,9]]])
        ]

        # medians
        # current           = 62.5 x2, 500, 666.67 x3, 1000, 1700, 2000, 2500, 10000
        # openings          = 1000, 1000 x8, 1000 x10, 1250
        # closings          = 125/2 x2, 500, 2000/3
        # churn_net         =
        # churn_saturation  = 1000, 1000 x2, 1000 x8, 1000 * 10, 1000 x2, 1250 * 2, 1700

        # create mock cell matches
        mock_cell_matches = [
            self._create_mock_cell_match(1, banner_id, 1), # 1000.   0 closings, 0 openings
            self._create_mock_cell_match(2, banner_id, 1), # 1700.   0 closings, 0 openings
            self._create_mock_cell_match(3, banner_id, 1), # 2000.   0 closings, 1 openings
            self._create_mock_cell_match(4, banner_id, 1), # 2500.   0 closings, 1 openings
            self._create_mock_cell_match(5, banner_id, 1), # 500.    1 closings, 0 openings
            self._create_mock_cell_match(6, banner_id, 2), # 125.    2 closings, 0 openings
            # skip cell_id 7                    # 8000.   0 closings, 8 openings
            self._create_mock_cell_match(8, banner_id, 1), # 10000.  0 closings, 9 openings
            self._create_mock_cell_match(9, banner_id, 3)  # 2000.   1 closings, 0 openings
        ]

        # stub out methods/classes
        self.mox.StubOutWithMock(white_space_grid_helper, "select_cell_matches_for_banners")
        self.mox.StubOutWithMock(self.calculator, "_get_combined_banner_ids")

        # begin recording
        self.mock_redis_helper.get_white_space_cells(grid_threshold, demographic_metric).AndReturn(mock_cells)
        self.calculator._get_combined_banner_ids(banner_id, None).AndReturn([banner_id])
        white_space_grid_helper.select_cell_matches_for_banners([banner_id], grid_threshold).AndReturn(mock_cell_matches)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = self.calculator.calculate_white_space(banner_id, grid_threshold, demographic_metric,
                                                        demographic_threshold)

        # some expected values (makes the division easier below) :)
        current_demographic_median = 2000.0 / 3.0
        openings_demographic_median = 1000.0
        closings_demographic_median = 281.25
        churn_saturation_demographic_median = 1000.0

        # make sure results (i.e. totals) are correct
        self.assertEqual(results, {
            "stores_total": {
                "current": 11,
                "potential_openings": 19,
                "potential_closings": 4,
                "potential_churn_net": 15,
                "potential_churn_saturation": 26
            },
            "stores_percent_change": {
                "current": 100.0,
                "potential_openings": 19.0 / 11.0 * 100,
                "potential_closings": -4.0 / 11.0 * 100,
                "potential_churn_net": 15.0 / 11.0 * 100,
                "potential_churn_saturation": 15.0 / 11.0 * 100
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
            }
        })

        expected_results = [
            self._create_cell_match_calc_result(1, 0, [[[1,1], [1,1], [1,1], [1,1], [1,1]]], 1000, 1),
            self._create_cell_match_calc_result(2, 0, [[[2,2], [2,2], [2,2], [2,2], [2,2]]], 1700, 1),
            self._create_cell_match_calc_result(3, 1, [[[3,3], [3,3], [3,3], [3,3], [3,3]]], 2000, 1),
            self._create_cell_match_calc_result(4, 1, [[[4,4], [4,4], [4,4], [4,4], [4,4]]], 2500, 1),
            self._create_cell_match_calc_result(5, -1, [[[5,5], [5,5], [5,5], [5,5], [5,5]]], 500, 1),
            self._create_cell_match_calc_result(6, -2, [[[6,6], [6,6], [6,6], [6,6], [6,6]]], 125, 2),
            self._create_cell_match_calc_result(7, 8, [[[7,7], [7,7], [7,7], [7,7], [7,7]]], 8000, 0),
            self._create_cell_match_calc_result(8, 9, [[[8,8], [8,8], [8,8], [8,8], [8,8]]], 10000, 1),
            self._create_cell_match_calc_result(9, -1, [[[9,9], [9,9], [9,9], [9,9], [9,9]]], 2000, 3)
        ]

        # make sure each individual cell match is correct (no thresholds)
        self.assertEqual(self.calculator.get_cell_results()["results"], expected_results)

        expected_results = [
            self._create_cell_match_calc_result(6, -2, [[[6,6], [6,6], [6,6], [6,6], [6,6]]], 125, 2),
            self._create_cell_match_calc_result(7, 8, [[[7,7], [7,7], [7,7], [7,7], [7,7]]], 8000, 0),
            self._create_cell_match_calc_result(8, 9, [[[8,8], [8,8], [8,8], [8,8], [8,8]]], 10000, 1),
        ]

        # make sure each individual cell match is correct (with thresholds)
        self.assertEqual(self.calculator.get_cell_results(2, -2)["results"], expected_results)

        # make sure each individual cell match is correct (with thresholds)
        self.assertEqual(self.calculator.get_cell_results(10, -10)["results"], [])

        expected_results = [
            self._create_cell_match_calc_result(1, 0, [[[1,1], [1,1], [1,1], [1,1], [1,1]]], 1000, 1),
            self._create_cell_match_calc_result(2, 0, [[[2,2], [2,2], [2,2], [2,2], [2,2]]], 1700, 1),
            self._create_cell_match_calc_result(3, 1, [[[3,3], [3,3], [3,3], [3,3], [3,3]]], 2000, 1),
            self._create_cell_match_calc_result(4, 1, [[[4,4], [4,4], [4,4], [4,4], [4,4]]], 2500, 1),
            self._create_cell_match_calc_result(5, -1, [[[5,5], [5,5], [5,5], [5,5], [5,5]]], 500, 1),
            self._create_cell_match_calc_result(6, -2, [[[6,6], [6,6], [6,6], [6,6], [6,6]]], 125, 2),
            self._create_cell_match_calc_result(8, 9, [[[8,8], [8,8], [8,8], [8,8], [8,8]]], 10000, 1),
            self._create_cell_match_calc_result(9, -1, [[[9,9], [9,9], [9,9], [9,9], [9,9]]], 2000, 3)
        ]

        # test the include stores option, which should be bring back all cells that has a store
        self.assertEqual(self.calculator.get_cell_results(10, -10, True)["results"], expected_results)


    def test_calculate_with_competition(self):

        # create calculator values
        banner_id = "woot"
        competition = {
            "chilly": 1,
            "woot": 1,
            "willy": .5
        }
        banner_ids = ["woot", "chilly", "willy"]
        grid_threshold = generate_square_threshold(10)
        demographic_metric = TOTAL_POPULATION
        demographic_threshold = 1000

        # create mock cells (with various demographics)
        mock_cells = [
            self._create_mock_cell(1, 1000, [[[1,1], [1,1], [1,1], [1,1], [1,1]]]),
            self._create_mock_cell(2, 2000, [[[2,2], [2,2], [2,2], [2,2], [2,2]]]),
            self._create_mock_cell(3, 3000, [[[3,3], [3,3], [3,3], [3,3], [3,3]]]),
            self._create_mock_cell(4, 1000, [[[4,4], [4,4], [4,4], [4,4], [4,4]]]),
        ]

        # medians
        # current           = 1000, 2000/3
        # openings          = 1000 X3
        # closings          = 2000/3
        # churn_net         = N/A
        # churn_saturation  = 1000 X3, 1000

        # create mock cell matches
        mock_cell_matches = [
            self._create_mock_cell_match(1, banner_id, 1), # 1000.   0 closings, 0 openings
            self._create_mock_cell_match(2, banner_id, 1), # 2000.   1 closings, 0 openings
            self._create_mock_cell_match(2, "chilly", 2),  # 2000.   1 closings, 0 openings
            self._create_mock_cell_match(3, "willy", 2),   # 3000.   0 closings, 1 openings
            self._create_mock_cell_match(4, "chilly", 1),   # 1000.   0 closings, 0 openings - not target banner
        ]

        # stub out methods/classes
        self.mox.StubOutWithMock(white_space_grid_helper, "select_cell_matches_for_banners")
        self.mox.StubOutWithMock(self.calculator, "_get_combined_banner_ids")

        # begin recording
        self.mock_redis_helper.get_white_space_cells(grid_threshold, demographic_metric).AndReturn(mock_cells)
        self.calculator._get_combined_banner_ids(banner_id, competition).AndReturn(banner_ids)
        white_space_grid_helper.select_cell_matches_for_banners(banner_ids, grid_threshold).AndReturn(mock_cell_matches)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = self.calculator.calculate_white_space(banner_id, grid_threshold, demographic_metric, demographic_threshold, competition)

        # some expected values (makes the division easier below) :)
        current_demographic_median = (1000.0 + 2000.0 / 3.0) / 2.0
        openings_demographic_median = 1000
        closings_demographic_median = 2000 / 3.0
        churn_saturation_demographic_median = 1000.0

        # make sure results (i. e. totals) are correct
        self.assertEqual(results, {
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
                # same as net, since we don't include the current in % change
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
            }
        })

        expected_results = [
            self._create_cell_match_calc_result(1, 0, [[[1,1], [1,1], [1,1], [1,1], [1,1]]], 1000, 1, 1),
            self._create_cell_match_calc_result(2, -1, [[[2,2], [2,2], [2,2], [2,2], [2,2]]], 2000, 1, 3),
            self._create_cell_match_calc_result(3, 2, [[[3,3], [3,3], [3,3], [3,3], [3,3]]], 3000, 0, 1),
            self._create_cell_match_calc_result(4, 0, [[[4,4], [4,4], [4,4], [4,4], [4,4]]], 1000, 0, 1)
        ]

        # make sure each individual cell match is correct (no thresholds)
        cell_results = self.calculator.get_cell_results(0, 0, False)["results"]
        self.assertEqual(cell_results, expected_results)

        # make sure each individual cell match is correct (same threshold as page/download, 1 / -1)
        # but set include_store_cells to True so that we get the 4th cell in the results,
        #   even though it's outside the churn threshold
        cell_results = self.calculator.get_cell_results(1, -1, True)["results"]
        self.assertEqual(cell_results, expected_results)

        # try again with page thresholds and include_store_cells = False
        # this time we should NOT get cells 1 and 4 because they have 0 churn potential
        cell_results = self.calculator.get_cell_results(1, -1, False)["results"]
        self.assertEqual(cell_results, expected_results[1:3])


    def test_get_combined_banner_ids(self):

        # create mock objects
        banner_id = 1
        mock_competitions = {
            1: 1,
            2: 1,
            3: 1,
            4: 1
        }

        # combine the lists and make sure that we get a unique set back
        banner_ids = self.calculator._get_combined_banner_ids(banner_id, mock_competitions)

        # assert, sucka
        self.assertEqual(banner_ids, [1, 2, 3, 4])


    def test_calculate_with_max_openings(self):

        # *** Test base case with no parameters. The reason I still have a test for this is
        #     so that we can have reference base calculations
        #

        # create calculator values
        banner_id = "woot"
        grid_threshold = generate_square_threshold(10)
        demographic_metric = TOTAL_POPULATION
        demographic_threshold = 10

        # create mock cells (with various demographics)
        mock_cells = [
            self._create_mock_cell(1, 10, [[[1,1], [1,1], [1,1], [1,1], [1,1]]]),
            self._create_mock_cell(2, 21, [[[2,2], [2,2], [2,2], [2,2], [2,2]]]),
            self._create_mock_cell(3, 30, [[[3,3], [3,3], [3,3], [3,3], [3,3]]]),
            self._create_mock_cell(4, 40, [[[4,4], [4,4], [4,4], [4,4], [4,4]]]),
            self._create_mock_cell(5, 50, [[[5,5], [5,5], [5,5], [5,5], [5,5]]]),
        ]

        # create mock cell matches
        mock_cell_matches = [
            self._create_mock_cell_match(1, banner_id, 1), # 10.   + 0
            self._create_mock_cell_match(2, banner_id, 1), # 20.   + 1
            self._create_mock_cell_match(3, banner_id, 4), # 30.   - 1
            self._create_mock_cell_match(4, banner_id, 1), # 40.   + 3
            self._create_mock_cell_match(5, banner_id, 7), # 50.   - 2
        ]

        # Create base case expected values here close to test data, easier to manually calculate
        expected_stores_total = {
            "current": 14,
            "potential_openings": 4,
            "potential_closings": 3,
            "potential_churn_net": 1,
            "potential_churn_saturation": 15
        }

        expected_stores_percent_change = {
            "current": 100.0,
            "potential_openings": 4.0 / 14.0 * 100,
            "potential_closings": -3.0 / 14.0 * 100,
            "potential_churn_net": 1.0 / 14.0 * 100,
            "potential_churn_saturation": 1.0 / 14.0 * 100
        }

        expected_median_demographic_total = {
            "current": 7.321428571428571,  # Rounding issue but should be close to ((50.0 / 7.0) + 7.5) / 2.0,
                                           #  (50/7) = 7.14 x 7; (30/4) = 7.5 x 4; 10; 20; 40;
            "potential_openings": 10.0,  # 10 x 3, 10.5
            "potential_closings": (50.0 / 7.0),
            "potential_churn_net": "N/A",
            "potential_churn_saturation": 10.0
        }

        expected_cell_results = [
            self._create_cell_match_calc_result(1, 0, [[[1,1], [1,1], [1,1], [1,1], [1,1]]], 10, 1),
            self._create_cell_match_calc_result(2, 1, [[[2,2], [2,2], [2,2], [2,2], [2,2]]], 21, 1),
            self._create_cell_match_calc_result(3, -1, [[[3,3], [3,3], [3,3], [3,3], [3,3]]], 30, 4),
            self._create_cell_match_calc_result(4, 3, [[[4,4], [4,4], [4,4], [4,4], [4,4]]], 40, 1),
            self._create_cell_match_calc_result(5, -2, [[[5,5], [5,5], [5,5], [5,5], [5,5]]], 50, 7),
        ]


        # stub out methods/classes
        self.mox.StubOutWithMock(white_space_grid_helper, "select_cell_matches_for_banners")
        self.mox.StubOutWithMock(self.calculator, "_get_combined_banner_ids")

        # begin recording
        self.mock_redis_helper.get_white_space_cells(grid_threshold, demographic_metric).AndReturn(mock_cells)
        self.calculator._get_combined_banner_ids(banner_id, None).AndReturn([banner_id])
        white_space_grid_helper.select_cell_matches_for_banners([banner_id], grid_threshold).AndReturn(mock_cell_matches)

        # replay all
        self.mox.ReplayAll()

        # Test and assert base case
        results = self.calculator.calculate_white_space(banner_id, grid_threshold, demographic_metric,
                                                        demographic_threshold)

        self.assertEqual(results["stores_total"], expected_stores_total)
        self.assertEqual(results["stores_percent_change"], expected_stores_percent_change)
        self.assertEqual(results["median_demographic_total"], expected_median_demographic_total)
        # Not going to test the median_demographic_change since its already tested elsewhere

        # Check cell results
        self.assertEqual(self.calculator.get_cell_results()["results"], expected_cell_results)

        #
        # *** Test max_openings parameter
        #
        maximum_openings = 2

        # Now there should be one less potential opening (+2 for cell 4 instead of +3)
        expected_stores_total = {
            "current": 14,
            "potential_openings": 3,
            "potential_closings": 3,
            "potential_churn_net": 0,
            "potential_churn_saturation": 14
        }

        expected_stores_percent_change = {
            "current": 100.0,
            "potential_openings": 3.0 / 14.0 * 100,
            "potential_closings": -3.0 / 14.0 * 100,
            "potential_churn_net": 0.0 / 14.0 * 100,
            "potential_churn_saturation": 0.0 / 14.0 * 100
        }

        expected_median_demographic_total = {
            "current": 7.321428571428571,  # Rounding issue but should be close to ((50.0 / 7.0) + 7.5) / 2.0,
                                           #  (50/7) = 7.14 x 7; (30/4) = 7.5 x 4; 10; 20; 40;
            # 40.0 / 3 (Normalized by 3 instead of 4 because the total_potential is capped by the max_openings parameter)
            # And median from [40.0/3, 40.0/3, 10]
            "potential_openings": 40.0 / 3,
            "potential_closings": (50.0 / 7.0),
            "potential_churn_net": "N/A",
            "potential_churn_saturation": 10.0
        }

        expected_cell_results = [
            self._create_cell_match_calc_result(1, 0, [[[1,1], [1,1], [1,1], [1,1], [1,1]]], 10, 1),
            self._create_cell_match_calc_result(2, 1, [[[2,2], [2,2], [2,2], [2,2], [2,2]]], 21, 1),
            self._create_cell_match_calc_result(3, -1, [[[3,3], [3,3], [3,3], [3,3], [3,3]]], 30, 4),
            self._create_cell_match_calc_result(4, 2, [[[4,4], [4,4], [4,4], [4,4], [4,4]]], 40, 1),
            self._create_cell_match_calc_result(5, -2, [[[5,5], [5,5], [5,5], [5,5], [5,5]]], 50, 7),
        ]

        # Reset the tests
        self.calculator._cell_match_calculations = []
        self.mox.ResetAll()
        self.mox.UnsetStubs()

        self.mox.StubOutWithMock(white_space_grid_helper, "select_cell_matches_for_banners")
        self.mox.StubOutWithMock(self.calculator, "_get_combined_banner_ids")

        self.mock_redis_helper.get_white_space_cells(grid_threshold, demographic_metric).AndReturn(mock_cells)
        self.calculator._get_combined_banner_ids(banner_id, None).AndReturn([banner_id])
        white_space_grid_helper.select_cell_matches_for_banners([banner_id], grid_threshold).AndReturn(mock_cell_matches)

        self.mox.ReplayAll()

        # Run with max_openings parameter
        results = self.calculator.calculate_white_space(banner_id, grid_threshold, demographic_metric,
                                                        demographic_threshold, maximum_openings=maximum_openings)

        # Check various calcs
        self.assertEqual(results["stores_total"], expected_stores_total)
        self.assertEqual(results["stores_percent_change"], expected_stores_percent_change)
        self.assertEqual(results["median_demographic_total"], expected_median_demographic_total)
        # Not going to test the median_demographic_change since its already tested elsewhere and derived directly from
        # "median_demographic_total"

        # Check cell results
        self.assertEqual(self.calculator.get_cell_results()["results"], expected_cell_results)



    # -------------------------- Private Helpers -------------------------- #

    def _create_mock_cell(self, cell_id, demographic_value, shape):

        return {
            "id": cell_id,
            "d": demographic_value,
            "c": shape
        }

    def _create_mock_cell_match(self, cell_id, company_id, store_count):

        return {
            "data": {
                "cell_id": cell_id,
                "company_id": company_id,
                "store_count": store_count
            }
        }

    def _create_cell_match_calc_result(self, cell_id, churn_potential, coordinates, demographic, store_count, weighted_store_count_all = None):

        increment = 1.0 if churn_potential > -1.0 else -1.0

        # default weighted_store_count_all to store_count
        if not weighted_store_count_all:
            weighted_store_count_all = store_count

        return [
            cell_id,
            coordinates,
            store_count,
            weighted_store_count_all,
            churn_potential,
            churn_potential + store_count,
            demographic / float(weighted_store_count_all) if weighted_store_count_all > 0 else demographic,
            demographic / float(abs(weighted_store_count_all + increment)) if abs(weighted_store_count_all + increment) > 0 else demographic,
            demographic / float(abs(churn_potential + weighted_store_count_all)) if abs(churn_potential + weighted_store_count_all) > 0 else demographic
        ]