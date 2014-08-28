from geoprocessing.geoprocessors.white_space.gp14_core_whitespace_competition import GP14CoreWhitespaceCompetition
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area, select_trade_area, insert_test_white_space_grid, insert_test_white_space_grid_cell, insert_test_store, select_test_store

__author__ = 'erezrubinstein'

class GP14TestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "gp_14_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        # create a base grid
        self.grid_name = "10 Mile Squares"
        self.grid_threshold = "GridDistanceMiles10"
        self.grid_id = insert_test_white_space_grid(self.grid_threshold, self.grid_name)

    def tearDown(self):

        # delete when ending
        self.mds_access.call_delete_reset_database()



    # -------------------------------------- Begin Testing!! --------------------------------------

    def test_simple_with_exact_match(self):

        # insert 4 grid cells
        grid_cell_1_id = insert_test_white_space_grid_cell(self.grid_id, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], self.grid_threshold, self.grid_name, .5, .5)
        grid_cell_2_id = insert_test_white_space_grid_cell(self.grid_id, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], self.grid_threshold, self.grid_name, 1.5, 1.5)
        grid_cell_3_id = insert_test_white_space_grid_cell(self.grid_id, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], self.grid_threshold, self.grid_name, 2.5, 2.5)
        grid_cell_4_id = insert_test_white_space_grid_cell(self.grid_id, [[[4, 4], [3, 4], [3, 3], [4, 3], [4, 4]]], self.grid_threshold, self.grid_name, 3.5, 3.5)

        # create a second grid and insert the same four cells
        second_grid_name = "20 Mile Squares"
        second_grid_threshold = "GridDistanceMiles20"
        second_grid_id = insert_test_white_space_grid(second_grid_threshold, second_grid_name)
        second_grid_cell_1_id = insert_test_white_space_grid_cell(second_grid_id, [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], second_grid_threshold, second_grid_name, .5, .5)
        second_grid_cell_2_id = insert_test_white_space_grid_cell(second_grid_id, [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], second_grid_threshold, second_grid_name, 1.5, 1.5)
        second_grid_cell_3_id = insert_test_white_space_grid_cell(second_grid_id, [[[3, 3], [2, 3], [2, 2], [3, 2], [3, 3]]], second_grid_threshold, second_grid_name, 2.5, 2.5)
        second_grid_cell_4_id = insert_test_white_space_grid_cell(second_grid_id, [[[4, 4], [3, 4], [3, 3], [4, 3], [4, 4]]], second_grid_threshold, second_grid_name, 3.5, 3.5)

        # create a trade area within the NYC coordinates (4th quadrant)
        store_id = insert_test_store(1, None)
        trade_area_id = insert_test_trade_area(store_id, 1, latitude = 3.9, longitude = 3.9)
        trade_area_document = select_trade_area(trade_area_id)
        
        # run gp 14 on this trade area
        GP14CoreWhitespaceCompetition().process_object(trade_area_document)

        # select the store
        store = select_test_store(store_id)

        # verify that the correct matches were made
        self.test_case.assertEqual(store["data"]["white_space_cell_matches"], {
                self.grid_threshold: {
                    "cell_id": grid_cell_4_id,
                    "grid_id": self.grid_id,
                    "grid_name": self.grid_name
                },
                second_grid_threshold: {
                    "cell_id": second_grid_cell_4_id,
                    "grid_id": second_grid_id,
                    "grid_name": second_grid_name
                }
            }
        )




    # ------------------------------------------ Helpers -----------------------------------------

    def _create_nyc_square(self, quadrant):
        # returns four squares around a section of manhattan.
        # you can request one of the below quadrants
        #   --- ---
        #  | 1 | 2 |
        #   --- ---
        #  | 3 | 4 |
        #   --- ---

        # create some random base manhattan coordinates
        lng = -74
        lat = 40.74

        # add subtract 0.5 degrees
        diff = 0.5

        if quadrant == 1:
            return [[[lng, lat], [lng - diff, lat], [lng - diff, lat + diff], [lng, lat + diff], [lng, lat]]]

        elif quadrant == 2:
            return [[[lng, lat], [lng + diff, lat], [lng + diff, lat + diff], [lng, lat + diff], [lng, lat]]]

        elif quadrant == 3:
            return [[[lng, lat], [lng - diff, lat], [lng - diff, lat - diff], [lng, lat - diff], [lng, lat]]]

        # assume 4th quadrant
        else:
            return [[[lng, lat], [lng + diff, lat], [lng + diff, lat - diff], [lng, lat - diff], [lng, lat]]]