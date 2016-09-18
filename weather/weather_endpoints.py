from common.utilities.Logging.debugging_timestamp_logger import DebuggingTimestampLogger
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import Dependency
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from common.utilities.pass_by_reference import PassByReference
from core.common.business_logic.service_entity_logic import weather_helper
from core.common.business_logic.service_entity_logic.time_interval_helper import live_entity_filter__existed_within
from core.service.svc_main.implementation.service_endpoints.service_endpoints import ServiceEndpoints
import numpy as np
import datetime

__author__ = 'erezrubinstein'

class WeatherEndpoints(ServiceEndpoints):

    def __init__(self, config, logger):

        # init on super class
        super(WeatherEndpoints, self).__init__(config, logger)

        # get useful dependencies
        self.main_access = Dependency("CoreAPIProvider").value
        self.main_param = Dependency("CoreAPIParamsBuilder").value

        # create a couple of these validation arrays up here so that we save re-instantiating the objects
        # create them as dicts for quick look ups.
        self.allowed_units = { "metric": 1, "us": 1 }

        # note this date parser will be shared by multiple requests, so dates will fill up over time
        # until the process is recycled... we may want to monitor this!
        self.date_parser = FastDateParser()

        # semantic list index vars
        self.store_id_idx = 0
        self.store_weather_code_idx = 1
        self.temp_station_distance_idx = 2
        self.precip_station_distance_idx = 3

    def get_weather_dates(self, context=None):
        """
        Get min and max date of all weather data loaded into MDS.
        Uses find with sort and limit because this is faster than an aggregate query.
        No need to use cache since these are superfast index lookups.
        """
        min_date = None
        max_date = None

        # these are used by both queries
        fields = ["_id", "d"]
        limit = 1

        # min_date first
        sort = [["d", 1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields, sort=sort, limit=limit, use_new_json_encoder=True)["params"]
        result = self.main_access.mds.call_find_entities_raw("weather", params, encode_and_decode_results=False, context=context)
        if result and len(result) == 1:
            min_date = result[0]["d"]

        # max_date next
        sort = [["d", -1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields, sort=sort, limit=limit, use_new_json_encoder=True)["params"]
        result = self.main_access.mds.call_find_entities_raw("weather", params, encode_and_decode_results=False, context=context)
        if result and len(result) == 1:
            max_date = result[0]["d"]

        return {"min_date": min_date, "max_date": max_date}

    def run_api_weather_stores(self, app, banner_ids, current_time_period, prior_time_period, units, user_params,
                               include_summary=False, context=None):
        """
        Main entry point for getting weather data aggregated for stores within banners over two time periods,
        and comparing current period vs prior period.
        """

        # field names vary with units (US or metric)
        self._set_fields(units)

        # validate user_params
        self._fix_user_params(user_params)

        # set up cache record for uniqueness
        cache_rec_detail = self._get_cache_rec(banner_ids, current_time_period, prior_time_period, units)

        # reference of the full data set, so that we can get the summary
        full_data_reference = PassByReference()

        # nested method to get the cache data
        def get_data_method():
            return self._get_raw_stores_for_cache(banner_ids, current_time_period, prior_time_period, units, context)

        # wrap the raw data in the cache provider
        data = app.get_preset_data_with_cache(cache_rec_detail, get_data_method, params=user_params,
                                              full_data_reference=full_data_reference, cache_with_params=True,
                                              override_cache_params=False)
        results = {
            "results": self._format_cached_data_for_ui(data["rows"]),
            "field_list": self.weather_fields_external,
            "field_meta": self.weather_field_meta,
            "meta": self._create_nice_meta(data["meta"], user_params)
        }

        # if we want to include the summary, calculate it
        if include_summary:

            # if full data is null (i.e. not the first run, than get the data set from cache)
            if not full_data_reference.reference:
                full_store_weather_list = app.get_preset_data_with_cache(cache_rec_detail, get_data_method,
                                                                         cache_with_params=True,
                                                                         override_cache_params=False)["rows"]
            else:
                full_store_weather_list = full_data_reference.reference

            summary = self._calculate_summary(full_store_weather_list)
            results["summary"] = summary

            coverage = self._calculate_coverage(full_store_weather_list, current_time_period, prior_time_period)
            results["coverage"] = coverage

        return results

    def _set_fields(self, units):

        if units == "us":
            temp = "F"
            precip = "in"
            distance = "mi"
        else:
            temp = "C"
            precip = "cm"
            distance = "km"

        # these are the fields to be returned for the weather_stores_list
        self.weather_fields_external = [
            "Banner",
            "Street Number",
            "Street",
            "Suite",
            "State",
            "City",
            "Zip",
            "Phone Number",
            "Store Opened",
            "Store Closed",
            "Weather\nStations",

            # Average Columns
            "Current\nAvg of Daily\nAvg Temp (&deg;{})".format(temp),
            "Prior\nAvg of Daily\nAvg Temp (&deg;{})".format(temp),
            "% Change\nAvg of Daily\nAvg Temp",
            "Current\nAvg of Daily\nPrecip ({})".format(precip),
            "Prior\nAvg of Daily\nPrecip ({})".format(precip),
            "% Change\nAvg of Daily\nPrecip",

            # Min Columns
            "Current\nMin of Daily\nAvg Temp (&deg;{})".format(temp),
            "Prior\nMin of Daily\nAvg Temp (&deg;{})".format(temp),
            "% Change\nMin of Daily\nAvg Temp",
            "Current\nMin of Daily\nPrecip ({})".format(precip),
            "Prior\nMin of Daily\nPrecip ({})".format(precip),
            "% Change\nMin of Daily\nPrecip",

            # Max Columns
            "Current\nMax of Daily\nAvg Temp (&deg;{})".format(temp),
            "Prior\nMax of Daily\nAvg Temp (&deg;{})".format(temp),
            "% Change\nMax of Daily\nAvg Temp",
            "Current\nMax of Daily\nPrecip ({})".format(precip),
            "Prior\nMax of Daily\nPrecip ({})".format(precip),
            "% Change\nMax of Daily\nPrecip",

            # Precip Days Columns
            "Current\nPrecip Days".format(precip),
            "Prior\nPrecip Days".format(precip),
            "% Change\nPrecip Days",

            # station details
            "Temp Station\nName",
            "Temp Station\nCode",
            "Temp Station\nState",
            "Temp Station\nDistance ({})".format(distance),
            "Temp Station\nLatitude",
            "Temp Station\nLongitude",
            "Precip Station\nName",
            "Precip Station\nCode",
            "Precip Station\nState",
            "Precip Station\nDistance ({})".format(distance),
            "Precip Station\nLatitude",
            "Precip Station\nLongitude"
        ]
        self.weather_fields_internal = [
            "company_name",
            "street_number",
            "street",
            "suite",
            "state",
            "city",
            "zip",
            "phone_number",
            "store_opened",
            "store_closed",
            "weather_station",

            # Average Columns
            "current_temp_avg",
            "prior_temp_avg",
            "temp_avg_percent_change",
            "current_precip_avg",
            "prior_precip_avg",
            "precip_avg_percent_change",

            # Min Columns
            "current_temp_min",
            "prior_temp_min",
            "temp_min_percent_change",
            "current_precip_min",
            "prior_precip_min",
            "precip_min_percent_change",

            # Max Columns
            "current_temp_max",
            "prior_temp_max",
            "temp_max_percent_change",
            "current_precip_max",
            "prior_precip_max",
            "precip_max_percent_change",

            # Precip Days Columns
            "current_precip_days",
            "prior_precip_days",
            "precip_days_percent_change",

            # station distance columns
            "temp_station_name",
            "temp_station_code",
            "temp_station_state",
            "temp_station_distance",
            "temp_station_latitude",
            "temp_station_longitude",
            "precip_station_name",
            "precip_station_code",
            "precip_station_state",
            "precip_station_distance",
            "precip_station_latitude",
            "precip_station_longitude",
        ]

        # meta for weather fields
        self.weather_field_meta = {
            "Current\nAvg of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "Prior\nAvg of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "% Change\nAvg of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
            "Current\nAvg of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "Prior\nAvg of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "% Change\nAvg of Daily\nPrecip": { "type": "percent", "decimals": 2 },

            # Min Columns
            "Current\nMin of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "Prior\nMin of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "% Change\nMin of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
            "Current\nMin of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "Prior\nMin of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "% Change\nMin of Daily\nPrecip": { "type": "percent", "decimals": 2 },

            # Max Columns
            "Current\nMax of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "Prior\nMax of Daily\nAvg Temp (&deg;{})".format(temp): { "type": "number", "decimals": 5 },
            "% Change\nMax of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
            "Current\nMax of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "Prior\nMax of Daily\nPrecip ({})".format(precip): { "type": "number", "decimals": 5 },
            "% Change\nMax of Daily\nPrecip": { "type": "percent", "decimals": 2 },

            # Precip Days Columns
            "Current\nPrecip Days": { "type": "number", "decimals": 5 },
            "Prior\nPrecip Days": { "type": "number", "decimals": 5 },
            "% Change\nPrecip Days": { "type": "percent", "decimals": 2 },

            "Temp Station\nDistance ({})".format(distance): {"type": "number", "decimals": 3},
            "Temp Station\nLatitude": { "type": "number", "decimals": 5 },
            "Temp Station\nLongitude": { "type": "number", "decimals": 5 },
            "Precip Station\nDistance ({})".format(distance): {"type": "number", "decimals": 3},
            "Precip Station\nLatitude": { "type": "number", "decimals": 5 },
            "Precip Station\nLongitude": { "type": "number", "decimals": 5 },
        }

        # field lists need to always match in order and length.  This is to check the length.  Just incase.
        assert len(self.weather_fields_internal) == len(self.weather_fields_external)

    def _get_raw_stores_for_cache(self, banner_ids, current_time_period, prior_time_period, units, context):

        with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "", self.logger):

            # validate and parse these specific inputs
            (current_time_period,
             prior_time_period,
             units) = self._validate_and_parse_inputs(current_time_period, prior_time_period, units)

            store_weather_info = self._get_store_weather_info(banner_ids, current_time_period, prior_time_period)

            if not store_weather_info:
                return []

            # get a distinct set of weather codes for these stores
            weather_codes = set([
                wc[self.store_weather_code_idx]
                for wc in store_weather_info
                if wc[self.store_weather_code_idx]
            ])

            # bail if no data
            if not weather_codes:
                return []

            # get a mapping of store_ids to the one-and-only weather_code per store
            weather_info_by_store = self._get_weather_info_by_store(store_weather_info, units)

            # get a mapping of codes to the list of store_ids that link to each code
            store_ids_by_code = self._get_store_ids_by_code(store_weather_info)

            # determine which weather fields we need based on units (f or c) and set semantic indexes for list access
            temp_field, precip_field = self._get_temp_precip_fields(units)

            # get prior period weather data
            with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "_get_weather_aggregates prior", self.logger):
                prior_period_weather = self._get_weather_aggregates(weather_codes, prior_time_period, temp_field, precip_field, context)

            # bail if no data
            if not prior_period_weather:
                return []

            # get current period weather
            with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "_get_weather_aggregates current", self.logger):
                current_period_weather = self._get_weather_aggregates(weather_codes, current_time_period, temp_field, precip_field, context)

            # combine prior and current data
            with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "combine prior and current", self.logger):
                combined_results = self._combine_prior_and_current_weather(prior_period_weather, current_period_weather)

            # bail if no data
            if not combined_results:
                return []

            # get weather station details (name, code, state, etc...)
            with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "get_weather_station_details", self.logger):
                weather_station_details_by_code = self._get_weather_station_details(weather_codes)

            # get store fields from trade areas
            with DebuggingTimestampLogger("WeatherEndPoints", "Complete", "combine store fields", self.logger):
                result = self._combine_store_fields_and_format_for_ui(combined_results, store_ids_by_code, weather_info_by_store, weather_station_details_by_code)

            return result

    # ----------------------- Protected Methods ----------------------- #

    def _get_weather_info_by_store(self, store_weather_info, units):
        """
        Transform a raw list of store info to a dict mapping string store_id to weather code and station distances.
        Convert station distances to specified units while we're here.
        """
        if units == "metric":
            # just convert to kilometers...
            def convert_units(input):
                if input is None:
                    return None
                else:
                    return input / 1000.0
        else:
            def convert_units(input):
                if input is None:
                    return None
                else:
                    return input * 0.000621371

        return {
            str(swc[self.store_id_idx]): {
                "weather_code": swc[self.store_weather_code_idx],
                "temp_station_distance": convert_units(swc[self.temp_station_distance_idx]),
                "precip_station_distance": convert_units(swc[self.precip_station_distance_idx])
            }
            for swc in store_weather_info
        }

    def _get_store_ids_by_code(self, store_weather_info):

        store_ids_by_code = {}

        for swc in store_weather_info:
            if swc[self.store_weather_code_idx] in store_ids_by_code:
                store_ids_by_code[swc[self.store_weather_code_idx]].append(str(swc[self.store_id_idx]))
            else:
                store_ids_by_code[swc[self.store_weather_code_idx]] = [str(swc[self.store_id_idx])]

        return store_ids_by_code


    def _get_weather_station_details(self, combined_weather_codes):

        # combined results
        results = {}

        # loop through the combined codes and break them up
        weather_codes = []
        for combined_code in combined_weather_codes:

            # get the separated codes
            precip_code, temp_code = weather_helper.parse_weather_station_code(combined_code)

            # add each code, if it's not empty
            if precip_code:
                weather_codes.append(precip_code)
            if temp_code:
                weather_codes.append(temp_code)

            # add the base formatted look up record to the results
            results[combined_code] = {
                "temp_station_code": temp_code,
                "precip_station_code": precip_code
            }

        # dedupe the weather codes
        unique_weather_codes = list(set(weather_codes))

        # query these weather stations
        query = { "data.code": { "$in": unique_weather_codes }}
        entity_fields = ["name", "data.code", "data.latitude", "data.longitude", "data.state"]
        params = self.main_param.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]
        weather_stations = self.main_access.mds.call_find_entities_raw("weather_station", params)

        # convert these weather stations into a dictionary by code
        weather_stations = convert_entity_list_to_dictionary(weather_stations, lambda ws: ws["data"]["code"])

        # create the default empty station record for easy lookups (so that we don't have to do a ton of dict.get(....., ....)
        empty_station_record = self._return_empty_station_details()

        # loop through the base results and append the weather station details
        for combined_code in results:

            # helper vars
            formatted_record = results[combined_code]
            temp_station_details = weather_stations.get(formatted_record["temp_station_code"], empty_station_record)
            precip_station_details = weather_stations.get(formatted_record["precip_station_code"], empty_station_record)

            # add details to formatted record
            formatted_record["temp_station_name"] = temp_station_details["name"]
            formatted_record["temp_station_state"] = temp_station_details["data"]["state"]
            formatted_record["temp_station_latitude"] = temp_station_details["data"]["latitude"]
            formatted_record["temp_station_longitude"] = temp_station_details["data"]["longitude"]
            formatted_record["precip_station_name"] = precip_station_details["name"]
            formatted_record["precip_station_state"] = precip_station_details["data"]["state"]
            formatted_record["precip_station_latitude"] = precip_station_details["data"]["latitude"]
            formatted_record["precip_station_longitude"] = precip_station_details["data"]["longitude"]

        return results


    def _return_empty_station_details(self):
        return {
            "name": "",
            "data": {
                "code": "",
                "latitude": "",
                "longitude": "",
                "state": ""
            }
        }

    def _combine_prior_and_current_weather(self, prior_period_weather, current_period_weather):

        # make the current period_weather into a dictionary so that it's a fast look up
        current_weather_dict = convert_entity_list_to_dictionary(current_period_weather)

        # need to create a new list to keep the items, because some stores won't qualify
        qualified_store_weather = []

        # loop through the prior_period_weather, since that one has all the base weather info
        for prior_weather in prior_period_weather:

            # get some variables
            weather_code = prior_weather["_id"]

            # only proceed if the weather code is in both current and prior
            current_weather = current_weather_dict.get(weather_code, None)
            if current_weather:

                # get the correct structure
                store_weather_rec = {
                    "_id": weather_code,
                    "prior_temp_avg": prior_weather["temp_avg"],
                    "current_temp_avg": current_weather["temp_avg"],
                    "prior_temp_min": prior_weather["temp_min"],
                    "current_temp_min": current_weather["temp_min"],
                    "prior_temp_max": prior_weather["temp_max"],
                    "current_temp_max": current_weather["temp_max"],
                    "prior_precip_avg": prior_weather["precip_avg"],
                    "current_precip_avg": current_weather["precip_avg"],
                    "prior_precip_min": prior_weather["precip_min"],
                    "current_precip_min": current_weather["precip_min"],
                    "prior_precip_max": prior_weather["precip_max"],
                    "current_precip_max": current_weather["precip_max"],
                    "prior_precip_days": prior_weather["precip_days"],
                    "current_precip_days": current_weather["precip_days"],
                    "prior_weather_days": prior_weather["weather_days"],
                    "current_weather_days": current_weather["weather_days"],
                }

                # EDGE CASE: when we have no min/max values, mongo returns the aggregate average as 0.0.
                # This function normalizes that to None, so that the min/max functions work correctly
                self._normalize_aggregate_nulls(store_weather_rec)

                # calc % changes after normalization since these depend on Nones
                store_weather_rec["temp_avg_percent_change"] = self._get_percent_change(store_weather_rec["prior_temp_avg"], store_weather_rec["current_temp_avg"])
                store_weather_rec["temp_min_percent_change"] = self._get_percent_change(store_weather_rec["prior_temp_min"], store_weather_rec["current_temp_min"])
                store_weather_rec["temp_max_percent_change"] = self._get_percent_change(store_weather_rec["prior_temp_max"], store_weather_rec["current_temp_max"])
                store_weather_rec["precip_avg_percent_change"] = self._get_percent_change(store_weather_rec["prior_precip_avg"], store_weather_rec["current_precip_avg"])
                store_weather_rec["precip_min_percent_change"] = self._get_percent_change(store_weather_rec["prior_precip_min"], store_weather_rec["current_precip_min"])
                store_weather_rec["precip_max_percent_change"] = self._get_percent_change(store_weather_rec["prior_precip_max"], store_weather_rec["current_precip_max"])
                store_weather_rec["precip_days_percent_change"] = self._get_percent_change(store_weather_rec["prior_precip_days"], store_weather_rec["current_precip_days"])

                qualified_store_weather.append(store_weather_rec)

        return qualified_store_weather

    def _combine_store_fields_and_format_for_ui(self, combined_results, store_ids_by_code, weather_code_by_store, weather_station_details_by_code):

        # get a list of all store ids from the combined results - translate from weather code to mapped store ids here
        store_ids = []
        for weather_data in combined_results:
            weather_code = weather_data["_id"]
            store_ids.extend(store_ids_by_code[weather_code])

        if not store_ids:
            return []

        # create the params
        query = { "data.store_id": { "$in": store_ids }}
        entity_fields = ["data.company_name", "data.street_number", "data.street", "data.suite", "data.city", "data.state", "data.zip", "data.phone",
                         "data.store_opened_date", "data.store_closed_date", "data.store_id"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=entity_fields)["params"]

        # get data from trade areas
        # note: we can switch this to store once we finish denormalizing address info into stores (via trade area upserter)
        trade_areas = self.main_access.mds.call_find_entities_raw("trade_area", params, encode_and_decode_results=False)

        if not trade_areas:
            return []

        # make a mapping of combined results weather by weather code to help lookups
        weather_data_by_code = convert_entity_list_to_dictionary(combined_results)

        # expand the station-level results to store-level, so that 2 stores using the same station become 2 rows of data
        store_level_results = []
        for trade_area in trade_areas:

            # semantic vars
            store_id = trade_area["data"]["store_id"]
            weather_code = weather_code_by_store[store_id]["weather_code"]
            temp_station_distance = weather_code_by_store[store_id]["temp_station_distance"]
            precip_station_distance = weather_code_by_store[store_id]["precip_station_distance"]
            weather_station_details = weather_station_details_by_code[weather_code]

            # initialize rec with a copy of the related weather data
            store_weather_rec = weather_data_by_code[weather_code].copy()

            # switch _id to store_id, and add weather_code as weather station for now...
            store_weather_rec["_id"] = store_id
            store_weather_rec["weather_station"] = ", ".join(weather_helper.parse_weather_station_code(weather_code))

            # add in distances
            store_weather_rec["temp_station_distance"] = temp_station_distance
            store_weather_rec["precip_station_distance"] = precip_station_distance

            # add the store level fields
            store_weather_rec["company_name"] = trade_area["data"]["company_name"]
            store_weather_rec["street_number"] = trade_area["data"]["street_number"]
            store_weather_rec["street"] = trade_area["data"]["street"]
            store_weather_rec["suite"] = trade_area["data"]["suite"]
            store_weather_rec["city"] = trade_area["data"]["city"]
            store_weather_rec["state"] = trade_area["data"]["state"]
            store_weather_rec["zip"] = trade_area["data"]["zip"]
            store_weather_rec["phone_number"] = trade_area["data"]["phone"]
            store_weather_rec["store_opened"] = trade_area["data"]["store_opened_date"]
            store_weather_rec["store_closed"] = trade_area["data"]["store_closed_date"]

            # add the weather station details
            store_weather_rec["temp_station_code"] = weather_station_details["temp_station_code"]
            store_weather_rec["temp_station_name"] = weather_station_details["temp_station_name"]
            store_weather_rec["temp_station_state"] = weather_station_details["temp_station_state"]
            store_weather_rec["temp_station_latitude"] = weather_station_details["temp_station_latitude"]
            store_weather_rec["temp_station_longitude"] = weather_station_details["temp_station_longitude"]
            store_weather_rec["precip_station_code"] = weather_station_details["precip_station_code"]
            store_weather_rec["precip_station_name"] = weather_station_details["precip_station_name"]
            store_weather_rec["precip_station_state"] = weather_station_details["precip_station_state"]
            store_weather_rec["precip_station_latitude"] = weather_station_details["precip_station_latitude"]
            store_weather_rec["precip_station_longitude"] = weather_station_details["precip_station_longitude"]

            store_level_results.append(store_weather_rec)

        # l'chaim
        return store_level_results

    def _calculate_summary(self, full_data):
        """
        Statistical summary of store-level weather data that has been aggregated over two time periods.
        Computes min, max, and average of min, max, avg prior and current temp and precip. Say that 5 times fast.
        """
        if not full_data:
            return None

        summary = {}

        # section 1: min, max, avg of current & prior temp and precip aggregates
        aggregates = ["min", "max", "avg"]
        vars = ["prior_temp", "current_temp", "prior_precip", "current_precip"]
        for agg_outer in aggregates:
            for var in vars:
                for agg_inner in aggregates:

                    stat = None
                    values_key = "{}_{}".format(var, agg_inner)

                    # remove None values
                    values = [fd[values_key] for fd in full_data if fd[values_key] is not None]

                    # make sure the array is not empty before converting to a numpy array, which doesn't deal with 0s well.
                    if values:

                        # convert to num py array
                        values = np.array(values, float)

                        # get agg stat
                        if agg_outer == "min":
                            stat = np.min(values)
                        elif agg_outer == "max":
                            stat = np.max(values)
                        elif agg_outer == "avg":
                            stat = np.mean(values)

                    final_key = "{}_{}_{}".format(agg_outer, var, agg_inner)
                    summary[final_key] = stat


        # section 2: min, max, avg of current & prior precip days
        vars = ["prior_precip_days", "current_precip_days"]
        for agg_outer in aggregates:
            for var in vars:

                stat = None

                # remove None values
                values = [fd[var] for fd in full_data if fd[var] is not None]

                # make sure the array is not empty before converting to a numpy array, which doesn't deal with 0s well.
                if values:

                    # convert to num py array
                    values = np.array(values, float)

                    # get agg stat
                    if agg_outer == "min":
                        stat = np.min(values)
                    elif agg_outer == "max":
                        stat = np.max(values)
                    elif agg_outer == "avg":
                        stat = np.mean(values)

                final_key = "{}_{}".format(agg_outer, var)
                summary[final_key] = stat

        # section 3: percent change for temp & precip
        vars = ["temp", "precip"]
        for agg_outer in aggregates:
            for var in vars:
                for agg_inner in aggregates:

                    prior_stat_key = "{}_prior_{}_{}".format(agg_outer, var, agg_inner)
                    current_stat_key = "{}_current_{}_{}".format(agg_outer, var, agg_inner)

                    prior_stat = summary[prior_stat_key]
                    current_stat = summary[current_stat_key]

                    percent_change = self._get_percent_change(prior_stat, current_stat)
                    final_key = "{}_{}_{}_change".format(agg_outer, var, agg_inner)
                    summary[final_key] = percent_change

        # section 4: percent change for precip days
        for agg in aggregates:

            prior_stat_key = "{}_prior_precip_days".format(agg)
            current_stat_key = "{}_current_precip_days".format(agg)

            prior_stat = summary[prior_stat_key]
            current_stat = summary[current_stat_key]

            percent_change = self._get_percent_change(prior_stat, current_stat)
            final_key = "{}_precip_days_change".format(agg)
            summary[final_key] = percent_change

        return summary

    def _calculate_coverage(self, full_data, current_time_period, prior_time_period):
        """
        Computes percent coverage for both prior and current period.
        """
        # first determine how many total days there were in each period
        # this will be the coverage denominator

        coverage = {}

        prior_start = self.date_parser.parse_date(prior_time_period[0])
        prior_end = self.date_parser.parse_date(prior_time_period[1])
        current_start = self.date_parser.parse_date(current_time_period[0])
        current_end = self.date_parser.parse_date(current_time_period[1])

        total_days = [(prior_end - prior_start).days + 1, (current_end - current_start).days + 1]

        # iterate variables and calc coverage per period
        vars = ["prior_weather_days", "current_weather_days"]
        for idx, var in enumerate(vars):

            weather_days_by_store = np.array([0. if fd[var] is None else fd[var] for fd in full_data], float)
            days_in_period = total_days[idx]

            coverage_by_store = weather_days_by_store / days_in_period
            percent_coverage = np.mean(coverage_by_store) * 100.0

            final_key = var.replace("_days", "_coverage")
            coverage[final_key] = percent_coverage

        return coverage

    def _get_store_weather_info(self, banner_ids, current_time_period, prior_time_period):
        """
        Retrieve store_ids and weather codes from MDS given a list of banners and time periods.
        Only gets stores that were alive during BOTH current and prior time periods. So, "comp stores".
        Uses as_list to save some dict creation overhead.
        Also gets station distances in meters.
        """
        query = {
            "data.company_id": {"$in": banner_ids},
            "$and": [
                {"$or": live_entity_filter__existed_within(current_time_period[0], current_time_period[1], "interval")},
                {"$or": live_entity_filter__existed_within(prior_time_period[0], prior_time_period[1], "interval")}
            ]
        }
        fields = ["_id", "data.weather_code", "data.temp_station_distance", "data.precip_station_distance"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True, use_new_json_encoder=True)["params"]
        return self.main_access.mds.call_find_entities_raw("store", params, encode_and_decode_results=False)

    def _get_weather_aggregates(self, weather_codes, time_period, temp_field, precip_field, context):

        pipeline = [
            {
                "$match": {
                    "code": {"$in": list(weather_codes)},
                    "d": {"$gte":  time_period[0], "$lte": time_period[1]}
                }
            },
            {
                "$group": {
                    "_id": "$code",

                    # easy cheesy
                    "temp_min": {"$min": "${}".format(temp_field)},
                    "temp_max": {"$max": "${}".format(temp_field)},
                    "temp_avg": {"$avg": "${}".format(temp_field)},
                    "precip_min": {"$min": "${}".format(precip_field)},
                    "precip_max": {"$max": "${}".format(precip_field)},
                    "precip_avg": {"$avg": "${}".format(precip_field)},

                    # sum up 1 precip day for anything but a null or 0
                    "precip_days": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        { "$ne": ["${}".format(precip_field), 0] },
                                        { "$ne": ["${}".format(precip_field), None] }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },

                    # sum up days with any weather (temp or precip) - used to compute coverage
                    "weather_days": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$or": [
                                        {
                                            "$and": [
                                                { "$ne": ["${}".format(precip_field), 0] },
                                                { "$ne": ["${}".format(precip_field), None] }
                                            ]
                                        },
                                        {
                                            "$and": [
                                                { "$ne": ["${}".format(temp_field), 0] },
                                                { "$ne": ["${}".format(temp_field), None] }
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                }
            }
        ]

        results = self.main_access.mds.call_aggregate_entities("weather", pipeline, context=context)

        return results

    def _get_station_data(self, weather_codes):
        """
        Look up weather station data (name, long/lat, country, state)
        based on precip_temp combo codes, which are underscore-delimited, eg US1ORMT0006_USC00356750
        """
        results = []

        temp_station_codes = set([weather_helper.parse_weather_station_code(wc)[0] for wc in weather_codes if weather_helper.parse_weather_station_code(wc)])
        precip_station_codes = set([weather_helper.parse_weather_station_code(wc)[1] for wc in weather_codes if weather_helper.parse_weather_station_code(wc)])
        station_codes = temp_station_codes | precip_station_codes

        if station_codes:

            query = {
                "data.code": {
                    "$in": list(weather_codes)
                }
            }
            fields = ["_id", "name", "data.code", "data.latitude", "data.longitude", "data.country", "data.state"]
            sort = [["d", 1]]
            params = self.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                       entity_fields=fields, sort=sort, as_list=True)["params"]
            results = self.main_access.mds.call_find_entities_raw("weather_station", params, encode_and_decode_results=False, use_new_json_encoder=True)

        return results

    def _format_cached_data_for_ui(self, rows):
        """
        need to format the cached dicts into arrays
        """
        ui_formatted_data = []

        # cycle through records
        if rows:
            for record in rows:

                # new nice record (i.e. formatted for UI)
                nice_record = []

                # cycle through display fields (internal though)
                for internal_field in self.weather_fields_internal:

                    value = record[internal_field]

                    # make sure dates are formatted nicely
                    if (internal_field == "store_opened" or internal_field == "store_closed") and value:
                        value = value[:10]

                    nice_record.append(value)

                ui_formatted_data.append(nice_record)

        return ui_formatted_data

    def _get_dates_in_range(self, time_period):
        """
        This gets a list that can be used with an $in clause for the time period.
        We're running the query this way because of mongodb limitations of multi-key indexes
        """

        # create base vars
        start_date = time_period[0]
        end_date = time_period[1]
        current_date = start_date
        dates = []

        # loop and add each date
        while current_date <= end_date:

            # add date to query
            dates.append(current_date)

            # increment date
            current_date += datetime.timedelta(days = 1)

        return dates

    def _normalize_aggregate_nulls(self, weather_data):

        # EDGE CASE: when we have no min/max values, mongo returns the aggregate average as 0.0.
        # This function normalizes that to None, so that the min/max functions work correctly
        # also normalize precip days and weather_days if null

        if weather_data["prior_temp_min"] is None and weather_data["prior_temp_max"] is None:
            weather_data["prior_temp_avg"] = None

        if weather_data["current_temp_min"] is None and weather_data["current_temp_max"] is None:
            weather_data["current_temp_avg"] = None
            
        if weather_data["prior_precip_min"] is None and weather_data["prior_precip_max"] is None:
            weather_data["prior_precip_avg"] = None
            weather_data["prior_precip_days"] = None

        if weather_data["current_precip_min"] is None and weather_data["current_precip_max"] is None:
            weather_data["current_precip_avg"] = None
            weather_data["current_precip_days"] = None

        if weather_data["prior_temp_avg"] is None and weather_data["prior_precip_avg"] is None:
            weather_data["prior_weather_days"] = None

        if weather_data["current_temp_avg"] is None and weather_data["current_precip_avg"] is None:
            weather_data["current_weather_days"] = None

    @staticmethod
    def _calculate_minimum(min_variable, current_value):
        if current_value is not None and current_value < min_variable:
            return current_value
        else:
            return min_variable

    @staticmethod
    def _calculate_maximum(max_variable, current_value):
        if current_value is not None and current_value > max_variable:
            return current_value
        else:
            return max_variable

    @staticmethod
    def _calculate_average(total, num):
        if num == 0:
            return None

        return round(float(total) / num, 1)

    @staticmethod
    def _calculate_nullable_summary_averages(totals, nums, counter):

        # all numbers have to be non null to average any of them.  This is because mongo returns a null average as 0.0
        for num in nums:
            if num is None:
                return [counter] + totals

        # if we pass, above, just add up the num to each total
        for index, num in enumerate(nums):
            totals[index] += num


        # increment counter
        counter += 1

        # return new counter and new totals
        return [counter] + totals

    @staticmethod
    def _get_percent_change(prior, current):

        # None vs. None or None vs. anything: percent change should be None since it's not computable
        # this is possible because a store can have temp (or precip) in both times, but not the other
        if prior is None or current is None:
            return None

        # divide by zero prevention; this is also an "N/A" case since it's not computable
        if prior == 0:
            return None

        # get percent change (t1 - t0) / t0 = (t1 / t0) - 1
        percent_change = float(current - prior) / prior

        # multiply by 100 and get 2 decimal point only
        return round(percent_change * 100, 2)

    @staticmethod
    def _get_temp_precip_fields(units):

        # figure out units
        if units == "metric":
            temp_units = "c"
            precip_units = "mm"
        else:
            temp_units = "f"
            precip_units = "in"

        # construct fields
        temp_field = "t{}mean".format(temp_units)
        precip_field = "p{}".format(precip_units)

        # return fields
        return temp_field, precip_field

    def _fix_user_params(self, user_params):

        # this allows the sort index to be both a string field and an int index
        if user_params and "output" in user_params and user_params["output"]["sort"]:

            sort_column = user_params["output"]["sort"][0][0]
            sort_direction =  user_params["output"]["sort"][0][1]

            # if sort column is an int, convert it to the field
            if isinstance(sort_column, int):
                sort_column = self.weather_fields_internal[sort_column]

            # reset the sort
            user_params["output"]["sort"] = [[sort_column, sort_direction]]

    def _get_cache_rec(self, banner_ids, current_time_period, prior_time_period, units):

        # create base rec with meta data and our inputs
        cache_params = {"options": { "has_metadata": True }}
        cache_rec = self._make_cache_rec(["store_weather"], "WeatherEndpoints.run_api_weather_stores.details", 'tabular', params = cache_params)

        # add params
        cache_rec["params"] = {
            "banner_ids": banner_ids,
            "current_time_period": current_time_period,
            "prior_time_period": prior_time_period,
            "units": units
        }

        return cache_rec

    def _create_nice_meta(self, cache_meta, user_params):

        # get sort index
        sort_index = 0
        sort_direction = 1
        if user_params and user_params["output"] and user_params["output"]["sort"]:
            sort = user_params["output"]["sort"][0]
            sort_index = self.weather_fields_internal.index(sort[0])
            sort_direction = sort[1]

        return {
            "page_index": cache_meta.get("page_index", -1),
            "page_size": cache_meta.get("page_size", -1),
            "num_rows": cache_meta["num_rows"],
            "sort_index": sort_index,
            "sort_direction": sort_direction
        }

    def _validate_and_parse_inputs(self, current_time_period, prior_time_period, units):

        # parse and validate time periods
        current_time_period = self._parse_time_period(current_time_period)
        prior_time_period = self._parse_time_period(prior_time_period)

        # verify that the units has one of the allowed values
        if units not in self.allowed_units:
            raise ValueError("Units must be metric or us")

        return current_time_period, prior_time_period, units

    def _parse_time_period(self, time_period):

        if isinstance(time_period, list) and len(time_period) == 2 and time_period[0] and time_period[1]:

            # if good, return an array of the parsed dates
            return [self.date_parser.parse_date(time_period[0]), self.date_parser.parse_date(time_period[1])]

        else:
            raise ValueError("Time period must be a list of two dates")