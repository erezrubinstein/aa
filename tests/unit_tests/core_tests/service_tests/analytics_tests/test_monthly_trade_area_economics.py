from __future__ import division
import random
from common.utilities.time_series import get_monthly_time_series
from core.service.svc_analytics.implementation.calc.engines.economics.monthly_trade_area_economics import MonthlyTradeAreaEconomics, EconZip, EconAreaType, EconMeasure
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser, LAST_ECONOMICS_DATE, get_start_date_of_next_month, ECONOMICS_START_DATE, END_OF_WORLD, START_OF_WORLD
from bson.objectid import ObjectId
import __builtin__
import datetime
import unittest
import pprint
import json
import mox


class MonthlyTradeAreaEconomicsTests(mox.MoxTestBase):

    def setUp(self):

        super(MonthlyTradeAreaEconomicsTests, self).setUp()
        register_common_mox_dependencies(self.mox)

        self.mox.StubOutWithMock(json, "loads")
        self.mox.StubOutWithMock(__builtin__, "super")

        self.context = "some sort of context"

        self.maxDiff = None

        # helper instance variables
        self.date_parser = FastDateParser()

        # main instance of the calc engine to test stuff with
        self.calc_engine = MonthlyTradeAreaEconomics(None, None, "123", "fusion", "fusion_reactor", None, None, None,
                                                     self.context, self.date_parser)

        self.company_id = ObjectId()
        self.calc_engine.run_params = {
            "target_entity_ids": [str(self.company_id)],
            "latest_econ_month": LAST_ECONOMICS_DATE
        }
        # some tests need this...
        self.calc_engine.latest_econ_month = LAST_ECONOMICS_DATE

        self.ta_id1 = ObjectId()
        self.ta_id2 = ObjectId()
        self.ta_id3 = ObjectId()
        self.ta_id4 = ObjectId()

        self.future_date = get_start_date_of_next_month(LAST_ECONOMICS_DATE)

        self.calc_engine.fetched_data = [
            [
                self.ta_id1,
                "New York City",
                "NY",
                "10001",
                "2013-01-01T00:00:00",
                get_start_date_of_next_month(self.future_date).strftime("%Y-%m-%dT%H:%M:%S")
            ],
            [
                self.ta_id2,
                "New York City",
                "NY",
                "10001",
                "2012-01-01T00:00:00",
                "2013-04-15T00:00:00"
            ],
            [
                self.ta_id3,
                "Tacoland",
                "TC",
                "99999",
                None,
                None
            ],
            [
                self.ta_id4,
                "New York City",
                "NY",
                "10001",
                "2012-01-01T00:00:00",
                get_start_date_of_next_month(self.future_date).strftime("%Y-%m-%dT%H:%M:%S")
            ]
        ]

    def test_calculate__no_zips(self):

        self.mox.StubOutWithMock(self.calc_engine, "_get_econ_zip")

        for ta in self.calc_engine.fetched_data:

            zip_code = int(ta[3][:5])

            self.calc_engine._get_econ_zip(zip_code).AndReturn(None)


        self.mox.ReplayAll()

        self.calc_engine._calculate()

        self.assertEqual(self.calc_engine.results, {})

    def test_calculate__got_zips(self):

        self.mox.StubOutWithMock(self.calc_engine, "_get_econ_zip")
        self.mox.StubOutWithMock(self.calc_engine, "_row_to_result")

        for ta in self.calc_engine.fetched_data:

            zip_code = int(ta[3][:5])
            econ_zip = EconZip(zip_code)
            econ_zip.area_types = {"P": "This Must Be the Place"}

            self.calc_engine._get_econ_zip(zip_code).AndReturn(econ_zip)
            self.calc_engine._row_to_result(ta, econ_zip).AndReturn("awesomeness")

        self.mox.ReplayAll()

        self.calc_engine._calculate()

        expected_results = {
            self.ta_id1: "awesomeness",
            self.ta_id2: "awesomeness",
            self.ta_id3: "awesomeness",
            self.ta_id4: "awesomeness"
        }
        self.assertEqual(self.calc_engine.results, expected_results)

    def test_get_econ_zip(self):

        mock_zip = "10001"

        query = {
            "ZCTA5": mock_zip
        }

        fields = [
            "_id",
            "measure_text",
            "area_text",
            "area_type",
            "timeseries"
        ]

        params = self.calc_engine.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                   entity_fields=fields, as_list=True)["params"]

        econ_id = ObjectId()
        econs = [
            [
                econ_id,
                "unemployment rate",
                "New York City, NY",
                "P",
                [
                    {'date': '2013-01-01T00:00:00', 'value': 6.0},
                    {'date': '2013-02-01T00:00:00', 'value': 5.6},
                    {'date': '2013-03-01T00:00:00', 'value': 5.4},
                    {'date': '2013-04-01T00:00:00', 'value': 5.3},
                    {'date': '2013-05-01T00:00:00', 'value': 5.5},
                    {'date': '2013-06-01T00:00:00', 'value': 5.8},
                    {'date': '2013-07-01T00:00:00', 'value': 5.7}
                ]
            ]
        ]

        self.calc_engine.main_access.mds.call_find_entities_raw("econ", params, self.context, timeout=240,
                                                                encode_and_decode_results=False).AndReturn(econs)


        self.mox.ReplayAll()

        # get the expected object structure
        expected_econ_zip = self.__get_test_econ_zip(reverse=False)

        econ_zip = self.calc_engine._get_econ_zip(mock_zip)

        # same same?
        self.assertEqual(econ_zip, expected_econ_zip)

    def test_row_to_result__normal(self):

        trade_area = self.calc_engine.fetched_data[0]

        econ_zip = self.__get_test_econ_zip()

        result = self.calc_engine._row_to_result(trade_area, econ_zip)

        expected_result = {
            "area_text": "New York City, NY",
            "area_type": "P",
            "monthly": {
                "unemployment rate": [
                        {'date': datetime.datetime(2013, 07, 01), 'value': 5.7},
                        {'date': datetime.datetime(2013, 06, 01), 'value': 5.8},
                        {'date': datetime.datetime(2013, 05, 01), 'value': 5.5},
                        {'date': datetime.datetime(2013, 04, 01), 'value': 5.3},
                        {'date': datetime.datetime(2013, 03, 01), 'value': 5.4},
                        {'date': datetime.datetime(2013, 02, 01), 'value': 5.6},
                        {'date': datetime.datetime(2013, 01, 01), 'value': 6.0}
                    ]
            }
        }

        self.assertDictEqual(result, expected_result)

    def test_row_to_result__closed_store(self):

        trade_area = self.calc_engine.fetched_data[1]

        # this store closed 2013-04-15, so last month with data should be 2013-03

        econ_zip = self.__get_test_econ_zip()

        result = self.calc_engine._row_to_result(trade_area, econ_zip)

        expected_result = {
            "area_text": "New York City, NY",
            "area_type": "P",
            "monthly": {
                "unemployment rate": [
                        {'date': datetime.datetime(2013, 03, 01), 'value': 5.4},
                        {'date': datetime.datetime(2013, 02, 01), 'value': 5.6},
                        {'date': datetime.datetime(2013, 01, 01), 'value': 6.0}
                    ]
            }
        }

        self.assertDictEqual(result, expected_result)

    def test_row_to_result__blend_timeseries(self):

        # if the Place timeseries covers less time overall than County,
        # we should append the older part of the County timeseries

        trade_area = self.calc_engine.fetched_data[3]

        econ_zip = self.__get_test_econ_zip(add_county=True)

        result = self.calc_engine._row_to_result(trade_area, econ_zip)

        expected_result = {
            "area_text": "New York City, NY",
            "area_type": "P",
            "monthly": {
                "unemployment rate": [
                        {'date': datetime.datetime(2013, 7, 1), 'value': 5.7},
                        {'date': datetime.datetime(2013, 6, 1), 'value': 5.8},
                        {'date': datetime.datetime(2013, 5, 1), 'value': 5.5},
                        {'date': datetime.datetime(2013, 4, 1), 'value': 5.3},
                        {'date': datetime.datetime(2013, 3, 1), 'value': 5.4},
                        {'date': datetime.datetime(2013, 2, 1), 'value': 5.6},
                        {'date': datetime.datetime(2013, 1, 1), 'value': 6.0},
                        {'date': datetime.datetime(2012, 12, 1), 'value': 5.7},
                        {'date': datetime.datetime(2012, 11, 1), 'value': 5.8},
                        {'date': datetime.datetime(2012, 10, 1), 'value': 5.5},
                        {'date': datetime.datetime(2012, 9, 1), 'value': 5.3},
                        {'date': datetime.datetime(2012, 8, 1), 'value': 5.4},
                        {'date': datetime.datetime(2012, 7, 1), 'value': 5.6},
                    ]
            }
        }

        self.assertDictEqual(result, expected_result)

    def test_slice_time_series_before_date(self):

        time_series = [
            {'date': '2013-07-01T00:00:00', 'value': 5.7},
            {'date': '2013-06-01T00:00:00', 'value': 5.8},
            {'date': '2013-05-01T00:00:00', 'value': 5.5},
            {'date': '2013-04-01T00:00:00', 'value': 5.3},
            {'date': '2013-03-01T00:00:00', 'value': 5.4},
            {'date': '2013-02-01T00:00:00', 'value': 5.6},
            {'date': '2013-01-01T00:00:00', 'value': 6.0}
        ]

        result = self.calc_engine._slice_time_series_before_date(time_series, datetime.datetime(2013, 4, 1))

        expected_result = [
            {'date': '2013-03-01T00:00:00', 'value': 5.4},
            {'date': '2013-02-01T00:00:00', 'value': 5.6},
            {'date': '2013-01-01T00:00:00', 'value': 6.0}
        ]

        self.assertEqual(result, expected_result)

    def test_slice_time_series_before_date__ignore_leading_year(self):

        time_series = [
            {'date': 2013, 'value': 5.7},
            {'date': '2013-12-01T00:00:00', 'value': 5.7},
            {'date': '2013-11-01T00:00:00', 'value': 5.8},
            {'date': '2013-10-01T00:00:00', 'value': 5.5},
            {'date': '2013-09-01T00:00:00', 'value': 5.3},
            {'date': '2013-08-01T00:00:00', 'value': 5.4},
            {'date': '2013-07-01T00:00:00', 'value': 5.6},
            {'date': '2013-06-01T00:00:00', 'value': 6.0}
        ]

        result = self.calc_engine._slice_time_series_before_date(time_series, datetime.datetime(2013, 9, 1))

        expected_result = [
            {'date': '2013-08-01T00:00:00', 'value': 5.4},
            {'date': '2013-07-01T00:00:00', 'value': 5.6},
            {'date': '2013-06-01T00:00:00', 'value': 6.0}
        ]

        self.assertEqual(result, expected_result)

    def test_clean_timeseries__always_open(self):

        time_series = [
            {"date": date.strftime("%Y-%m-%dT%H:%M:%S"), "value": random.random()*7}
            for date in get_monthly_time_series(start=ECONOMICS_START_DATE, end=LAST_ECONOMICS_DATE)
        ]

        expected_result = [
            {"date": self.date_parser.parse_date((t["date"])), "value": t["value"]} for t in time_series
        ]

        result = self.calc_engine._clean_timeseries(time_series, START_OF_WORLD, END_OF_WORLD)

        self.assertEqual(result, expected_result)

    def test_clean_timeseries__opened(self):

        open_date = LAST_ECONOMICS_DATE - datetime.timedelta(days=300)

        time_series = [
            {"date": date.strftime("%Y-%m-%dT%H:%M:%S"), "value": random.random()*7}
            for date in get_monthly_time_series(start=ECONOMICS_START_DATE, end=LAST_ECONOMICS_DATE)
        ]

        expected_result = [
            {"date": self.date_parser.parse_date((t["date"])), "value": t["value"]}
            for t in time_series
            if get_start_date_of_next_month(self.date_parser.parse_date((t["date"]))) >= open_date
        ]

        result = self.calc_engine._clean_timeseries(time_series, open_date, END_OF_WORLD)

        self.assertEqual(result, expected_result)

    def test_clean_timeseries__closed(self):

        closed_date = LAST_ECONOMICS_DATE - datetime.timedelta(days=90)

        time_series = [
            {"date": date.strftime("%Y-%m-%dT%H:%M:%S"), "value": random.random()*7}
            for date in get_monthly_time_series(start=ECONOMICS_START_DATE, end=LAST_ECONOMICS_DATE)
        ]

        expected_result = [
            {"date": self.date_parser.parse_date((t["date"])), "value": t["value"]}
            for t in time_series
            if get_start_date_of_next_month(self.date_parser.parse_date((t["date"]))) < closed_date
        ]

        result = self.calc_engine._clean_timeseries(time_series, START_OF_WORLD, closed_date)

        self.assertEqual(result, expected_result)


    ### ---------------------- private helpers ----------------------###

    def __get_test_econ_zip(self, reverse=True, add_county=False):

        time_series = [
                    {'date': '2013-07-01T00:00:00', 'value': 5.7},
                    {'date': '2013-06-01T00:00:00', 'value': 5.8},
                    {'date': '2013-05-01T00:00:00', 'value': 5.5},
                    {'date': '2013-04-01T00:00:00', 'value': 5.3},
                    {'date': '2013-03-01T00:00:00', 'value': 5.4},
                    {'date': '2013-02-01T00:00:00', 'value': 5.6},
                    {'date': '2013-01-01T00:00:00', 'value': 6.0}
                ]
        if not reverse:
            time_series = sorted(time_series, key=lambda x: x["date"])

        econ_measure = EconMeasure("unemployment rate", time_series)
        econ_area_type = EconAreaType("P", "New York City, NY")
        econ_area_type.measures = {"unemployment rate": econ_measure}

        econ_zip = EconZip("10001")
        econ_zip.area_types = {
            "P": econ_area_type
        }

        if add_county:

            county_time_series = [
                {'date': '2013-07-01T00:00:00', 'value': 5.7},
                {'date': '2013-06-01T00:00:00', 'value': 5.8},
                {'date': '2013-05-01T00:00:00', 'value': 5.5},
                {'date': '2013-04-01T00:00:00', 'value': 5.3},
                {'date': '2013-03-01T00:00:00', 'value': 5.4},
                {'date': '2013-02-01T00:00:00', 'value': 5.6},
                {'date': '2013-01-01T00:00:00', 'value': 6.0},
                {'date': '2012-12-01T00:00:00', 'value': 5.7},
                {'date': '2012-11-01T00:00:00', 'value': 5.8},
                {'date': '2012-10-01T00:00:00', 'value': 5.5},
                {'date': '2012-09-01T00:00:00', 'value': 5.3},
                {'date': '2012-08-01T00:00:00', 'value': 5.4},
                {'date': '2012-07-01T00:00:00', 'value': 5.6},
            ]
            if not reverse:
                county_time_series = sorted(county_time_series, key=lambda x: x["date"])

            econ_measure = EconMeasure("unemployment rate", county_time_series)
            county_area_type = EconAreaType("C", "New York County, NY")
            county_area_type.measures = {"unemployment rate": econ_measure}
            econ_zip.area_types["C"] = county_area_type

        return econ_zip


if __name__ == '__main__':
    unittest.main()
