import unittest
from common.service_access.utilities.rec_helpers import *

__author__ = 'jsternberg'

class RecHelperTests(unittest.TestCase):


    ## ---------------------------------------- main get / set with dot notation ------------------------------------- ##

    def test_get_rec_field_basic(self):

        rec = {"a":{"b":1}}
        value = get_rec_field(rec, "a.b")
        self.assertEqual(value, 1)

    def test_set_rec_field_basic(self):

        rec = {"a":{"b":1}}
        old_value = set_rec_field(rec, "a.b", 2)
        self.assertEqual(rec, {"a":{"b":2}})
        self.assertEqual(old_value, 1)

    ## ------------------------------------------------ transformations ---------------------------------------------- ##

    # TODO: implement rec helper transformation unit tests

    ## ------------------------------------------------ validations -------------------------------------------------- ##

    # TODO: implement rec helper validations unit tests

    ## ------------------------------------------------ matching helpers --------------------------------------------- ##

    def test_get_field_value_match(self):

        rec = {"a":{"b":1}}

        match = get_field_value_match(rec, "a.b", 1)
        self.assertTrue(match)

        match = get_field_value_match(rec, "a.b", "spam")
        self.assertFalse(match)

        match = get_field_value_match(rec, "a.b", 2)
        self.assertFalse(match)

    def test_all_field_values_match(self):

        rec = {"a":{"b":1}, "c":{"d":2}}

        # as dict
        match = all_field_values_match(rec, {"a.b":1, "c.d":2})
        self.assertTrue(match)

        match = all_field_values_match(rec, {"a.b":1, "c.d":"spam"})
        self.assertFalse(match)

        # as list
        match = all_field_values_match(rec, [{"a.b":1}, {"c.d":2}])
        self.assertTrue(match)

        match = all_field_values_match(rec, [{"a.b":1}, {"c.d":"spam"}])
        self.assertFalse(match)

    def test_any_field_values_match(self):

        rec = {"a":{"b":1}, "c":{"d":2}}

        # as dict
        match = any_field_values_match(rec, {"a.b":1, "c.d":2})
        self.assertTrue(match)

        match = any_field_values_match(rec, {"a.b":1, "c.d":"spam"})
        self.assertTrue(match)

        match = any_field_values_match(rec, {"a.b":"ham", "c.d":"spam"})
        self.assertFalse(match)

        # as list
        match = any_field_values_match(rec, [{"a.b":1}, {"c.d":2}])
        self.assertTrue(match)

        match = any_field_values_match(rec, [{"a.b":1}, {"c.d":"spam"}])
        self.assertTrue(match)

        match = any_field_values_match(rec, [{"a.b":"ham"}, {"c.d":"spam"}])
        self.assertFalse(match)

    def test_no_field_values_match(self):

        rec = {"a":{"b":1}, "c":{"d":2}}

        # as dict
        match = no_field_values_match(rec, {"a.b":1, "c.d":2})
        self.assertFalse(match)

        match = no_field_values_match(rec, {"a.b":1, "c.d":"spam"})
        self.assertFalse(match)

        match = no_field_values_match(rec, {"a.b":"ham", "c.d":"spam"})
        self.assertTrue(match)

        # as list
        match = no_field_values_match(rec, [{"a.b":1}, {"c.d":2}])
        self.assertFalse(match)

        match = no_field_values_match(rec, [{"a.b":1}, {"c.d":"spam"}])
        self.assertFalse(match)

        match = no_field_values_match(rec, [{"a.b":"ham"}, {"c.d":"spam"}])
        self.assertTrue(match)


if __name__ == '__main__':
    unittest.main()
