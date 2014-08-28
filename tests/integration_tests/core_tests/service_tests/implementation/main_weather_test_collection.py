from common.utilities.inversion_of_control import Dependency
from core.service.svc_main.implementation.service_endpoints.weather_endpoints import WeatherEndpoints
from geoprocessing.geoprocessors.weather.gp16_get_store_weather import GP16GetStoreWeather
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area, select_trade_area, insert_test_store, insert_test_weather, insert_test_company, insert_test_weather_station_mongo
from tests.integration_tests.utilities.data_access_misc_queries_postgres import purge_weather_tables, insert_test_weather_station, insert_test_weather_var, insert_test_point_data, insert_test_source_file
import numpy as np
import datetime

__author__ = "erezrubinstein"

class MainWeatherTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = "test@nexusri.com"
        self.source = "main_plan_b_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # get some dependencies
        self.main_param = Dependency("CoreAPIParamsBuilder").value

        # create a version of the endpoints to test specific methods
        self.main_weather_endpoints = WeatherEndpoints(None, None)

    def setUp(self):

        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

        # reset the postgres data
        purge_weather_tables()


    def tearDown(self):
        pass



    # -------------------- Begin Tests -------------------- #

    def test_run_api_weather_stores(self):

        # create stores
        store_id_1 = insert_test_store("company_id_1", None)
        store_id_2 = insert_test_store("company_id_1", None)
        store_id_3 = insert_test_store("company_id_1", None)

        # create three trade_areas, each one matching it's appropriate station
        trade_area_id_1 = insert_test_trade_area(store_id_1, company_id="company_id_1", city="city_1", state="state_1", company_name="company_name_1", latitude=40, longitude=-80)
        trade_area_id_2 = insert_test_trade_area(store_id_2, company_id="company_id_1", city="city_2", state="state_2", company_name="company_name_1", latitude=30, longitude=-75)
        trade_area_id_3 = insert_test_trade_area(store_id_3, company_id="company_id_1", city="city_3", state="state_3", company_name="company_name_1", latitude=20, longitude=-70)

        # create three weather stations in postgres
        station_1_id = insert_test_weather_station("station1", 40, -80)
        station_2_id = insert_test_weather_station("station2", 30, -75)
        station_3_id = insert_test_weather_station("station3", 20, -70)

        # insert weather stations into mongo
        insert_test_weather_station_mongo("station1", "station_name", station_1_id, 40, -80)
        insert_test_weather_station_mongo("station2", "station_name", station_2_id, 30, -75)
        insert_test_weather_station_mongo("station3", "station_name", station_3_id, 20, -70)

        # insert weather vars for precipitation and tmin/tmax
        t_min_var_id = insert_test_weather_var("TMIN")
        t_max_var_id = insert_test_weather_var("TMAX")
        precip_var_id = insert_test_weather_var("PRCP")

        source_file_id = insert_test_source_file("jomamma")

        # create three point data (t-min, t-max, precip) entries for each weather station per day
        # station 1
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-07", 0, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-07", 20, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-07", 30, source_file_id)
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-08", 40, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-08", 60, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-08", 70, source_file_id)
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-09", 80, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-09", 100, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-09", 110, source_file_id)
        # station 2
        insert_test_point_data(t_min_var_id, station_2_id, "2013-11-07", 100, source_file_id)
        insert_test_point_data(t_max_var_id, station_2_id, "2013-11-07", 120, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-07", 130, source_file_id)
        insert_test_point_data(t_min_var_id, station_2_id, "2013-11-08", 140, source_file_id)
        insert_test_point_data(t_max_var_id, station_2_id, "2013-11-08", 160, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-08", 170, source_file_id)
        insert_test_point_data(t_min_var_id, station_2_id, "2013-11-09", 180, source_file_id)
        insert_test_point_data(t_max_var_id, station_2_id, "2013-11-09", 200, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-09", 210, source_file_id)
        # station 3
        insert_test_point_data(t_min_var_id, station_3_id, "2013-11-07", 220, source_file_id)
        insert_test_point_data(t_max_var_id, station_3_id, "2013-11-07", 240, source_file_id)
        insert_test_point_data(precip_var_id, station_3_id, "2013-11-07", 250, source_file_id)
        insert_test_point_data(t_min_var_id, station_3_id, "2013-11-08", 260, source_file_id)
        insert_test_point_data(t_max_var_id, station_3_id, "2013-11-08", 280, source_file_id)
        insert_test_point_data(precip_var_id, station_3_id, "2013-11-08", 290, source_file_id)
        insert_test_point_data(t_min_var_id, station_3_id, "2013-11-09", 300, source_file_id)
        insert_test_point_data(t_max_var_id, station_3_id, "2013-11-09", 320, source_file_id)
        insert_test_point_data(precip_var_id, station_3_id, "2013-11-09", 330, source_file_id)

        # run gp 16 on all of those trade areas
        GP16GetStoreWeather().process_object(select_trade_area(trade_area_id_1))
        GP16GetStoreWeather().process_object(select_trade_area(trade_area_id_2))
        GP16GetStoreWeather().process_object(select_trade_area(trade_area_id_3))

        # DO NOT UNCOMMENT/DELETE THE BELOW.
        # it's how you would insert it if we didn't run GP16.  It helped calculating the below numbers
        # create three store_weather/trade_area records for store 1, company 1
        #sw_1_1_1 = insert_test_store_weather("store_id_1", "company_id_1", "station1", "2013-11-07", 1, 33.8, 3, 0.11811)
        #sw_1_1_2 = insert_test_store_weather("store_id_1", "company_id_1", "station1", "2013-11-08", 5, 41, 7, 0.275591)
        #sw_1_1_3 = insert_test_store_weather("store_id_1", "company_id_1", "station1", "2013-11-09", 9, 48.2, 11, 0.433071)
        #
        ## create three stores_weather/trade_area records for store 2, company 1
        #sw_1_2_1 = insert_test_store_weather("store_id_2", "company_id_1", "station2", "2013-11-07", 11, 51.8, 13, 0.511811)
        #sw_1_2_2 = insert_test_store_weather("store_id_2", "company_id_1", "station2", "2013-11-08", 15, 59, 17, 0.669291)
        #sw_1_2_3 = insert_test_store_weather("store_id_2", "company_id_1", "station2", "2013-11-09", 19, 66.2, 21, 0.826772)
        #
        ## create three stores_weather/trade_area records for store 3, company 1
        #sw_1_3_1 = insert_test_store_weather("store_id_3", "company_id_1", "station3", "2013-11-07", 23, 73.4, 25, 0.984252)
        #sw_1_3_2 = insert_test_store_weather("store_id_3", "company_id_1", "station3", "2013-11-08", 27, 80.6, 29, 1.14173)
        #sw_1_3_3 = insert_test_store_weather("store_id_3", "company_id_1", "station3", "2013-11-09", 31, 87.8, 33, 1.29921)

        # create common input params for all the queries
        banner_ids = ["company_id_1"]
        prior_time_period = ["2013-11-07", "2013-11-08"]
        current_time_period = ["2013-11-09", "2013-11-09"]
        units = "metric"

        # get first two rows in reverse order
        user_params = {
            "output": {
                "page": {
                    "size": 2,
                    "index": 0
                },
                "sort": [[4, -1]]
            }
        }
        results = self.main_access.call_get_store_weather_data(banner_ids, current_time_period, prior_time_period, units, user_params, True)

        # round summary data to nearest tenth for comparison
        for k, v in results["summary"].iteritems():
            results["summary"][k] = round(v, 1)

        # compare (calculated myself)
        self.test_case.assertEqual(results, {
            "results": [
                self._create_combined_store_data(3, 1, 25, 31, 23, 31, 27, 31, 27, 33, 25, 33, 29, 33, 2, 1, 24, 34.78, 14.81, 22.22, 32, 13.79, -50, "station3, station3",
                                                 0.0, 0.0, "station_name", "station3", "NY", 20, -70, "station_name", "station3", "NY", 20, -70),
                self._create_combined_store_data(2, 1, 13, 19, 11, 19, 15, 19, 15, 21, 13, 21, 17, 21, 2, 1, 46.15, 72.73, 26.67, 40, 61.54, 23.53, -50, "station2, station2",
                                                 0.0, 0.0, "station_name", "station2", "NY", 30, -75, "station_name", "station2", "NY", 30, -75)
            ],
            "field_list": [
                "Banner", "Street Number", "Street", "Suite", "State", "City", "Zip", "Phone Number", "Store Opened", "Store Closed", "Weather\nStations",

                # Average Columns
                "Current\nAvg of Daily\nAvg Temp (&deg;C)",
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)",
                "% Change\nAvg of Daily\nAvg Temp",
                "Current\nAvg of Daily\nPrecip (cm)",
                "Prior\nAvg of Daily\nPrecip (cm)",
                "% Change\nAvg of Daily\nPrecip",

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)",
                "Prior\nMin of Daily\nAvg Temp (&deg;C)",
                "% Change\nMin of Daily\nAvg Temp",
                "Current\nMin of Daily\nPrecip (cm)",
                "Prior\nMin of Daily\nPrecip (cm)",
                "% Change\nMin of Daily\nPrecip",

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)",
                "Prior\nMax of Daily\nAvg Temp (&deg;C)",
                "% Change\nMax of Daily\nAvg Temp",
                "Current\nMax of Daily\nPrecip (cm)",
                "Prior\nMax of Daily\nPrecip (cm)",
                "% Change\nMax of Daily\nPrecip",

                # Precip Days Columns
                "Current\nPrecip Days",
                "Prior\nPrecip Days",
                "% Change\nPrecip Days",

                # station details
                "Temp Station\nName", "Temp Station\nCode", "Temp Station\nState", "Temp Station\nDistance (km)", "Temp Station\nLatitude", "Temp Station\nLongitude",
                "Precip Station\nName", "Precip Station\nCode", "Precip Station\nState", "Precip Station\nDistance (km)", "Precip Station\nLatitude", "Precip Station\nLongitude"
            ],
            "field_meta": {
                "Current\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Precip Days Columns
                "Current\nPrecip Days": { "type": "number", "decimals": 5 },
                "Prior\nPrecip Days": { "type": "number", "decimals": 5 },
                "% Change\nPrecip Days": { "type": "percent", "decimals": 2 },

                "Temp Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Temp Station\nLatitude": { "type": "number", "decimals": 5 },
                "Temp Station\nLongitude": { "type": "number", "decimals": 5 },
                "Precip Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Precip Station\nLatitude": { "type": "number", "decimals": 5 },
                "Precip Station\nLongitude": { "type": "number", "decimals": 5 },
            },
            "meta": {
                "page_index": 0,
                "page_size": 2,
                "num_rows": 3,
                "sort_index": 4,
                "sort_direction": -1
            },
            "summary": {
                "min_prior_temp_min": 1,
                "min_prior_temp_avg": 3,
                "min_prior_temp_max": 5,
                "avg_prior_temp_min": 11.7,
                "avg_prior_temp_avg": 13.7,
                "avg_prior_temp_max": 15.7,
                "max_prior_temp_min": 23,
                "max_prior_temp_avg": 25,
                "max_prior_temp_max": 27,
                "min_prior_precip_min": 3,
                "min_prior_precip_avg": 5,
                "min_prior_precip_max": 7,
                "avg_prior_precip_min": 13.7,
                "avg_prior_precip_avg": 15.7,
                "avg_prior_precip_max": 17.7,
                "max_prior_precip_min": 25,
                "max_prior_precip_avg": 27,
                "max_prior_precip_max": 29,
                "min_current_temp_min": 9,
                "min_current_temp_avg": 9,
                "min_current_temp_max": 9,
                "avg_current_temp_min": 19.7,
                "avg_current_temp_avg": 19.7,
                "avg_current_temp_max": 19.7,
                "max_current_temp_min": 31,
                "max_current_temp_avg": 31,
                "max_current_temp_max": 31,
                "min_current_precip_min": 11,
                "min_current_precip_avg": 11,
                "min_current_precip_max": 11,
                "avg_current_precip_min": 21.7,
                "avg_current_precip_avg": 21.7,
                "avg_current_precip_max": 21.7,
                "max_current_precip_min": 33,
                "max_current_precip_avg": 33,
                "max_current_precip_max": 33,
                "min_prior_precip_days": 2,
                "avg_prior_precip_days": 2,
                "max_prior_precip_days": 2,
                "min_current_precip_days": 1,
                "avg_current_precip_days": 1,
                "max_current_precip_days": 1,

                # percent diffs
                "min_temp_min_change": 800,
                "min_temp_avg_change": 200,
                "min_temp_max_change": 80,
                "avg_temp_min_change": 68.6,
                "avg_temp_avg_change": 43.9,
                "avg_temp_max_change": 25.5,
                "max_temp_min_change": 34.8,
                "max_temp_avg_change": 24,
                "max_temp_max_change": 14.8,
                "min_precip_min_change": 266.7,
                "min_precip_avg_change": 120,
                "min_precip_max_change": 57.1,
                "avg_precip_min_change": 58.5,
                "avg_precip_avg_change": 38.3,
                "avg_precip_max_change": 22.6,
                "max_precip_min_change": 32,
                "max_precip_avg_change": 22.2,
                "max_precip_max_change": 13.8,
                "min_precip_days_change": -50,
                "avg_precip_days_change": -50,
                "max_precip_days_change": -50
            },
            "coverage": {
                "current_weather_coverage": 100.0,
                "prior_weather_coverage": 100.0
            }
        })

        # get the last item in reverse order
        user_params = {
            "output": {
                "page": {
                    "size": 2,
                    "index": 1
                },
                "sort": [[4, -1]]
            }
        }
        results = self.main_access.call_get_store_weather_data(banner_ids, current_time_period, prior_time_period, units, user_params, True)

        # round summary data to nearest tenth for comparison
        for k, v in results["summary"].iteritems():
            results["summary"][k] = round(v, 1)

        # compare (calculated myself)
        self.test_case.assertEqual(results, {
            "results": [
                self._create_combined_store_data(1, 1, 3, 9, 1, 9, 5, 9, 5, 11, 3, 11, 7, 11, 2, 1, 200, 800, 80, 120, 266.67, 57.14, -50, "station1, station1",
                                                 0.0, 0.0, "station_name", "station1", "NY", 40, -80, "station_name", "station1", "NY", 40, -80)
            ],
            "field_list": [
                "Banner", "Street Number", "Street", "Suite", "State", "City", "Zip", "Phone Number", "Store Opened", "Store Closed", "Weather\nStations",

                # Average Columns
                "Current\nAvg of Daily\nAvg Temp (&deg;C)",
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)",
                "% Change\nAvg of Daily\nAvg Temp",
                "Current\nAvg of Daily\nPrecip (cm)",
                "Prior\nAvg of Daily\nPrecip (cm)",
                "% Change\nAvg of Daily\nPrecip",

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)",
                "Prior\nMin of Daily\nAvg Temp (&deg;C)",
                "% Change\nMin of Daily\nAvg Temp",
                "Current\nMin of Daily\nPrecip (cm)",
                "Prior\nMin of Daily\nPrecip (cm)",
                "% Change\nMin of Daily\nPrecip",

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)",
                "Prior\nMax of Daily\nAvg Temp (&deg;C)",
                "% Change\nMax of Daily\nAvg Temp",
                "Current\nMax of Daily\nPrecip (cm)",
                "Prior\nMax of Daily\nPrecip (cm)",
                "% Change\nMax of Daily\nPrecip",

                # Precip Days Columns
                "Current\nPrecip Days",
                "Prior\nPrecip Days",
                "% Change\nPrecip Days",

                # station details
                "Temp Station\nName", "Temp Station\nCode", "Temp Station\nState", "Temp Station\nDistance (km)", "Temp Station\nLatitude", "Temp Station\nLongitude",
                "Precip Station\nName", "Precip Station\nCode", "Precip Station\nState", "Precip Station\nDistance (km)", "Precip Station\nLatitude", "Precip Station\nLongitude"
            ],
            "field_meta": {
                "Current\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Precip Days Columns
                "Current\nPrecip Days": { "type": "number", "decimals": 5 },
                "Prior\nPrecip Days": { "type": "number", "decimals": 5 },
                "% Change\nPrecip Days": { "type": "percent", "decimals": 2 },

                "Temp Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Temp Station\nLatitude": { "type": "number", "decimals": 5 },
                "Temp Station\nLongitude": { "type": "number", "decimals": 5 },
                "Precip Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Precip Station\nLatitude": { "type": "number", "decimals": 5 },
                "Precip Station\nLongitude": { "type": "number", "decimals": 5 },
            },
            "meta": {
                "page_index": 1,
                "page_size": 2,
                "num_rows": 3,
                "sort_index": 4,
                "sort_direction": -1
            },
            "summary": {
                "min_prior_temp_min": 1,
                "min_prior_temp_avg": 3,
                "min_prior_temp_max": 5,
                "avg_prior_temp_min": 11.7,
                "avg_prior_temp_avg": 13.7,
                "avg_prior_temp_max": 15.7,
                "max_prior_temp_min": 23,
                "max_prior_temp_avg": 25,
                "max_prior_temp_max": 27,
                "min_prior_precip_min": 3,
                "min_prior_precip_avg": 5,
                "min_prior_precip_max": 7,
                "avg_prior_precip_min": 13.7,
                "avg_prior_precip_avg": 15.7,
                "avg_prior_precip_max": 17.7,
                "max_prior_precip_min": 25,
                "max_prior_precip_avg": 27,
                "max_prior_precip_max": 29,
                "min_current_temp_min": 9,
                "min_current_temp_avg": 9,
                "min_current_temp_max": 9,
                "avg_current_temp_min": 19.7,
                "avg_current_temp_avg": 19.7,
                "avg_current_temp_max": 19.7,
                "max_current_temp_min": 31,
                "max_current_temp_avg": 31,
                "max_current_temp_max": 31,
                "min_current_precip_min": 11,
                "min_current_precip_avg": 11,
                "min_current_precip_max": 11,
                "avg_current_precip_min": 21.7,
                "avg_current_precip_avg": 21.7,
                "avg_current_precip_max": 21.7,
                "max_current_precip_min": 33,
                "max_current_precip_avg": 33,
                "max_current_precip_max": 33,
                "min_prior_precip_days": 2,
                "avg_prior_precip_days": 2,
                "max_prior_precip_days": 2,
                "min_current_precip_days": 1,
                "avg_current_precip_days": 1,
                "max_current_precip_days": 1,

                # percent change
                "min_temp_min_change": 800,
                "min_temp_avg_change": 200,
                "min_temp_max_change": 80,
                "avg_temp_min_change": 68.6,
                "avg_temp_avg_change": 43.9,
                "avg_temp_max_change": 25.5,
                "max_temp_min_change": 34.8,
                "max_temp_avg_change": 24,
                "max_temp_max_change": 14.8,
                "min_precip_min_change": 266.7,
                "min_precip_avg_change": 120,
                "min_precip_max_change": 57.1,
                "avg_precip_min_change": 58.5,
                "avg_precip_avg_change": 38.3,
                "avg_precip_max_change": 22.6,
                "max_precip_min_change": 32,
                "max_precip_avg_change": 22.2,
                "max_precip_max_change": 13.8,
                "min_precip_days_change": -50,
                "avg_precip_days_change": -50,
                "max_precip_days_change": -50
            },
            "coverage": {
                "current_weather_coverage": 100.0,
                "prior_weather_coverage": 100.0
            }
        })


        # get all results without summary
        user_params = {
            "output": {
                "page": {
                    "size": 10,
                    "index": 0
                },
                "sort": [[4, -1]]
            }
        }
        results = self.main_access.call_get_store_weather_data(banner_ids, current_time_period, prior_time_period, units, user_params)



        # compare (calculated myself)
        self.test_case.assertEqual(results, {
            "results": [
                self._create_combined_store_data(3, 1, 25, 31, 23, 31, 27, 31, 27, 33, 25, 33, 29, 33, 2, 1, 24, 34.78, 14.81, 22.22, 32, 13.79, -50, "station3, station3",
                                                 0.0, 0.0, "station_name", "station3", "NY", 20, -70, "station_name", "station3", "NY", 20, -70),
                self._create_combined_store_data(2, 1, 13, 19, 11, 19, 15, 19, 15, 21, 13, 21, 17, 21, 2, 1, 46.15, 72.73, 26.67, 40, 61.54, 23.53, -50, "station2, station2",
                                                 0.0, 0.0, "station_name", "station2", "NY", 30, -75, "station_name", "station2", "NY", 30, -75),
                self._create_combined_store_data(1, 1, 3, 9, 1, 9, 5, 9, 5, 11, 3, 11, 7, 11, 2, 1, 200, 800, 80, 120, 266.67, 57.14, -50, "station1, station1",
                                                 0.0, 0.0, "station_name", "station1", "NY", 40, -80, "station_name", "station1", "NY", 40, -80)
            ],
            "field_list": [
                "Banner", "Street Number", "Street", "Suite", "State", "City", "Zip", "Phone Number", "Store Opened", "Store Closed", "Weather\nStations",

                # Average Columns
                "Current\nAvg of Daily\nAvg Temp (&deg;C)",
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)",
                "% Change\nAvg of Daily\nAvg Temp",
                "Current\nAvg of Daily\nPrecip (cm)",
                "Prior\nAvg of Daily\nPrecip (cm)",
                "% Change\nAvg of Daily\nPrecip",

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)",
                "Prior\nMin of Daily\nAvg Temp (&deg;C)",
                "% Change\nMin of Daily\nAvg Temp",
                "Current\nMin of Daily\nPrecip (cm)",
                "Prior\nMin of Daily\nPrecip (cm)",
                "% Change\nMin of Daily\nPrecip",

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)",
                "Prior\nMax of Daily\nAvg Temp (&deg;C)",
                "% Change\nMax of Daily\nAvg Temp",
                "Current\nMax of Daily\nPrecip (cm)",
                "Prior\nMax of Daily\nPrecip (cm)",
                "% Change\nMax of Daily\nPrecip",

                # Precip Days Columns
                "Current\nPrecip Days",
                "Prior\nPrecip Days",
                "% Change\nPrecip Days",

                # station details
                "Temp Station\nName", "Temp Station\nCode", "Temp Station\nState", "Temp Station\nDistance (km)", "Temp Station\nLatitude", "Temp Station\nLongitude",
                "Precip Station\nName", "Precip Station\nCode", "Precip Station\nState", "Precip Station\nDistance (km)", "Precip Station\nLatitude", "Precip Station\nLongitude"
            ],
            "field_meta": {
                "Current\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Precip Days Columns
                "Current\nPrecip Days": { "type": "number", "decimals": 5 },
                "Prior\nPrecip Days": { "type": "number", "decimals": 5 },
                "% Change\nPrecip Days": { "type": "percent", "decimals": 2 },

                "Temp Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Temp Station\nLatitude": { "type": "number", "decimals": 5 },
                "Temp Station\nLongitude": { "type": "number", "decimals": 5 },
                "Precip Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Precip Station\nLatitude": { "type": "number", "decimals": 5 },
                "Precip Station\nLongitude": { "type": "number", "decimals": 5 },
            },
            "meta": {
                "page_index": 0,
                "page_size": 10,
                "num_rows": 3,
                "sort_index": 4,
                "sort_direction": -1
            }
        })


    def test_run_api_weather_stores__multiple_stores_per_station(self):

        # create test companies
        company_id_1 = insert_test_company(name="company_name_1", ctype="retail_banner")
        company_id_2 = insert_test_company(name="company_name_2", ctype="retail_banner")

        # create stores (one for the other company)
        store_id_1 = insert_test_store(company_id_1, None, weather_code="station1#!@station1")
        store_id_2 = insert_test_store(company_id_1, None, weather_code="station1#!@station1")
        store_id_3 = insert_test_store(company_id_1, None, weather_code="station2#!@station2")
        store_id_4 = insert_test_store(company_id_2, None, weather_code="station2#!@station2")

        # create three trade_areas, each one matching it's appropriate station  (one for the other company)
        insert_test_trade_area(store_id_1, company_id=company_id_1, city="city_1", state="state_1", company_name="company_name_1", latitude=40, longitude=-80)
        insert_test_trade_area(store_id_2, company_id=company_id_1, city="city_2", state="state_2", company_name="company_name_1", latitude=30, longitude=-75)
        insert_test_trade_area(store_id_3, company_id=company_id_1, city="city_3", state="state_3", company_name="company_name_1", latitude=20, longitude=-70)
        insert_test_trade_area(store_id_4, company_id=company_id_2, city="city_4", state="state_4", company_name="company_name_2", latitude=20, longitude=-70)

        # insert weather stations into mongo
        insert_test_weather_station_mongo("station1", "station_name", 9, 40, -80)
        insert_test_weather_station_mongo("station2", "station_name", 29, 30, -75)

        # create weather data, where two stores point at the same weather_id and one points at a different one
        # NOTE - I'm adding store_id_4 too, which is a different company to test an unwinding bug.

        # prior set:
        insert_test_weather("2013-11-07", "station1#!@station1", 1, 2, 3, 4)
        insert_test_weather("2013-11-07", "station2#!@station2", 5, 6, 7, 8)

        # current set:
        insert_test_weather("2013-11-08", "station1#!@station1", 2, 4, 6, 8)
        insert_test_weather("2013-11-08", "station2#!@station2", 10, 12, 14, 16)

        # create the inputs for the report
        banner_ids = [company_id_1]
        prior_time_period = ["2013-11-07", "2013-11-07"]
        current_time_period = ["2013-11-08", "2013-11-08"]
        units = "metric"
        user_params = {
            "output": {
                "page": {
                    "size": 3,
                    "index": 0
                },
                "sort": [[4, -1]]
            }
        }

        results = self.main_access.call_get_store_weather_data(banner_ids, current_time_period, prior_time_period, units, user_params, True)

        # round summary data to nearest tenth for comparison
        for k, v in results["summary"].iteritems():
            results["summary"][k] = round(v, 1)

        # compare (calculated myself)
        self.test_case.assertEqual(results, {
            "results": [
                self._create_combined_store_data(3, 1, 5, 10, 5, 10, 5, 10, 7, 14, 7, 14, 7, 14, 1, 1, 100, 100, 100, 100, 100, 100, 0, "station2, station2", None, None,
                                                 "station_name", "station2", "NY", 30, -75, "station_name", "station2", "NY", 30, -75),
                self._create_combined_store_data(2, 1, 1, 2, 1, 2, 1, 2, 3, 6, 3, 6, 3, 6, 1, 1, 100, 100, 100, 100, 100, 100, 0, "station1, station1", None, None,
                                                 "station_name", "station1", "NY", 40, -80, "station_name", "station1", "NY", 40, -80),
                self._create_combined_store_data(1, 1, 1, 2, 1, 2, 1, 2, 3, 6, 3, 6, 3, 6, 1, 1, 100, 100, 100, 100, 100, 100, 0, "station1, station1", None, None,
                                                 "station_name", "station1", "NY", 40, -80, "station_name", "station1", "NY", 40, -80),
            ],
            "field_list": [
                "Banner", "Street Number", "Street", "Suite", "State", "City", "Zip", "Phone Number", "Store Opened", "Store Closed", "Weather\nStations",

                # Average Columns
                "Current\nAvg of Daily\nAvg Temp (&deg;C)",
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)",
                "% Change\nAvg of Daily\nAvg Temp",
                "Current\nAvg of Daily\nPrecip (cm)",
                "Prior\nAvg of Daily\nPrecip (cm)",
                "% Change\nAvg of Daily\nPrecip",

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)",
                "Prior\nMin of Daily\nAvg Temp (&deg;C)",
                "% Change\nMin of Daily\nAvg Temp",
                "Current\nMin of Daily\nPrecip (cm)",
                "Prior\nMin of Daily\nPrecip (cm)",
                "% Change\nMin of Daily\nPrecip",

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)",
                "Prior\nMax of Daily\nAvg Temp (&deg;C)",
                "% Change\nMax of Daily\nAvg Temp",
                "Current\nMax of Daily\nPrecip (cm)",
                "Prior\nMax of Daily\nPrecip (cm)",
                "% Change\nMax of Daily\nPrecip",

                # Precip Days Columns
                "Current\nPrecip Days",
                "Prior\nPrecip Days",
                "% Change\nPrecip Days",

                # station details
                "Temp Station\nName", "Temp Station\nCode", "Temp Station\nState", "Temp Station\nDistance (km)", "Temp Station\nLatitude", "Temp Station\nLongitude",
                "Precip Station\nName", "Precip Station\nCode", "Precip Station\nState", "Precip Station\nDistance (km)", "Precip Station\nLatitude", "Precip Station\nLongitude"
            ],
            "field_meta": {
                "Current\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nAvg of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nAvg of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Min Columns
                "Current\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMin of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMin of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Max Columns
                "Current\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nAvg Temp (&deg;C)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nAvg Temp": { "type": "percent", "decimals": 2 },
                "Current\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "Prior\nMax of Daily\nPrecip (cm)": { "type": "number", "decimals": 5 },
                "% Change\nMax of Daily\nPrecip": { "type": "percent", "decimals": 2 },

                # Precip Days Columns
                "Current\nPrecip Days": { "type": "number", "decimals": 5 },
                "Prior\nPrecip Days": { "type": "number", "decimals": 5 },
                "% Change\nPrecip Days": { "type": "percent", "decimals": 2 },

                "Temp Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Temp Station\nLatitude": { "type": "number", "decimals": 5 },
                "Temp Station\nLongitude": { "type": "number", "decimals": 5 },
                "Precip Station\nDistance (km)": {"type": "number", "decimals": 3},
                "Precip Station\nLatitude": { "type": "number", "decimals": 5 },
                "Precip Station\nLongitude": { "type": "number", "decimals": 5 },
            },
            "meta": {
                "page_index": 0,
                "page_size": 3,
                "num_rows": 3,
                "sort_index": 4,
                "sort_direction": -1
            },
            "summary": {
                "min_prior_temp_min": 1,
                "min_prior_temp_avg": 1,
                "min_prior_temp_max": 1,
                "avg_prior_temp_min": 2.3,
                "avg_prior_temp_avg": 2.3,
                "avg_prior_temp_max": 2.3,
                "max_prior_temp_min": 5,
                "max_prior_temp_avg": 5,
                "max_prior_temp_max": 5,
                "min_prior_precip_min": 3,
                "min_prior_precip_avg": 3,
                "min_prior_precip_max": 3,
                "avg_prior_precip_min": 4.3,
                "avg_prior_precip_avg": 4.3,
                "avg_prior_precip_max": 4.3,
                "max_prior_precip_min": 7,
                "max_prior_precip_avg": 7,
                "max_prior_precip_max": 7,
                "min_current_temp_min": 2,
                "min_current_temp_avg": 2,
                "min_current_temp_max": 2,
                "avg_current_temp_min": 4.7,
                "avg_current_temp_avg": 4.7,
                "avg_current_temp_max": 4.7,
                "max_current_temp_min": 10,
                "max_current_temp_avg": 10,
                "max_current_temp_max": 10,
                "min_current_precip_min": 6,
                "min_current_precip_avg": 6,
                "min_current_precip_max": 6,
                "avg_current_precip_min": 8.7,
                "avg_current_precip_avg": 8.7,
                "avg_current_precip_max": 8.7,
                "max_current_precip_min": 14,
                "max_current_precip_avg": 14,
                "max_current_precip_max": 14,
                "min_prior_precip_days": 1,
                "avg_prior_precip_days": 1,
                "max_prior_precip_days": 1,
                "min_current_precip_days": 1,
                "avg_current_precip_days": 1,
                "max_current_precip_days": 1,

                # percent change - using helper for some of these to handle rounding properly
                "min_temp_min_change": 100,
                "min_temp_avg_change": 100,
                "min_temp_max_change": 100,
                "avg_temp_min_change": self.__calc_percent_change_np_arrays(np.array([3, 3, 7], float), np.array([6, 6, 14], float)),
                "avg_temp_avg_change": self.__calc_percent_change_np_arrays(np.array([3, 3, 7], float), np.array([6, 6, 14], float)),
                "avg_temp_max_change": self.__calc_percent_change_np_arrays(np.array([3, 3, 7], float), np.array([6, 6, 14], float)),
                "max_temp_min_change": 100,
                "max_temp_avg_change": 100,
                "max_temp_max_change": 100,
                "min_precip_min_change": 100,
                "min_precip_avg_change": 100,
                "min_precip_max_change": 100,
                "avg_precip_min_change": self.__calc_percent_change_np_arrays(np.array([1, 1, 5], float), np.array([2, 2, 10], float)),
                "avg_precip_avg_change": self.__calc_percent_change_np_arrays(np.array([1, 1, 5], float), np.array([2, 2, 10], float)),
                "avg_precip_max_change": self.__calc_percent_change_np_arrays(np.array([1, 1, 5], float), np.array([2, 2, 10], float)),
                "max_precip_min_change": 100,
                "max_precip_avg_change": 100,
                "max_precip_max_change": 100,
                "min_precip_days_change": 0,
                "avg_precip_days_change": 0,
                "max_precip_days_change": 0
            },
            "coverage": {
                "current_weather_coverage": 100.0,
                "prior_weather_coverage": 100.0
            }
        })

    def __calc_percent_change_np_arrays(self, prior, current):

        return round((current.mean() - prior.mean()) / prior.mean() * 100, 1)

    def test_get_period_weather_data__null_aggregates(self):
        """
        This tests various complex aggregates and how they deal with null values...
        """

        # create test company & store
        company_id_1 = insert_test_company(name="company_name_1", ctype="retail_banner")
        store_id_1 = insert_test_store(company_id_1, None, weather_code="station1_station1")

        # create sets of weather data with null values for either temp or precip, plus one set with non-null values
        insert_test_weather("2013-11-07", "station1_station1", None, None, 3.0, 4.0)
        insert_test_weather("2013-11-08", "station1_station1", 5.0, 6.0, None, None)
        insert_test_weather("2013-11-09", "station1_station1", 9.0, 10.0, 11.0, 12.0)

        self.test_case.maxDiff = None

        # query prior and verify nulls are not counted in min/max/avg/precip_days
        results = self.main_weather_endpoints._get_weather_aggregates({"station1_station1"}, [datetime.datetime(2013, 11, 7), datetime.datetime(2013, 11, 9)], "tcmean", "pmm", self.context)
        self.test_case.assertEqual(sorted(results), sorted([
            self._create_weather_aggregate("station1_station1", 7, 5, 9, 7, 3, 11, 2, 3)
        ]))

        # edge case, verify the behavior of the aggregate, when all the values are null
        results = self.main_weather_endpoints._get_weather_aggregates({"station1_station1"}, [datetime.datetime(2013, 11, 8), datetime.datetime(2013, 11, 8)], "tcmean", "pmm", self.context)
        self.test_case.assertEqual(sorted(results), sorted([
            self._create_weather_aggregate("station1_station1", 5, 5, 5, 0, None, None, 0, 1)
        ]))

        # verify same edge case as above, but for temps
        results = self.main_weather_endpoints._get_weather_aggregates({"station1_station1"}, [datetime.datetime(2013, 11, 7), datetime.datetime(2013, 11, 7)], "tcmean", "pmm", self.context)
        self.test_case.assertEqual(sorted(results), sorted([
            self._create_weather_aggregate("station1_station1", 0, None, None, 3, 3, 3, 1, 1)
        ]))



    # --------------------- Private Methods --------------------- #

    def _create_combined_store_data(self, store_num, company_num, prior_temp_avg, current_temp_avg, prior_temp_min, current_temp_min,
                                    prior_temp_max, current_temp_max, prior_precip_avg, current_precip_avg, prior_precip_min,
                                    current_precip_min, prior_precip_max, current_precip_max, prior_precip_days, current_precip_days,
                                    temp_avg_diff, temp_min_diff, temp_max_diff, precip_avg_diff, precip_min_diff, precip_max_diff, precip_days_diff,
                                    weather_code, temp_station_distance, precip_station_distance, temp_station_name, temp_station_code, temp_station_state,
                                    temp_station_latitude, temp_station_longitude, precip_station_name, precip_station_code, precip_station_state, precip_station_latitude, precip_station_longitude):

        return [
            "company_name_%s" % str(company_num),
            "street_number",
            "street",
            "suite",
            "state_%s" % str(store_num),
            "city_%s" % str(store_num),
            "zip",
            "phone",
            None,
            None,
            weather_code,

            # Average Columns
            current_temp_avg,
            prior_temp_avg,
            temp_avg_diff,
            current_precip_avg,
            prior_precip_avg,
            precip_avg_diff,

            # Min Columns
            current_temp_min,
            prior_temp_min,
            temp_min_diff,
            current_precip_min,
            prior_precip_min,
            precip_min_diff,

            # Max Columns
            current_temp_max,
            prior_temp_max,
            temp_max_diff,
            current_precip_max,
            prior_precip_max,
            precip_max_diff,

            # Precip Days Columns
            current_precip_days,
            prior_precip_days,
            precip_days_diff,

            temp_station_name,
			temp_station_code,
			temp_station_state,
			temp_station_distance,
			temp_station_latitude,
			temp_station_longitude,
			precip_station_name,
			precip_station_code,
			precip_station_state,
			precip_station_distance,
			precip_station_latitude,
			precip_station_longitude
        ]

    def _create_weather_aggregate(self, weather_code, temp_avg, temp_min, temp_max, precip_avg, precip_min, precip_max, precip_days, weather_days):

        data = {
            "_id": weather_code,
            "temp_avg": temp_avg,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "precip_avg": precip_avg,
            "precip_min": precip_min,
            "precip_max": precip_max,
            "precip_days": precip_days,
            "weather_days": weather_days
        }

        return data