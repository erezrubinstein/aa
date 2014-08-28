# coding=utf-8
import pprint
import unittest
import json
import mox
from datetime import datetime, timedelta
from common.utilities.time_series import get_monthly_time_series
from common.utilities.date_utilities import parse_date, FastDateParser, LAST_ANALYTICS_DATE
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from core.service.svc_analytics.implementation.calc.engines.demographics.monthly_trade_area_demographics \
    import MonthlyTradeAreaDemographics
from common.utilities.time_series import TIME_SERIES_START


class MonthlyTradeAreaDemographicsTests(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(MonthlyTradeAreaDemographicsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # instantiate calc engine without init
        self.engine = MonthlyTradeAreaDemographics.__new__(MonthlyTradeAreaDemographics)
        self.engine.date_parser = FastDateParser()


    def test_calculate__always_open(self):
        test_pop_count = 12345

        self.engine.fetched_data = [self._get_test_trade_area("some_id", None, None, test_pop_count)]
        self.engine._calculate()

        result = self.engine.results["some_id"]
        result_series = result[0]["series"]
        monthly_series = get_monthly_time_series(end=LAST_ANALYTICS_DATE)

        self.assertEqual(len(monthly_series), len(result_series))

        for idx, series_item in enumerate(result_series):
            item_date = parse_date(series_item["date"])
            self.assertEqual(monthly_series[idx], item_date)
            self.assertEqual(test_pop_count, series_item["value"])


    def test_calculate__target_year(self):
        test_pop_count = 12345

        self.engine.fetched_data = [self._get_test_trade_area("some_id", None, None, test_pop_count, 2009)]
        self.engine._calculate()
        result = self.engine.results["some_id"][0]

        self.assertEqual(2009, result["target_year"])

    def test_calculate__has_store_opening(self):
        test_pop_count = 45462

        self.engine.fetched_data = [self._get_test_trade_area("some_id", datetime(2012, 1, 15), None, test_pop_count)]
        self.engine._calculate()

        result = self.engine.results["some_id"][0]
        result_series = result["series"]
        expected_dates = get_monthly_time_series(datetime(2012, 1, 1), LAST_ANALYTICS_DATE)

        self.assertEqual(len(expected_dates), len(result_series))

        for idx, result_series_item in enumerate(result_series):
            result_item_date = parse_date(result_series_item["date"])
            self.assertEqual(expected_dates[idx], result_item_date)
            self.assertEqual(test_pop_count, result_series_item["value"])

    def test_calculate__has_store_closing(self):

        test_pop_count = 2314

        self.engine.fetched_data = [self._get_test_trade_area("some_id", None, datetime(2011, 7, 3), test_pop_count)]
        self.engine._calculate()

        result = self.engine.results["some_id"][0]
        result_series = result["series"]
        expected_dates = get_monthly_time_series(TIME_SERIES_START, datetime(2011, 6, 1))

        self.assertEqual(len(expected_dates), len(result_series))
        self.assertEqual(datetime(2011, 6, 1), result_series[0]['date'])
        self.assertEqual(datetime(2011, 1, 1), result_series[-1]['date'])

        for idx, result_series_item in enumerate(result_series):
            item_date = parse_date(result_series_item["date"])
            self.assertEqual(expected_dates[idx], item_date)
            self.assertEqual(test_pop_count, result_series_item["value"])

    def test_calculate__has_store_opening_and_closing(self):
        test_pop_count = 68321

        self.engine.fetched_data = [self._get_test_trade_area("some_id", datetime(2011, 9, 3), datetime(2012, 3, 3), test_pop_count)]
        self.engine._calculate()

        result = self.engine.results["some_id"][0]
        result_series = result["series"]
        expected_dates = get_monthly_time_series(datetime(2011, 9, 3), datetime(2012, 2, 1))

        # we expect the date range to be 2011 09 30 to 2012 29 9
        self.assertEqual(len(expected_dates), len(result_series))
        self.assertEqual(datetime(2011, 9, 1), result_series[-1]['date'])
        self.assertEqual(datetime(2012, 2, 1), result_series[0]['date'])

        for idx, result_series_item in enumerate(result_series):
            item_date = parse_date(result_series_item["date"])
            self.assertEqual(expected_dates[idx], item_date)
            self.assertEqual(test_pop_count, result_series_item["value"])

    def test_calculate__multiple_trade_areas(self):
        test_pop_count_1 = 1000
        test_pop_count_2 = 2000
        test_pop_count_3 = 3000

        self.engine.fetched_data = [
            self._get_test_trade_area("test1", None, None, test_pop_count_1),
            self._get_test_trade_area("test2", None, None, test_pop_count_2),
            self._get_test_trade_area("test3", None, None, test_pop_count_3)
        ]

        self.engine._calculate()

        results_1 = [item["value"] for item in self.engine.results["test1"][0]["series"]]
        results_2 = [item["value"] for item in self.engine.results["test2"][0]["series"]]
        results_3 = [item["value"] for item in self.engine.results["test3"][0]["series"]]

        for result_combined in zip(results_1, results_2, results_3):
            expected_combined = (test_pop_count_1, test_pop_count_2, test_pop_count_3)
            self.assertTupleEqual(expected_combined, result_combined)

    def _get_test_trade_area(self, id, open=None, closed=None, demographics=100000, target_year=None):
        return [
            id,
            demographics,
            None if open is None else open.isoformat(),
            None if closed is None else closed.isoformat(),
            target_year
        ]


if __name__ == '__main__':
    unittest.main()
