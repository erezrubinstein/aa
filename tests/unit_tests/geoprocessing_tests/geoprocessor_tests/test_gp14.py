import mox
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import white_space_grid_helper
from geoprocessing.geoprocessors.white_space.gp14_core_whitespace_competition import GP14CoreWhitespaceCompetition
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies

__author__ = 'erezrubinstein'

class GP14Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP14Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # create the mock trade _area
        self.trade_area_id = 11
        self.store_id = "woot!"
        self.trade_area = {
            "_id" : self.trade_area_id,
            "data" : {
                "store_id": self.store_id,
                "company_id": "buddy!",
                "latitude" : 1,
                "longitude" : -1
            }
        }

        # create the test gp
        self.gp = GP14CoreWhitespaceCompetition()


    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(GP14Tests, self).doCleanups()
        dependencies.clear()


    def test_gp_14_complete_run(self):
        """
        GP14 is very simple.  Given that, we'll just test the entire run.
        """

        # create mock_grids
        mock_grids = [
            { "data": { "threshold": "bobby", "grid_id": 1 }},
            { "data": { "threshold": "boucher", "grid_id": 2 }}
        ]

        # create mock cell matches (3 responses - 2 in unique grids and one duplicate)
        mock_cell_match_1 = {"_id": 1, "data": { "threshold": "bobby", "grid_id": "chicken", "grid_name": "woot" }}
        mock_cell_match_2 = { "_id": 3, "data": { "threshold": "boucher", "grid_id": "chilly", "grid_name": "willy" }}

        # mock update query and update_operation
        mock_update_query = { "_id": self.store_id }
        mock_update_operation = {
            "$set": {
                "data.white_space_cell_matches": {
                    "bobby": {
                        "cell_id": "1",
                        "grid_id": "chicken",
                        "grid_name": "woot"
                    },
                    "boucher": {
                        "cell_id": "3",
                        "grid_id": "chilly",
                        "grid_name": "willy"
                    }
                }
            }
        }

        # stub out various methods
        self.mox.StubOutWithMock(white_space_grid_helper, "select_grid_thresholds")
        self.mox.StubOutWithMock(white_space_grid_helper, "select_grid_cell_by_lat_long")

        # begin recording
        white_space_grid_helper.select_grid_thresholds().AndReturn(mock_grids)
        white_space_grid_helper.select_grid_cell_by_lat_long(1, -1, "bobby").AndReturn(mock_cell_match_1)
        white_space_grid_helper.select_grid_cell_by_lat_long(1, -1, "boucher").AndReturn(mock_cell_match_2)
        self.mock_main_access.mds.call_batch_update_entities("store", mock_update_query, mock_update_operation, self.gp.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp.process_object(self.trade_area)
        