from datetime import datetime
from common.utilities.date_utilities import get_later_date, get_earlier_date, get_start_date_of_previous_month, \
                                            get_first_day_of_month, get_months_difference

__author__ = 'erezrubinstein'

import unittest

class DateUtilitiesTests(unittest.TestCase):
    """
    These are tests for the common.utilities.date_utilities module
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass


    ############################################################ get_later_date tests ############################################################
    def test_get_later_date_date1_larger(self):
        date1 = "2012-01-02"
        date2 = "2012-01-01"

        # make sure date1 is returned
        larger_date = get_later_date(date1, date2)
        self.assertEqual(larger_date, self.__convert_str(date1))

    def test_get_later_date_date2_larger(self):
        date1 = "2012-01-01"
        date2 = "2012-01-02"

        # make sure date2 is returned
        larger_date = get_later_date(date1, date2)
        self.assertEqual(larger_date, self.__convert_str(date2))

    def test_get_later_date_date1_is_null(self):
        date1 = None
        date2 = "2012-01-02"

        # make sure date2 is returned
        larger_date = get_later_date(date1, date2)
        self.assertEqual(larger_date, self.__convert_str(date2))

    def test_get_later_date_date2_is_null(self):
        date1 = "2012-01-01"
        date2 = None

        # make sure date1 is returned
        larger_date = get_later_date(date1, date2)
        self.assertEqual(larger_date, self.__convert_str(date1))

    def test_get_later_date_both_dates_are_null(self):
        date1 = None
        date2 = None

        # make sure date1 is returned
        larger_date = get_later_date(date1, date2)
        self.assertIsNone(larger_date)


    ############################################################ get_earlier_date tests ############################################################
    def test_get_earlier_date_date1_earlier(self):
        date1 = "2012-01-01"
        date2 = "2012-01-02"

        # make sure date1 is returned
        earlier_date = get_earlier_date(date1, date2)
        self.assertEqual(earlier_date, self.__convert_str(date1))

    def test_get_earlier_date_date2_earlier(self):
        date1 = "2012-01-02"
        date2 = "2012-01-01"

        # make sure date2 is returned
        earlier_date = get_earlier_date(date1, date2)
        self.assertEqual(earlier_date, self.__convert_str(date2))

    def test_get_earlier_date_date1_is_null(self):
        date1 = None
        date2 = "2012-01-02"

        # make sure date2 is returned
        earlier_date = get_earlier_date(date1, date2)
        self.assertEqual(earlier_date, self.__convert_str(date2))

    def test_get_earlier_date_date2_is_null(self):
        date1 = "2012-01-01"
        date2 = None

        # make sure date1 is returned
        earlier_date = get_earlier_date(date1, date2)
        self.assertEqual(earlier_date, self.__convert_str(date1))

    def test_get_earlier_date_both_dates_are_null(self):
        date1 = None
        date2 = None

        # make sure date1 is returned
        earlier_date = get_earlier_date(date1, date2)
        self.assertIsNone(earlier_date)

    # This is for the "get_last_date_of_previous_month" method in the same file
    def test_get_start_date_of_previous_month(self):

        result = get_start_date_of_previous_month(datetime(2012, 1, 15))
        self.assertEqual(datetime(2011, 12, 01), result)

    def test_get_first_day_of_month(self):
        result = get_first_day_of_month(datetime(2012, 1, 15))

        self.assertEqual(datetime(2012, 1, 1), result)

    def __convert_str(self, date):
        return datetime.strptime(date, '%Y-%m-%d')


    def test_get_months_difference_basic(self):

        result = get_months_difference("2013-06-07", "2013-12-15")
        self.assertEqual(result, 6)

    def test_get_months_difference_multi_year(self):

        result = get_months_difference("2013-06-07", "2014-12-15")
        self.assertEqual(result, 18)

    def test_get_months_difference_nones(self):

        result = get_months_difference(None, None)
        self.assertEqual(result, 0)

    def test_get_months_difference_wrong_order(self):

        with self.assertRaises(ValueError):
            result = get_months_difference("2013-12-15", "2012-06-07")
