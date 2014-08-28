from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_geoprocessed_trade_area, insert_test_white_space_grid, insert_test_white_space_grid_cell
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency


__author__ = 'vgold'


class RetailWhiteSpaceTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Retail Web Company Tests ---------------------------------------##

    def test_retail_get_whitespace_stores(self):

        main_access = Dependency("CoreAPIProvider").value
        company_id = insert_test_company()

        trade_area_1 = insert_test_geoprocessed_trade_area(home_store_id=1, away_store_id=21, company_id=company_id,
                                                           company_name="woot", opened_date=None, closed_date=None,
                                                           longitude=35, latitude=-40)
        trade_area_2 = insert_test_geoprocessed_trade_area(home_store_id=2, away_store_id=22, company_id=company_id,
                                                           company_name="woot", opened_date=None, closed_date=None,
                                                           longitude=36, latitude=-41)
        trade_area_3 = insert_test_geoprocessed_trade_area(home_store_id=3, away_store_id=23, company_id=999,
                                                           company_name="woot", opened_date=None, closed_date=None,
                                                           longitude=37, latitude=-42)

        params = {
            "bannerIds": [company_id]
        }
        context = {}
        resource = "/data/preset/whitespace/stores"

        data = main_access.call_get_preset(resource, params=params, context=context)
        stores = data["stores"]

        self.test_case.assertEqual(len(stores), 2)
        self.test_case.assertItemsEqual(stores[0][-6], [35, -40])
        self.test_case.assertItemsEqual(stores[1][-6], [36, -41])

    def test_retail_get_whitespace_grid(self):

        main_access = Dependency("CoreAPIProvider").value

        grid_name = "Grid 100 mile x 100 mile"
        threshold = "GridDistanceMiles100"
        grid_id = insert_test_white_space_grid(threshold, grid_name)

        another_grid_name = "Random Grid 7 mile x 7 mile"
        another_threshold = "GridDistanceMiles7"
        another_grid_id = insert_test_white_space_grid(threshold, another_grid_name)

        grid_cell_1_poly = [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
        grid_cell_2_poly = [[[1, 0], [1, 1], [2, 1], [2, 0], [1, 0]]]
        grid_cell_3_poly = [[[0, 1], [0, 2], [1, 2], [1, 1], [0, 1]]]
        grid_cell_4_poly = [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]

        grid_cell_1_id = insert_test_white_space_grid_cell(grid_id, grid_cell_1_poly, threshold, grid_name, 0.5, 0.5)
        grid_cell_2_id = insert_test_white_space_grid_cell(grid_id, grid_cell_2_poly, threshold, grid_name, 1.5, 0.5)
        grid_cell_3_id = insert_test_white_space_grid_cell(grid_id, grid_cell_3_poly, threshold, grid_name, 0.5, 1.5)
        grid_cell_4_id = insert_test_white_space_grid_cell(another_grid_id, grid_cell_4_poly, another_threshold,
                                                           another_grid_name, 1.5, 1.5)

        context = {}
        params = {}

        resource = "/data/preset/whitespace/grid/%s" % threshold
        data = main_access.call_get_preset(resource, params=params, context=context)
        grid_cells = data["grid_cells"]

        grid_cells_dict = {}
        for grid_cell in grid_cells:
            grid_cells_dict[grid_cell[0]] = grid_cell[1]

        self.test_case.assertEqual(len(grid_cells), 3)
        self.test_case.assertItemsEqual(grid_cells_dict[grid_cell_1_id], grid_cell_1_poly)
        self.test_case.assertItemsEqual(grid_cells_dict[grid_cell_2_id], grid_cell_2_poly)
        self.test_case.assertItemsEqual(grid_cells_dict[grid_cell_3_id], grid_cell_3_poly)

        is_grid_cell_4_returned = grid_cell_4_id in grid_cells_dict.keys()
        self.test_case.assertEqual(is_grid_cell_4_returned, False)
