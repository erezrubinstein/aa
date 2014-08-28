from core.common.business_logic.service_entity_logic.white_space_grid_helper import select_grid_cell_by_lat_long
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_white_space_grid, insert_test_white_space_grid_cell

__author__ = 'erezrubinstein'

class WhiteSpaceHelperTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "gp_14_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        # delete when starting
        self.mds_access.call_delete_reset_database()

        # create a base grid
        self.grid_name = "10 Mile Squares"
        self.grid_threshold = "GridDistanceMiles10"
        self.grid_id = insert_test_white_space_grid(self.grid_threshold, self.grid_name)

    def tearDown(self):
        pass

    # -------------------------------------- Begin Testing!! --------------------------------------

    def test_select_grid_cells_by_lat_long(self):

        # create three 10 mile grid cells.  cell 1 and 2 intersect.  cell 3 is very different
        grid_cell_1_id = ensure_id(insert_test_white_space_grid_cell(str(self.grid_id), [[[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]], self.grid_threshold, self.grid_name))
        grid_cell_2_id = ensure_id(insert_test_white_space_grid_cell(str(self.grid_id), [[[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]], self.grid_threshold, self.grid_name))
        grid_cell_3_id = ensure_id(insert_test_white_space_grid_cell(str(self.grid_id), [[[5, 5], [4, 5], [4, 4], [5, 4], [5, 5]]], self.grid_threshold, self.grid_name))

        # find the match for the first threshold
        grid_match = select_grid_cell_by_lat_long(.3, .3, self.grid_threshold)

        # make sure only the first 2 grids match
        self.test_case.assertEqual(grid_match, { "_id": grid_cell_1_id, "data": { "grid_id": str(self.grid_id), "threshold": self.grid_threshold, "grid_name": self.grid_name }})

        # create one more grid and one more cell that intersects the point, but in a separate grid
        second_grid_id = insert_test_white_space_grid("GridDistanceMiles50", "50 Mile Squares")
        grid_cell_4_id = ensure_id(insert_test_white_space_grid_cell(str(second_grid_id), [[[10, 10], [0, 10], [0, 0], [10, 0], [10, 10]]], "GridDistanceMiles50", "50 Mile Squares"))

        # find the match for the first threshold
        grid_match = select_grid_cell_by_lat_long(.3, .3, "GridDistanceMiles50")

        # make sure only the first 2 grids match
        self.test_case.assertEqual(grid_match, { "_id": grid_cell_4_id, "data": { "grid_id": str(second_grid_id), "threshold": "GridDistanceMiles50", "grid_name": "50 Mile Squares" }})
