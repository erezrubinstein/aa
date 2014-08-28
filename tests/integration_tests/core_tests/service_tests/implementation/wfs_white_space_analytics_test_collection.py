from datetime import timedelta
import datetime

from bson.objectid import ObjectId

from geoprocessing.geoprocessors.white_space.gp14_core_whitespace_competition import GP14CoreWhitespaceCompetition
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_white_space_grid, insert_test_white_space_grid_cell, insert_test_trade_area, select_trade_area, insert_test_store, select_all_white_space_grid_cell_matches, insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import get_start_date_of_previous_month, get_first_day_of_month_one_year_ago, LAST_ANALYTICS_DATE


__author__ = "erezrubinstein"


class WFSWhiteSpaceAnalyticsTestCollection(ServiceTestCollection):

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

    def test_white_space_grid_analytics(self):

        # create two grids
        grid_name_1 = "10 Mile Squares"
        grid_name_2 = "20 Mile Squares"
        grid_threshold_1 = "SquareMiles10"
        grid_threshold_2 = "SquareMiles20"
        grid_id_1 = insert_test_white_space_grid(grid_threshold_1, grid_name_1)
        grid_id_2 = insert_test_white_space_grid(grid_threshold_2, grid_name_2)

        # opening dates helpers (relative to the global last analytics date)
        recent_date = get_start_date_of_previous_month(LAST_ANALYTICS_DATE)
        one_year_ago_first_day = get_first_day_of_month_one_year_ago(LAST_ANALYTICS_DATE)
        old_date = one_year_ago_first_day - timedelta(days = 1)
        after_last_analytics_date = LAST_ANALYTICS_DATE + timedelta(days=60)

        # create three cells within the first grid
        grid_cell_1_id = insert_test_white_space_grid_cell(grid_id_1, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], grid_threshold_1, grid_name_1, 0.5, 0.5)
        grid_cell_2_id = insert_test_white_space_grid_cell(grid_id_1, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], grid_threshold_1, grid_name_1, 1.5, 1.5)
        grid_cell_3_id = insert_test_white_space_grid_cell(grid_id_1, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], grid_threshold_1, grid_name_1, 2.5, 2.5)

        # create one cell within the second grid that encompasses all of the first grid's cells
        grid_cell_4_id = insert_test_white_space_grid_cell(grid_id_2, [[[3, 3], [0, 3], [0, 0], [3, 0], [3, 3]]], grid_threshold_2, grid_name_2, 1.5, 1.5)

        # insert two companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()

        # create four stores, 3 for company 1, and 1 for company 2.  With different dates.
        store_id_1 = insert_test_store(company_id_1, [recent_date, None])
        store_id_2 = insert_test_store(company_id_1, None)
        store_id_3 = insert_test_store(company_id_1, [old_date, None])
        store_id_4 = insert_test_store(company_id_2, [one_year_ago_first_day, None])

        # insert a trade area per store.  store1, store2, store4 will be within grid1.  store3 will be within grid2.
        # grid 3 is empty and grid 4 will encompass all stores.
        trade_area_id_1 = insert_test_trade_area(store_id_1, company_id_1, longitude=0.5, latitude=0.5)
        trade_area_id_2 = insert_test_trade_area(store_id_2, company_id_1, longitude=0.4, latitude=0.4)
        trade_area_id_3 = insert_test_trade_area(store_id_3, company_id_1, longitude=1.5, latitude=1.5)
        trade_area_id_4 = insert_test_trade_area(store_id_4, company_id_2, longitude=0.1, latitude=0.1)

        # run gp14 on all four trade areas
        gp = GP14CoreWhitespaceCompetition()
        gp.process_object(select_trade_area(trade_area_id_1))
        gp.process_object(select_trade_area(trade_area_id_2))
        gp.process_object(select_trade_area(trade_area_id_3))
        gp.process_object(select_trade_area(trade_area_id_4))

        # run analytics on all the grids in the db (everything synchronous)
        self.main_access.call_run_white_space_analytics(True, False)

        # select all the currently existing cell matches and get array of it's data
        cell_matches = select_all_white_space_grid_cell_matches()
        cell_matches = [match["data"] for match in cell_matches]

        # verify that the cell matches are correct
        self.test_case.assertEqual(sorted(cell_matches), sorted([
            self._create_cell_match_record(grid_cell_1_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_1, 2, True),
            self._create_cell_match_record(grid_cell_1_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_2, 1, True),
            self._create_cell_match_record(grid_cell_2_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_1, 1, False),
            self._create_cell_match_record(grid_cell_4_id, grid_id_2, grid_name_2, grid_threshold_2, company_id_1, 3, True),
            self._create_cell_match_record(grid_cell_4_id, grid_id_2, grid_name_2, grid_threshold_2, company_id_2, 1, True)
        ]))

        #!!!!!!!!!!!!! UPDATE - close a store, add a new store, add a new company, verify all is still good.

        # close store1
        query = {"_id": store_id_1}
        update = {"$set": {"interval": [None, datetime.datetime(2012, 1, 1)]}}
        self.main_access.mds.call_batch_update_entities("store", query, update, self.context)

        # update store 3 to close after the analytics date, and verify that it shows as still open (because everything is relative to the last analytics date)
        query = {"_id": store_id_3}
        update = {"$set": {"interval": [None, after_last_analytics_date]}}
        self.main_access.mds.call_batch_update_entities("store", query, update, self.context)

        # add a new store to company 2, in grid 1, and geoprocess it
        store_id_5 = insert_test_store(company_id_2, None)
        trade_area_id_5 = insert_test_trade_area(store_id_5, company_id_2, longitude=0.1, latitude=0.1)
        gp.process_object(select_trade_area(trade_area_id_5))

        # create company 3, a new store for it, in grid 1, and geoprocess it
        company_id_3 = insert_test_company()
        store_id_6 = insert_test_store(company_id_3, None)
        trade_area_id_6 = insert_test_trade_area(store_id_6, company_id_3, longitude=0.1, latitude=0.1)
        gp.process_object(select_trade_area(trade_area_id_6))

        # run analytics again
        self.main_access.call_run_white_space_analytics(True, False)

        # select all the currently existing cell matches and get array of it's data
        cell_matches = select_all_white_space_grid_cell_matches()
        cell_matches = [match["data"] for match in cell_matches]

        expected = [
            self._create_cell_match_record(grid_cell_1_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_1, 1, False),
            self._create_cell_match_record(grid_cell_1_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_2, 2, True),
            self._create_cell_match_record(grid_cell_1_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_3, 1, False),
            self._create_cell_match_record(grid_cell_2_id, grid_id_1, grid_name_1, grid_threshold_1, company_id_1, 1, False),
            self._create_cell_match_record(grid_cell_4_id, grid_id_2, grid_name_2, grid_threshold_2, company_id_1, 2, False),
            self._create_cell_match_record(grid_cell_4_id, grid_id_2, grid_name_2, grid_threshold_2, company_id_2, 2, True),
            self._create_cell_match_record(grid_cell_4_id, grid_id_2, grid_name_2, grid_threshold_2, company_id_3, 1, False)
        ]

        # verify that the changes are correct
        self.test_case.assertEqual(sorted(cell_matches), sorted(expected))

    # ------------------------------------ Private helpers ------------------------------------

    def _create_cell_match_record(self, cell_id, grid_id, grid_name, threshold, company_id, store_count, has_openings):
        return {
            "cell_id": cell_id,
            "grid_id": grid_id,
            "grid_name": grid_name,
            "threshold": threshold,
            "company_id": company_id,
            "store_count": store_count,
            "has_openings": has_openings
        }
