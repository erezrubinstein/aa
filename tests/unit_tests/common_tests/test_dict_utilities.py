from common.utilities.dict_utilities import get_by_dot_notation, set_by_dot_notation

__author__ = 'imashhor'

import unittest


class DictUtilitiesTests(unittest.TestCase):
    def test_get_by_dot_notation__sub_elements(self):
        test_dict = {
            "sub1": {
                "sub2": {
                    "sub3": "hello"
                }
            }
        }

        self.assertEqual({"sub3": "hello"}, get_by_dot_notation(test_dict, "sub1.sub2"))
        self.assertEqual("hello", get_by_dot_notation(test_dict, "sub1.sub2.sub3"))

    def test_get_by_dot_notation__defaults(self):
        test_dict = {
            "sub1": {
                "sub2": {
                    "sub3": "hello"
                }
            }
        }

        self.assertEqual(None, get_by_dot_notation(test_dict, "xxx"))
        self.assertEqual(10, get_by_dot_notation(test_dict, "sub1.subxx", 10))


    def test_set_by_dot_notation__one_level(self):
        expected = { "foo" : "bar" }
        self.assertEqual(expected, set_by_dot_notation({}, "foo", "bar"))

    def test_set_by_dot_notation__multi_level_recursive(self):
        expected = { "foo" : { "bar" : { "chicken" : "woot" } } }
        self.assertEqual(expected, set_by_dot_notation({}, "foo.bar.chicken", "woot"))

    def test_set_by_dot_notation__multi_level_nonrecursive(self):
        self.assertEqual({}, set_by_dot_notation({}, "foo.bar.chicken", "woot", False))

