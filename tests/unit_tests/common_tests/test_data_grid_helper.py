from collections import namedtuple
from common.web_helpers.data_grid_helper import page_data, sort_data

__author__ = 'erezrubinstein'

import unittest

class DataGridHelperTests(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def test_paging__less_items_than_page_size(self):
        paged_data = page_data(self.data, 0, len(self.data))
        self.assertEqual(paged_data, self.data)


    def test_paging__first_page(self):
        paged_data = page_data(self.data, 0, 3)

        # make sure right items were returned
        self.assertEqual(len(paged_data), 3)
        self.assertEqual(paged_data[0], 1)
        self.assertEqual(paged_data[1], 2)
        self.assertEqual(paged_data[2], 3)


    def test_paging__middle_page(self):
        paged_data = page_data(self.data, 1, 3)

        # make sure right items were returned
        self.assertEqual(len(paged_data), 3)
        self.assertEqual(paged_data[0], 4)
        self.assertEqual(paged_data[1], 5)
        self.assertEqual(paged_data[2], 6)


    def test_paging__last_page__less_items_left(self):
        paged_data = page_data(self.data, 1, 13)

        # make sure right items were returned
        self.assertEqual(len(paged_data), 2)
        self.assertEqual(paged_data[0], 14)
        self.assertEqual(paged_data[1], 15)


    def test_sorting__simple__ascending(self):
        # sort ascending
        data = [3, 1, 2]
        sorted_data = sort_data(data, "")

        self.assertEqual(sorted_data, [1, 2, 3])


    def test_sorting__simple__descending(self):
        # sort descending
        data = [3, 1, 2]
        sorted_data = sort_data(data, "", True)

        self.assertEqual(sorted_data, [3, 2, 1])


    def test_sorting__complex__ascending(self):
        # create named tuple
        point = namedtuple("point", "x y")
        data = [point(1, 3), point(2, 1), point(3, 2)]

        # sort ascending
        sorted_data = sort_data(data, "y")

        self.assertEqual(sorted_data, [point(2, 1), point(3, 2), point(1, 3)])


    def test_sorting__complex__descending(self):
        # create named tuple
        point = namedtuple("point", "x y")
        data = [point(1, 3), point(2, 1), point(3, 2)]

        # sort descending
        sorted_data = sort_data(data, "y", True)

        self.assertEqual(sorted_data, [point(1, 3), point(3, 2), point(2, 1)])


if __name__ == '__main__':
    unittest.main()
