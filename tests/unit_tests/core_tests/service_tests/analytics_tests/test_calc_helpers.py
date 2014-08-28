from core.service.svc_analytics.implementation.calc.calc_helpers import aggregate_list, get_median_of_list, get_average_of_list, get_min_of_list, get_max_of_list
from common.service_access.utilities.errors import ServiceCallError
import numpy as np
import unittest

__author__ = 'imashhor'

class CalcHelpersTests(unittest.TestCase):

    def test_get_median_of_list_odd(self):
        self.assertEqual(4.5, get_median_of_list([2.2, 5., 6, 4.5, 6, 2.2, 3.2]))

    def test_get_median_of_list_even(self):
        self.assertEqual(4.75, get_median_of_list([2.2, 5., 6, 4.5, 6, 2.2]))

    def test_get_median_of_list_none(self):
        self.assertEqual(4.75, get_median_of_list([None, None, 2.2, 5., 6, None, 4.5, 6, 2.2, None]))

    def test_get_min_of_list(self):
        self.assertEqual(1.23, get_min_of_list([12.3, 3.21, 1.6, 1.23, 1.56]))

    def test_get_min_of_list_none(self):
        self.assertEqual(1.23, get_min_of_list([12.3, 3.21, None, 1.6, 1.23, 1.56, None]))

    def test_get_max_of_list(self):
        self.assertEqual(12.3, get_max_of_list([12.3, 3.21, 1.6, 1.23, 1.56]))

    def test_get_max_of_list_none(self):
        self.assertEqual(12.3, get_max_of_list([12.3, 3.21, None, 1.6, 1.23, 1.56, None]))

    def test_get_average_of_list(self):
        self.assertAlmostEqual(3.97, get_average_of_list([12.3, 3.21, 1.6, 1.23, 1.51]), 2)

    def test_get_average_of_list_none(self):
        self.assertAlmostEqual(3.97, get_average_of_list([12.3, None, None, 3.21, 1.6, 1.23, 1.51]), 2)

    def test_aggregate_list_median(self):
        self.assertEqual(4.75, aggregate_list("median", [None, None, 2.2, 5., 6, None, 4.5, 6, 2.2, None]))

    def test_aggregate_list_min(self):
        self.assertEqual(1.23, aggregate_list("min", [12.3, 3.21, None, 1.6, 1.23, 1.56, None]))

    def test_aggregate_list_min_all_none(self):
        self.assertEqual(None, aggregate_list("min", [None, None, None]))

    def test_aggregate_list_max(self):
        self.assertEqual(12.3, aggregate_list("max", [12.3, 3.21, None, 1.6, 1.23, 1.56, None]))

    def test_aggregate_list_average(self):
        self.assertAlmostEqual(3.97, aggregate_list("average", [12.3, None, None, 3.21, 1.6, 1.23, 1.51]), 2)

    def test_aggregate_list_mean(self):
        self.assertAlmostEqual(3.97, aggregate_list("mean", [12.3, None, None, 3.21, 1.6, 1.23, 1.51]), 2)

    def test_aggregate_list_unsupported(self):
        self.assertRaises(ServiceCallError, aggregate_list, "reimann_zeta", [2, 2, None])

    def test_aggregate_list_all_none(self):
        for func in ["median", "min", "max", "average", "mean", "sum", "variance"]:
            self.assertEqual(None, aggregate_list(func, [None, None, None]))

        self.assertEqual([], aggregate_list("raw", [None, None, None]))


    # -- numpy tests --- #

    def test_aggregate_list_np_median(self):
        self.assertEqual(4.75, aggregate_list("median", np.array([None, None, 2.2, 5., 6, None, 4.5, 6, 2.2, None], float)))

    def test_aggregate_list_np_min(self):
        self.assertEqual(1.23, aggregate_list("min", np.array([12.3, 3.21, None, 1.6, 1.23, 1.56, None], float)))

    def test_aggregate_list_np_max(self):
        self.assertEqual(12.3, aggregate_list("max", np.array([12.3, 3.21, None, 1.6, 1.23, 1.56, None], float)))

    def test_aggregate_list_np_average(self):
        self.assertAlmostEqual(3.97, aggregate_list("average", np.array([12.3, None, None, 3.21, 1.6, 1.23, 1.51], float)), 2)

    def test_aggregate_list_np_mean(self):
        self.assertAlmostEqual(3.97, aggregate_list("mean", np.array([12.3, None, None, 3.21, 1.6, 1.23, 1.51], float)), 2)


    def test_aggregate_list_np_all_none(self):
        for func in ["median", "min", "max", "average", "mean", "sum", "variance"]:
            self.assertEqual(None, aggregate_list(func, np.array([None, None, None], float)))

    def test_aggregate_list_np_all_none_raw(self):
        self.assertEqual([], aggregate_list("raw", np.array([None, None, None])))

    def test_aggregate_list_np_all_none_raw_float(self):
        nones_float = aggregate_list("raw", np.array([None, None, None], float))
        np.testing.assert_array_equal(nones_float, np.array([np.nan, np.nan, np.nan]))


if __name__ == '__main__':
    unittest.main()