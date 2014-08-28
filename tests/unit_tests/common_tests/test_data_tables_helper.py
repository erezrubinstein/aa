from common.web_helpers.jquery_data_tables_helper import create_data_tables_json, jquery_data_grids_parameters

__author__ = 'erezrubinstein'

import unittest

class DataTablesHelperTests(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.get_data_method = lambda (item): item

    def test_create_data_tables_json(self):
        # jsonify!
        json = create_data_tables_json(self.data, self.get_data_method, 1, 0, 3, "", True)

        # set up expected json and verify they match
        expected_json = "{\"aaData\": [15, 14, 13], \"iTotalRecords\": 15, \"sEcho\": 2, \"iTotalDisplayRecords\": 15}"
        self.assertEqual(json, expected_json)


    def test_jquery_data_grids_parameters_class(self):
        # create args
        args = {
            "sEcho" : "2",
            "iSortCol_0" : "2",
            "sSortDir_0" : "asc",
            "iDisplayStart" : "4",
            "iDisplayLength" : "2"
        }

        # parse args
        params = jquery_data_grids_parameters(args)

        # verify results
        self.assertEqual(params.draw_count, 2)
        self.assertEqual(len(params.sorted_column), 1)
        self.assertEqual(params.sorted_column[2], "asc")
        self.assertEqual(params.page, 2)
        self.assertEqual(params.page_size, 2)



if __name__ == '__main__':
    unittest.main()
