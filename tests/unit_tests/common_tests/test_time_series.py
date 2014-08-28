# coding=utf-8
import unittest
from datetime import datetime
from common.utilities.date_utilities import FastDateParser
from common.utilities.time_series import scale_to_monthly_start_of_month, filter_values_after_date, \
    get_monthly_time_series, TIME_SERIES_START, get_time_series_value, \
    sort_series_by_date, parse_series_dates, get_time_series_value_from_field, get_time_series_item, expand_monthly_series_start_of_month, get_daily_time_series

__author__ = 'imashhor'


class TimeSeriesTest(unittest.TestCase):

    ## --------------- expand_monthly_series_start_of_month  ---------------##

    def test_expand_monthly_series_start_of_month__should_set_dates_to_start_of_month(self):

        dates = [datetime(2013, 1, 15), datetime(2013, 2, 13), datetime(2013, 3, 26)]

        expected_dates = [
            datetime(2013, 1, 1),
            datetime(2013, 2, 1),
            datetime(2013, 3, 1)
        ]
        actual_dates = expand_monthly_series_start_of_month(dates, False)

        self.assertEqual(expected_dates, actual_dates)

    def test_expand_monthly_series_end_of_month__should_order_descending_by_default(self):

        dates = [
            datetime(2013, 2, 1),
            datetime(2013, 4, 1),
            datetime(2013, 3, 1)
        ]

        expected_dates = [
            datetime(2013, 4, 1),
            datetime(2013, 3, 1),
            datetime(2013, 2, 1)
        ]

        actual_dates = expand_monthly_series_start_of_month(dates)

        self.assertEqual(expected_dates, actual_dates)

    def test_expand_monthly_series_end_of_month__should_take_start_value_of_month(self):

        dates = [
            datetime(2013, 1, 1),
            datetime(2013, 1, 15),
            datetime(2013, 1, 23),
            datetime(2013, 3, 1)
        ]

        expected_dates = [
            datetime(2013, 1, 1),
            datetime(2013, 2, 1),
            datetime(2013, 3, 1)
        ]

        actual_dates = expand_monthly_series_start_of_month(dates, False)

        self.assertEqual(expected_dates, actual_dates)

    def test_expand_monthly_series_end_of_month__should_fill_with_previous_months_value(self):

        dates = [datetime(2013, 2, 1), datetime(2013, 5, 1)]

        expected_dates = [
            datetime(2013, 2, 1),
            datetime(2013, 3, 1),
            datetime(2013, 4, 1),
            datetime(2013, 5, 1)
        ]

        actual_dates = expand_monthly_series_start_of_month(dates, False)

        self.assertEqual(expected_dates, actual_dates)


    def test_expand_monthly_series_end_of_month__should_handle_last_day_of_month(self):

        dates = [datetime(2013, 2, 1), datetime(2013, 5, 1)]

        expected_dates = [
            datetime(2013, 2, 1),
            datetime(2013, 3, 1),
            datetime(2013, 4, 1),
            datetime(2013, 5, 1)
        ]

        actual_dates = expand_monthly_series_start_of_month(dates, False)

        self.assertEqual(expected_dates, actual_dates)

    def test_expand_monthly_series_end_of_month__should_account_for_leap_year(self):

        dates = [datetime(2012, 3, 1)]

        expected_dates = [datetime(2012, 3, 1)]

        actual_dates = expand_monthly_series_start_of_month(dates, False)

        self.assertEqual(expected_dates, actual_dates)

    ## --------------- scale_to_monthly_start_of_month  ---------------##

    def test_scale_to_monthly_start_of_month__should_set_dates_to_start_of_month(self):

        dates = [datetime(2013, 1, 15), datetime(2013, 2, 13), datetime(2013, 3, 26)]
        values = [1., 2., 3.]

        expected_dates = [
            datetime(2013, 1, 1),
            datetime(2013, 2, 1),
            datetime(2013, 3, 1)
        ]
        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values, False)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(values, actual_values)

    def test_scale_to_monthly_end_of_month__should_order_descending_by_default(self):

        dates = [
            datetime(2013, 2, 1),
            datetime(2013, 4, 1),
            datetime(2013, 3, 1)
        ]
        values = [1., 3., 2.]

        expected_dates = [
            datetime(2013, 4, 1),
            datetime(2013, 3, 1),
            datetime(2013, 2, 1)
        ]
        expected_values = [3., 2., 1.]

        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(expected_values, actual_values)

    def test_scale_to_monthly_start_of_month__should_take_start_value_of_month(self):

        dates = [
            datetime(2013, 1, 1),
            datetime(2013, 1, 15),
            datetime(2013, 1, 23),
            datetime(2013, 3, 1)
        ]
        values = [1., 3., 2., 4.]

        expected_dates = [
            datetime(2013, 1, 1),
            datetime(2013, 2, 1),
            datetime(2013, 3, 1)
        ]
        expected_values = [2., 2., 4.]

        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values, False)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(expected_values, actual_values)

    def test_scale_to_monthly_start_of_month__should_fill_with_previous_months_value(self):

        dates = [datetime(2013, 2, 1), datetime(2013, 5, 1)]
        values = [1., 100.]

        expected_dates = [
            datetime(2013, 2, 1),
            datetime(2013, 3, 1),
            datetime(2013, 4, 1),
            datetime(2013, 5, 1)
        ]
        expected_values = [1., 1., 1., 100.]

        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values, False)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(expected_values, actual_values)

    def test_scale_to_monthly_end_of_month__should_handle_last_day_of_month(self):

        dates = [datetime(2013, 2, 1), datetime(2013, 5, 1)]
        values = [1., 100.]

        expected_dates = [
            datetime(2013, 2, 1),
            datetime(2013, 3, 1),
            datetime(2013, 4, 1),
            datetime(2013, 5, 1)
        ]
        expected_values = [1., 1., 1., 100.]

        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values, False)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(expected_values, actual_values)

    def test_scale_to_monthly_start_of_month__should_account_for_leap_year(self):

        dates = [datetime(2012, 3, 1)]
        values = [7.]

        expected_dates = [datetime(2012, 3, 1)]

        (actual_dates, actual_values) = scale_to_monthly_start_of_month(dates, values, False)

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(values, actual_values)

    ## --------------- others  ---------------##

    def test_filter_values_after_date(self):

        dates = [datetime(2013, 1, 13), datetime(2013, 2, 15), datetime(2013, 2, 23), datetime(2013, 2, 28)]
        values = [1., 2., 3., 4.]

        filter_values_after_date(dates, values, datetime(2013, 2, 1))

        self.assertEqual([datetime(2013, 1, 13)], dates)
        self.assertEqual([1.], values)

    def test_get_monthly_time_series(self):

        start = TIME_SERIES_START
        end = datetime(2013, 7, 15, 3, 4, 5)

        actual_dates = get_monthly_time_series(start, end)

        # We should have a date for each month between now and Jan 1, 2011, minus the last month
        expected_count = (end.year - start.year) * 12 + (end.month - start.month) + 1

        # first date should be the last day of the previous month from today
        expected_first_date = datetime(end.year, end.month, 1)

        self.assertEqual(expected_count, len(actual_dates))
        self.assertEqual(datetime(2011, 1, 1), actual_dates[-1])
        self.assertEqual(expected_first_date, actual_dates[0])

    def test_get_monthly_time_series_month_start(self):

        now = datetime.utcnow()
        start = datetime(2009, 1, 25)

        month = now.month
        year = now.year

        expected_end = datetime(year, month, 1)
        actual_dates = get_monthly_time_series(start=start, sort_descending=False)

        # first date should be equal to start
        self.assertEqual(datetime(2009, 1, 1), actual_dates[0])
        self.assertEqual(expected_end, actual_dates[-1])

    def test_get_time_series_value_from_field(self):

        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},
        ]
        entity_rec = {"series": series}
        self.assertEqual(849, get_time_series_value_from_field(entity_rec, "series", datetime(2013, 3, 18, 0, 0)))
        self.assertEqual(194, get_time_series_value_from_field(entity_rec, "series", datetime(2011, 1, 31, 0, 0)))
        self.assertEqual(993, get_time_series_value_from_field(entity_rec, "series", datetime(2011, 6, 3, 0, 0)))
        self.assertEqual(None, get_time_series_value_from_field(entity_rec, "series", datetime(2011, 6, 4, 0, 0)))

    def test_get_time_series_value(self):
        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},
        ]

        self.assertEqual(849, get_time_series_value(series, datetime(2013, 3, 18, 0, 0)))
        self.assertEqual(194, get_time_series_value(series, datetime(2011, 1, 31, 0, 0)))
        self.assertEqual(993, get_time_series_value(series, datetime(2011, 6, 3, 0, 0)))
        self.assertEqual(None, get_time_series_value(series, datetime(2011, 6, 4, 0, 0)))

    def test_get_time_series_item(self):
        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},
        ]

        self.assertEqual({'date': datetime(2013, 3, 18, 0, 0), 'value': 849}, get_time_series_item(series, datetime(2013, 3, 18, 0, 0)))
        self.assertEqual({'date': datetime(2011, 1, 31, 0, 0), 'value': 194}, get_time_series_item(series, datetime(2011, 1, 31, 0, 0)))
        self.assertEqual({'date': datetime(2011, 6, 3, 0, 0), 'value': 993}, get_time_series_item(series, datetime(2011, 6, 3, 0, 0)))
        self.assertEqual(None, get_time_series_item(series, datetime(2011, 6, 4, 0, 0)))

    def test_get_time_series_value_with_parser(self):

        parser = FastDateParser()
        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},

            # these should be memoized, and values ignored since they are duplicates
            {'date': "2011-02-28", 'value': 99999},
            {'date': "2011-02-28", 'value': 999999},
        ]

        self.assertEqual(849, get_time_series_value(series, datetime(2013, 3, 18, 0, 0), parser))
        self.assertEqual(194, get_time_series_value(series, datetime(2011, 1, 31, 0, 0), parser))
        self.assertEqual(993, get_time_series_value(series, datetime(2011, 6, 3, 0, 0), parser))

        # wasn't in the list, so should return None
        self.assertEqual(None, get_time_series_value(series, datetime(2011, 6, 4, 0, 0), parser))

        # we've used 1 unique string date here
        self.assertEqual(1, len(parser.dates))

    def test_get_time_series_item_with_parser(self):

        parser = FastDateParser()
        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},

            # these should be memoized, and values ignored since they are duplicates
            {'date': "2011-02-28", 'value': 99999},
            {'date': "2011-02-28", 'value': 999999},
        ]

        self.assertEqual({'date': datetime(2013, 3, 18, 0, 0), 'value': 849}, get_time_series_item(series, datetime(2013, 3, 18, 0, 0), parser))
        self.assertEqual({'date': datetime(2011, 1, 31, 0, 0), 'value': 194}, get_time_series_item(series, datetime(2011, 1, 31, 0, 0), parser))
        self.assertEqual({'date': datetime(2011, 6, 3, 0, 0), 'value': 993}, get_time_series_item(series, datetime(2011, 6, 3, 0, 0), parser))

        # wasn't in the list, so should return None
        self.assertEqual(None, get_time_series_item(series, datetime(2011, 6, 4, 0, 0), parser))

        # we've used 1 unique string date here
        self.assertEqual(1, len(parser.dates))

    def test_get_daily_time_series(self):

        series = get_daily_time_series(datetime(2013, 1, 1, 12, 18), datetime(2013, 1, 5, 23, 2))
        self.assertEqual(series, [datetime(2013, 1, 5, 0, 0), datetime(2013, 1, 4, 0, 0), datetime(2013, 1, 3, 0, 0), datetime(2013, 1, 2, 0, 0), datetime(2013, 1, 1, 0, 0)])

    def test_get_daily_time_series_not_reverse(self):

        series = get_daily_time_series(datetime(2013, 1, 1, 12, 18), datetime(2013, 1, 5, 23, 2), sort_descending=False)
        self.assertEqual(series, [datetime(2013, 1, 1, 0, 0), datetime(2013, 1, 2, 0, 0), datetime(2013, 1, 3, 0, 0), datetime(2013, 1, 4, 0, 0), datetime(2013, 1, 5, 0, 0)])

    def sort_series_by_date(self):
        series = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},
        ]

        expected = [
            {'date': datetime(2013, 3, 18, 0, 0), 'value': 849},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2011, 2, 28, 0, 0), 'value': 619},
            {'date': datetime(2011, 1, 31, 0, 0), 'value': 194},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243},
        ]

        self.assertListEqual(expected, sort_series_by_date(series))

    def parse_series_dates(self):
        series = [
            {'date': "2011-06-30T00:00:00", 'value': 993},
            {'date': "2012-05-15T00:00:00", 'value': 663},
            {'date': "2010-04-04T00:00:00", 'value': 243}
        ]

        expected = [
            {'date': datetime(2011, 6, 3, 0, 0), 'value': 993},
            {'date': datetime(2012, 5, 15, 0, 0), 'value': 663},
            {'date': datetime(2010, 4, 4, 0, 0), 'value': 243}
        ]

        self.assertListEqual(expected, parse_series_dates(series))


