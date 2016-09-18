import datetime
import pprint
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.service.svc_main.implementation.service_endpoints.weather_endpoints import WeatherEndpoints
import unittest

__author__ = 'erezrubinstein'



class TestMainWeather(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestMainWeather, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_logger = Dependency("FlaskLogger").value
        self.main_param = Dependency("CoreAPIParamsBuilder").value

        # create endpoint object
        self.endpoint = WeatherEndpoints(None, self.mock_logger)

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.maxDiff = None


    def doCleanups(self):

        # call parent clean up
        super(TestMainWeather, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_get_weather_dates(self):

        # inputs
        fields = ["_id", "d"]
        limit = 1
        sort = [["d", 1]]
        params_1 = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields, sort=sort, limit=limit, use_new_json_encoder=True)["params"]
        sort = [["d", -1]]
        params_2 = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields, sort=sort, limit=limit, use_new_json_encoder=True)["params"]

        # mock return data
        mock_result_1 = [{"_id": "droid_1", "d": "R2D2"}]
        mock_result_2 = [{"_id": "droid_2", "d": "C3PO"}]

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("weather", params_1, encode_and_decode_results=False, context=self.context).AndReturn(mock_result_1)
        self.mock_main_access.mds.call_find_entities_raw("weather", params_2, encode_and_decode_results=False, context=self.context).AndReturn(mock_result_2)

        # replay recording
        self.mox.ReplayAll()

        # run & assert
        results = self.endpoint.get_weather_dates(context=self.context)

        self.assertEqual(results, {"min_date": "R2D2", "max_date": "C3PO"})


    def test_input_parsing_and_validation(self):

        # create good params
        current_time_period = ["2013-01-01", "2013-01-02"]
        prior_time_period = ["2012-01-01", "2012-01-02"]
        units = "metric"

        # test bad current time periods
        self.assertRaises(ValueError, self.endpoint._validate_and_parse_inputs, ['', '', ''], prior_time_period, units)
        self.assertRaises(ValueError, self.endpoint._validate_and_parse_inputs, current_time_period, ['', '', ''], units)
        self.assertRaises(ValueError, self.endpoint._validate_and_parse_inputs, ['324234', ''], prior_time_period, units)
        self.assertRaises(ValueError, self.endpoint._validate_and_parse_inputs, current_time_period, ['324234', ''], units)

        # test bad aggregate and bad units
        self.assertRaises(ValueError, self.endpoint._validate_and_parse_inputs, current_time_period, prior_time_period, "woot")

        # test a good run
        (current_time_period,
         prior_time_period,
         units) = self.endpoint._validate_and_parse_inputs(current_time_period, prior_time_period, units)

        # verify they're parsed correctly
        self.assertEqual(current_time_period, current_time_period)
        self.assertEqual(prior_time_period, prior_time_period)
        self.assertEqual(units, "metric")


    def test_get_raw_stores_for_cache(self):

        # define params
        banner_ids = ["chicken", "woot"]
        current_time_period = [datetime.datetime(2013, 1, 1), datetime.datetime(2013, 1, 2)]
        prior_time_period = [datetime.datetime(2012, 1, 1), datetime.datetime(2012, 1, 2)]
        units = "metric"

        # define mocks and expected values
        temp_field = "tcmean"
        precip_field = "pmm"

        store_weather_info = [["store_1", "weather_1", 1000.0, 1000.0],
                              ["store_2", "weather_2", 1000.0, 1000.0],
                              ["store_3", "weather_1", 1000.0, 1000.0]]
        weather_codes = {"weather_1", "weather_2"}
        weather_code_by_store = {"store_1": "weather_1", "store_2": "weather_2"}
        store_ids_by_code = {"weather_1": ["store_1", "store_3"], "weather_2": ["store_2"]}

        prior_period_weather = ["chicken"]
        current_period_weather = ["woot"]

        # stub out stuff
        self.mox.StubOutWithMock(self.endpoint, "_get_store_weather_info")
        self.mox.StubOutWithMock(self.endpoint, "_get_weather_info_by_store")
        self.mox.StubOutWithMock(self.endpoint, "_get_store_ids_by_code")
        self.mox.StubOutWithMock(self.endpoint, "_get_weather_aggregates")
        self.mox.StubOutWithMock(self.endpoint, "_combine_prior_and_current_weather")
        self.mox.StubOutWithMock(self.endpoint, "_get_weather_station_details")
        self.mox.StubOutWithMock(self.endpoint, "_combine_store_fields_and_format_for_ui")

        # begin recording
        self.endpoint._get_store_weather_info(banner_ids, current_time_period, prior_time_period).AndReturn(store_weather_info)
        self.endpoint._get_weather_info_by_store(store_weather_info, units).AndReturn(weather_code_by_store)
        self.endpoint._get_store_ids_by_code(store_weather_info).AndReturn(store_ids_by_code)
        self.endpoint._get_weather_aggregates(weather_codes, prior_time_period, temp_field, precip_field, self.context).AndReturn(prior_period_weather)
        self.endpoint._get_weather_aggregates(weather_codes, current_time_period, temp_field, precip_field, self.context).AndReturn(current_period_weather)
        self.endpoint._combine_prior_and_current_weather(prior_period_weather, current_period_weather).AndReturn("chicken_woot")
        self.endpoint._get_weather_station_details(weather_codes).AndReturn("mr bigglesworth")
        self.endpoint._combine_store_fields_and_format_for_ui("chicken_woot", store_ids_by_code, weather_code_by_store, "mr bigglesworth").AndReturn("chilly_willy")

        # replay recording
        self.mox.ReplayAll()

        # run
        results = self.endpoint._get_raw_stores_for_cache(banner_ids, current_time_period, prior_time_period, units, self.context)

        # verify results are the combined data
        self.assertEqual(results, "chilly_willy")


    def test_combine_prior_and_current_weather(self):

        # create mock weather for prior and current
        # make sure that there's a prior that's not in current and that there's a current that's not in prior.
        # also make sure to test positive and negative % diffs
        mock_prior_weather = [
            self._create_prior_store_weather(1, 2, 1, 3, 5, 4, 6, 2, 2),
            self._create_prior_store_weather(2, 8, 7, 9, 11, 10, 12, 2, 2),
            self._create_prior_store_weather(3, 14, 13, 15, 17, 16, 18, 2, 2)
        ]
        mock_current_weather = [
            self._create_current_store_weather(2, 11, 10, 12, 14, 13, 15, 4, 4),
            self._create_current_store_weather(3, 5, 4, 6, 8, 7, 9, 1, 4),
            self._create_current_store_weather(4, 1, 1, 1, 1, 1, 1, 0, 4)
        ]

        # combine the two data sets
        results = self.endpoint._combine_prior_and_current_weather(mock_prior_weather, mock_current_weather)

        # verify the results, which I calculated manually
        self.assertEqual(sorted(results), sorted([
            self._create_combined_store_data(2, 8, 11, 7, 10, 9, 12, 11, 14, 10, 13, 12, 15, 37.5, 42.86, 33.33, 27.27, 30, 25, 2, 4, 100, 2, 4),
            self._create_combined_store_data(3, 14, 5, 13, 4, 15, 6, 17, 8, 16, 7, 18, 9, -64.29, -69.23, -60, -52.94, -56.25, -50, 2, 1, -50, 2, 4)
        ]))


    def test_combine_store_fields_and_format_for_ui(self):

        # define mocks
        combined_data = [
            self._create_combined_store_data(2, 8, 11, 7, 10, 9, 12, 11, 14, 10, 13, 12, 15, 37.33, 42.86, 33.33, 27.27, 30, 25, 2, 4, 100, 2, 4),
            self._create_combined_store_data(3, 14, 5, 13, 4, 15, 6, 17, 8, 16, 7, 18, 9, -64.3, -69.2, -60, -52.9, -56.3, -50, 2, 1, -50, 2, 4)
        ]
        mock_params = {
            "query": { "data.store_id": { "$in": ["store_id_2", "store_id_3"] }},
            "entity_fields": ["data.company_name", "data.street_number", "data.street", "data.suite", "data.city", "data.state", "data.zip", "data.phone",
                              "data.store_opened_date", "data.store_closed_date", "data.store_id"]
        }
        mock_trade_areas = [
            { "data": { "store_id": "store_id_2", "company_name": "company_name_2", "city": "city_2", "state": "state_2", "street_number": 1, "street": "yo", "zip": 1, "suite": 2, "phone": 3, "store_opened_date": None, "store_closed_date": None }},
            { "data": { "store_id": "store_id_3", "company_name": "company_name_3", "city": "city_3", "state": "state_3", "street_number": 1, "street": "yo", "zip": 1, "suite": 2, "phone": 3, "store_opened_date": None, "store_closed_date": None }}
        ]
        mock_store_weather_info = [
            ["store_id_2", "store_id_2#!@store_id_2", 1000.0, 1000.0],
            ["store_id_3", "store_id_3#!@store_id_3", 2000.0, 2000.0]
        ]
        mock_weather_station_lookups = {
            "store_id_2#!@store_id_2": {
                "temp_station_code": "store_id_2",
                "temp_station_name": "temp_1",
                "temp_station_state": "temp_2",
                "temp_station_latitude": 1,
                "temp_station_longitude": -1,
                "precip_station_code": "store_id_2",
                "precip_station_name": "precip_1",
                "precip_station_state": "precip_2",
                "precip_station_latitude": 2,
                "precip_station_longitude": -2
            },
            "store_id_3#!@store_id_3": {
                "temp_station_code": "store_id_3",
                "temp_station_name": "temp_3",
                "temp_station_state": "temp_4",
                "temp_station_latitude": 3,
                "temp_station_longitude": -3,
                "precip_station_code": "store_id_3",
                "precip_station_name": "precip_3",
                "precip_station_state": "precip_4",
                "precip_station_latitude": 4,
                "precip_station_longitude": -4
            }
        }

        # translate to mappings
        mock_weather_code_by_store = self.endpoint._get_weather_info_by_store(mock_store_weather_info, "metric")
        mock_store_ids_by_code = self.endpoint._get_store_ids_by_code(mock_store_weather_info)

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("trade_area", mock_params, encode_and_decode_results=False).AndReturn(mock_trade_areas)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = self.endpoint._combine_store_fields_and_format_for_ui(combined_data, mock_store_ids_by_code, mock_weather_code_by_store, mock_weather_station_lookups)

        # make sure results are correct
        self.assertEqual(results, [
            self._add_store_fields_to_combined_data(combined_data[0], 2, 1.0, 1.0, "temp_1", "temp_2", 1, -1, "precip_1", "precip_2", 2, -2, "store_id_2", "store_id_2"),
            self._add_store_fields_to_combined_data(combined_data[1], 3, 2.0, 2.0, "temp_3", "temp_4", 3, -3, "precip_3", "precip_4", 4, -4, "store_id_3", "store_id_3")
        ])

    def test_calculate_summary_empty_lists(self):

        # define mocks
        mock_prior_weather = [
            # has nothing!
            self._create_prior_store_weather(1, None, None, None, None, None, None, None, None),
        ]

        mock_current_weather = [
            # has nothing!
            self._create_current_store_weather(1, None, None, None, None, None, None, None, None),
        ]

        # nothing to record... respect!

        # replay all
        self.mox.ReplayAll()

        # go!
        full_data = self.endpoint._combine_prior_and_current_weather(mock_prior_weather, mock_current_weather)
        summary = self.endpoint._calculate_summary(full_data)

        self.assertEqual(summary, {
            "min_prior_temp_min": None,
            "min_prior_temp_avg": None,
            "min_prior_temp_max": None,
            "avg_prior_temp_min": None,
            "avg_prior_temp_avg": None,
            "avg_prior_temp_max": None,
            "max_prior_temp_min": None,
            "max_prior_temp_avg": None,
            "max_prior_temp_max": None,
            "min_prior_precip_min": None,
            "min_prior_precip_avg": None,
            "min_prior_precip_max": None,
            "avg_prior_precip_min": None,
            "avg_prior_precip_avg": None,
            "avg_prior_precip_max": None,
            "max_prior_precip_min": None,
            "max_prior_precip_avg": None,
            "max_prior_precip_max": None,
            "min_current_temp_min": None,
            "min_current_temp_avg": None,
            "min_current_temp_max": None,
            "avg_current_temp_min": None,
            "avg_current_temp_avg": None,
            "avg_current_temp_max": None,
            "max_current_temp_min": None,
            "max_current_temp_avg": None,
            "max_current_temp_max": None,
            "min_current_precip_min": None,
            "min_current_precip_avg": None,
            "min_current_precip_max": None,
            "avg_current_precip_min": None,
            "avg_current_precip_avg": None,
            "avg_current_precip_max": None,
            "max_current_precip_min": None,
            "max_current_precip_avg": None,
            "max_current_precip_max": None,
            "min_prior_precip_days": None,
            "avg_prior_precip_days": None,
            "max_prior_precip_days": None,
            "min_current_precip_days": None,
            "avg_current_precip_days": None,
            "max_current_precip_days": None,
            "min_temp_min_change": None,
            "min_temp_avg_change": None,
            "min_temp_max_change": None,
            "avg_temp_min_change": None,
            "avg_temp_avg_change": None,
            "avg_temp_max_change": None,
            "max_temp_min_change": None,
            "max_temp_avg_change": None,
            "max_temp_max_change": None,
            "min_precip_min_change": None,
            "min_precip_avg_change": None,
            "min_precip_max_change": None,
            "avg_precip_min_change": None,
            "avg_precip_avg_change": None,
            "avg_precip_max_change": None,
            "max_precip_min_change": None,
            "max_precip_avg_change": None,
            "max_precip_max_change": None,
            "min_precip_days_change": None,
            "avg_precip_days_change": None,
            "max_precip_days_change": None
        })


    def test_calculate_summary_with_nulls(self):

        # define mocks
        mock_prior_weather = [

            # has all fields
            self._create_prior_store_weather(1, 1, 3, 5, 7, 9, 11, 2, 2),

            # has only temp fields
            self._create_prior_store_weather(2, 13, 15, 17, 0.0, None, None, 0, 2),

            # has only precip fields
            self._create_prior_store_weather(3, 0.0, None, None, 19, 21, 23, 1, 2)
        ]

        mock_current_weather = [
            # has all fields
            self._create_current_store_weather(1, 2, 4, 6, 8, 10, 12, 4, 2),

            # has only temp fields
            self._create_current_store_weather(2, 14, 16, 18, 0.0, None, None, 0, 2),

            # has only precip fields
            self._create_current_store_weather(3, 0.0, None, None, 20, 22, 24, 2, 2)
        ]

        # nothing to record... respect!

        # replay all
        self.mox.ReplayAll()

        # go!
        full_data = self.endpoint._combine_prior_and_current_weather(mock_prior_weather, mock_current_weather)
        summary = self.endpoint._calculate_summary(full_data)

        # verify that the summary doesn't include the fields that had nulls.  Most important for the averages.
        self.assertEqual(summary, {
            "min_prior_temp_min": 3,
            "min_prior_temp_avg": 1,
            "min_prior_temp_max": 5,
            "avg_prior_temp_min": 9,
            "avg_prior_temp_avg": 7,
            "avg_prior_temp_max": 11,
            "max_prior_temp_min": 15,
            "max_prior_temp_avg": 13,
            "max_prior_temp_max": 17,
            "min_prior_precip_min": 9,
            "min_prior_precip_avg": 7,
            "min_prior_precip_max": 11,
            "avg_prior_precip_min": 15,
            "avg_prior_precip_avg": 13,
            "avg_prior_precip_max": 17,
            "max_prior_precip_min": 21,
            "max_prior_precip_avg": 19,
            "max_prior_precip_max": 23,
            "min_current_temp_min": 4,
            "min_current_temp_avg": 2,
            "min_current_temp_max": 6,
            "avg_current_temp_min": 10,
            "avg_current_temp_avg": 8,
            "avg_current_temp_max": 12,
            "max_current_temp_min": 16,
            "max_current_temp_avg": 14,
            "max_current_temp_max": 18,
            "min_current_precip_min": 10,
            "min_current_precip_avg": 8,
            "min_current_precip_max": 12,
            "avg_current_precip_min": 16,
            "avg_current_precip_avg": 14,
            "avg_current_precip_max": 18,
            "max_current_precip_min": 22,
            "max_current_precip_avg": 20,
            "max_current_precip_max": 24,
            "min_prior_precip_days": 1,
            "avg_prior_precip_days": 1.5,
            "max_prior_precip_days": 2,
            "min_current_precip_days": 2,
            "avg_current_precip_days": 3,
            "max_current_precip_days": 4,

            # percent diff section
            "min_temp_min_change": 33.33,
            "min_temp_avg_change": 100,
            "min_temp_max_change": 20,
            "avg_temp_min_change": 11.11,
            "avg_temp_avg_change": 14.29,
            "avg_temp_max_change": 9.09,
            "max_temp_min_change": 6.67,
            "max_temp_avg_change": 7.69,
            "max_temp_max_change": 5.88,
            "min_precip_min_change": 11.11,
            "min_precip_avg_change": 14.29,
            "min_precip_max_change": 9.09,
            "avg_precip_min_change": 6.67,
            "avg_precip_avg_change": 7.69,
            "avg_precip_max_change": 5.88,
            "max_precip_min_change": 4.76,
            "max_precip_avg_change": 5.26,
            "max_precip_max_change": 4.35,
            "min_precip_days_change": 100,
            "avg_precip_days_change": 100,
            "max_precip_days_change": 100
        })


    def test_get_dates_in_range(self):

        # test february...
        time_period = [datetime.datetime(2013, 2, 25), datetime.datetime(2013, 3, 4)]

        # get range
        dates = self.endpoint._get_dates_in_range(time_period)

        # verify date query
        self.assertEqual(dates, [
            datetime.datetime(2013, 2, 25),
            datetime.datetime(2013, 2, 26),
            datetime.datetime(2013, 2, 27),
            datetime.datetime(2013, 2, 28),
            datetime.datetime(2013, 3, 1),
            datetime.datetime(2013, 3, 2),
            datetime.datetime(2013, 3, 3),
            datetime.datetime(2013, 3, 4)
        ])

    def test_get_percent_change(self):

        # basics
        prior = 1.0
        current = 2.0
        self.assertEqual(self.endpoint._get_percent_change(prior, current), 100.0)

        prior = 1.0
        current = 1.0
        self.assertEqual(self.endpoint._get_percent_change(prior, current), 0.0)

        # rounding
        prior = 1.0
        current = 1.0 + (1.0 / 3.0)
        self.assertEqual(self.endpoint._get_percent_change(prior, current), 33.33)

        # null-handling
        prior = None
        current = None
        self.assertEqual(self.endpoint._get_percent_change(prior, current), None)

        prior = 1.0
        current = None
        self.assertEqual(self.endpoint._get_percent_change(prior, current), None)

        prior = None
        current = 1.0
        self.assertEqual(self.endpoint._get_percent_change(prior, current), None)

        # avoid divide by zero
        prior = 0.0
        current = 1.0
        self.assertEqual(self.endpoint._get_percent_change(prior, current), None)

    def test_calculate_coverage(self):

        mock_full_data = [{"prior_weather_days": 31, "current_weather_days": 15}, {"prior_weather_days": 31, "current_weather_days": 10}]
        mock_current_time_period = ["2014-05-01", "2014-05-17"]
        mock_prior_time_period = ["2013-05-01", "2013-05-31"]

        coverage = self.endpoint._calculate_coverage(mock_full_data, mock_current_time_period, mock_prior_time_period)

        expected_prior_coverage = 100.0
        expected_current_coverage = (12.5/17.0) * 100.0

        self.assertEqual(round(coverage["prior_weather_coverage"], 2), round(expected_prior_coverage, 2))
        self.assertEqual(round(coverage["current_weather_coverage"], 2), round(expected_current_coverage, 2))


    # --------------------------- Private Methods --------------------------- #

    def _add_store_fields_to_combined_data(self, combined_record, store_num, temp_station_distance, precip_station_distance,
                                           temp_station_name, temp_station_state, temp_station_latitude, temp_station_longitude,
                                           precip_station_name, precip_station_state, precip_station_latitude, precip_station_longitude,
                                           temp_station_code, precip_station_code):

        combined_record["_id"] = "store_id_%s" % str(store_num)
        combined_record["company_name"] = 'company_name_%s' % str(store_num)
        combined_record["city"] = 'city_%s' % str(store_num)
        combined_record["state"] = 'state_%s' % str(store_num)
        combined_record["city"] = "city_%s" % str(store_num)
        combined_record["state"] = "state_%s" % str(store_num)
        combined_record["street_number"] = 1
        combined_record["street"] = "yo"
        combined_record["zip"] = 1
        combined_record["suite"] = 2
        combined_record["phone_number"] = 3
        combined_record["store_opened"] = None
        combined_record["store_closed"] = None

        # yes, this is weird... normal weather codes are formatted like station_station, we do split on underscore for the UI
        combined_record["weather_station"] = "store_id_%s, store_id_%s" % (str(store_num), str(store_num))

        # set weather station details
        combined_record["temp_station_distance"] = temp_station_distance
        combined_record["precip_station_distance"] = precip_station_distance
        combined_record["temp_station_name"] = temp_station_name
        combined_record["temp_station_code"] = temp_station_code
        combined_record["temp_station_state"] = temp_station_state
        combined_record["temp_station_latitude"] = temp_station_latitude
        combined_record["temp_station_longitude"] = temp_station_longitude
        combined_record["precip_station_name"] = precip_station_name
        combined_record["precip_station_code"] = precip_station_code
        combined_record["precip_station_state"] = precip_station_state
        combined_record["precip_station_latitude"] = precip_station_latitude
        combined_record["precip_station_longitude"] = precip_station_longitude

        return combined_record

    def _create_combined_store_data(self, store_num, prior_temp_avg, current_temp_avg, prior_temp_min, current_temp_min,
                                    prior_temp_max, current_temp_max, prior_precip_avg, current_precip_avg, prior_precip_min,
                                    current_precip_min, prior_precip_max, current_precip_max, temp_avg_diff, temp_min_diff,
                                    temp_max_diff, precip_avg_diff, precip_min_diff, precip_max_diff, prior_precip_days,
                                    current_precip_days, precip_days_percent_diff, prior_weather_days, current_weather_days):

        store_data = {
            '_id': 'store_id_%s#!@store_id_%s' % (str(store_num), str(store_num)),
            "prior_temp_avg": prior_temp_avg,
            "current_temp_avg": current_temp_avg,
            "temp_avg_percent_change": temp_avg_diff,
            "prior_temp_min": prior_temp_min,
            "current_temp_min": current_temp_min,
            "temp_min_percent_change": temp_min_diff,
            "prior_temp_max": prior_temp_max,
            "current_temp_max": current_temp_max,
            "temp_max_percent_change": temp_max_diff,
            "prior_precip_avg": prior_precip_avg,
            "current_precip_avg": current_precip_avg,
            "precip_avg_percent_change": precip_avg_diff,
            "prior_precip_min": prior_precip_min,
            "current_precip_min": current_precip_min,
            "precip_min_percent_change": precip_min_diff,
            "prior_precip_max": prior_precip_max,
            "current_precip_max": current_precip_max,
            "precip_max_percent_change": precip_max_diff,
            "prior_precip_days": prior_precip_days,
            "current_precip_days": current_precip_days,
            "precip_days_percent_change": precip_days_percent_diff,
            "prior_weather_days": prior_weather_days,
            "current_weather_days": current_weather_days
        }


        return store_data

    def _create_prior_store_weather(self, store_num, temp_avg, temp_min, temp_max, precip_avg, precip_min, precip_max, precip_days, weather_days):

        return {
            '_id': 'store_id_%s#!@store_id_%s' % (str(store_num), str(store_num)),
            'temp_avg': temp_avg,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'precip_avg': precip_avg,
            'precip_min': precip_min,
            'precip_max': precip_max,
            'precip_days': precip_days,
            'weather_days': weather_days
        }

    def _create_current_store_weather(self, store_num, temp_avg, temp_min, temp_max, precip_avg, precip_min, precip_max, precip_days, weather_days):

        return {
            '_id': 'store_id_%s#!@store_id_%s' % (str(store_num), str(store_num)),
            'weather_code': '%s, %s' % (str(store_num), str(store_num)),
            'temp_avg': temp_avg,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'precip_avg': precip_avg,
            'precip_min': precip_min,
            'precip_max': precip_max,
            'precip_days': precip_days,
            'weather_days': weather_days
        }

if __name__ == '__main__':
    unittest.main()
