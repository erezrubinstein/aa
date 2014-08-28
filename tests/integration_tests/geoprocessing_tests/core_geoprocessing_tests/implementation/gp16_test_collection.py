import datetime

from common.utilities.inversion_of_control import Dependency
from tests.integration_tests.utilities.data_access_misc_queries_postgres import purge_weather_tables, insert_test_weather_station, insert_test_weather_var, insert_test_point_data, insert_test_source_file
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area, select_trade_area, insert_test_store, select_test_store
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from geoprocessing.geoprocessors.weather.gp16_get_store_weather import GP16GetStoreWeather
from common.utilities.date_utilities import parse_date


__author__ = 'erezrubinstein'

class GP16TestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "gp_16_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        # clear dbs
        self.mds_access.call_delete_reset_database()

        # reset the postgres data
        purge_weather_tables()

        # get mds access
        self.mds_direct_access = Dependency("MDSMongoAccess").value

        # in the face
        self.test_case.maxDiff = None

    def tearDown(self):

        # reset the postgres data
        purge_weather_tables()



    # -------------------------------------- Begin Testing!! -------------------------------------- #

    def test_simple_run(self):

        # insert a source file
        source_file_id = insert_test_source_file("bob sagget")

        # create three stations (close to each other)
        station_1_id = insert_test_weather_station("code_1", 40, -80, "station_name_1")
        station_2_id = insert_test_weather_station("code_2", 40.01, -8.01, "station_name_2")
        station_3_id = insert_test_weather_station("code_3", 40.02, -8.02, "station_name_3")

        # insert weather vars for precipitation and tmin/tmax
        t_min_var_id = insert_test_weather_var("TMIN")
        t_max_var_id = insert_test_weather_var("TMAX")
        precip_var_id = insert_test_weather_var("PRCP")

        # create three point data (t-min, t-max, precip) entries for each weather station for two days
        # station 1
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-07", 0, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-07", 20, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-07", 30, source_file_id)
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-08", 40, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-08", 60, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-08", 70, source_file_id)
        # station 2
        insert_test_point_data(t_min_var_id, station_2_id, "2013-11-07", 100, source_file_id)
        insert_test_point_data(t_max_var_id, station_2_id, "2013-11-07", 120, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-07", 130, source_file_id)
        insert_test_point_data(t_min_var_id, station_2_id, "2013-11-08", 140, source_file_id)
        insert_test_point_data(t_max_var_id, station_2_id, "2013-11-08", 160, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-08", 170, source_file_id)
        # station 3
        insert_test_point_data(t_min_var_id, station_3_id, "2013-11-07", 220, source_file_id)
        insert_test_point_data(t_max_var_id, station_3_id, "2013-11-07", 240, source_file_id)
        insert_test_point_data(precip_var_id, station_3_id, "2013-11-07", 250, source_file_id)
        insert_test_point_data(t_min_var_id, station_3_id, "2013-11-08", 260, source_file_id)
        insert_test_point_data(t_max_var_id, station_3_id, "2013-11-08", 280, source_file_id)
        insert_test_point_data(precip_var_id, station_3_id, "2013-11-08", 290, source_file_id)

        # create a trade area, which is closest to station 1
        store_id = insert_test_store("company_id_1", None)
        trade_area_id = insert_test_trade_area(store_id, company_id = "company_id_1", city = "city_1", state = "state_1", company_name = "company_name_1", latitude = 40, longitude = -80)

        # query the trade area document, and run GP16 on it
        trade_area_document = select_trade_area(trade_area_id)

        # run gp 16 on on two days worth
        GP16GetStoreWeather().process_object(trade_area_document)

        # query the store weathers and remove the distance, since it's tough to verify
        weather_records = self._query_weather_records_and_remove_ids()

        # verify structure of store weather
        self.test_case.assertEqual(weather_records, [
            self._create_weather_structure(datetime.datetime(2013, 11, 7), 0, 2, 1, 32, 35.6, 33.8, "code_1", 3, .11811, "code_1"),
            self._create_weather_structure(datetime.datetime(2013, 11, 8), 4, 6, 5, 39.2, 42.8, 41, "code_1", 7, .27559, "code_1")
        ])

        # query the store
        store = select_test_store(store_id)

        # verify that it's matched to this station
        self.test_case.assertEqual(store["data"]["weather_code"], "code_1#!@code_1")


    def test_mixed_weather_stations(self):

        # insert a source file
        source_file_id = insert_test_source_file("bob sagget")

        # create several stations (close to each other)
        station_1_id = insert_test_weather_station("code_1", 40, -80, "station_name_1")
        station_2_id = insert_test_weather_station("code_2", 40.01, -80.01, "station_name_2")

        # insert weather vars for precipitation and tmin/tmax
        t_min_var_id = insert_test_weather_var("TMIN")
        t_max_var_id = insert_test_weather_var("TMAX")
        precip_var_id = insert_test_weather_var("PRCP")

        # create data for each station
        # station 1, no precip
        # station 2, no temp
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-07", 0, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-07", 20, source_file_id)
        insert_test_point_data(precip_var_id, station_2_id, "2013-11-07", 30, source_file_id)

        # trade area 1, close to station 1 and 2
        # trade area 2, close to station 3
        # trade area 3, close to station 4
        store_id = insert_test_store("company_id_1", None)
        trade_area_id_1 = insert_test_trade_area(store_id, company_id = "company_id_1", city = "city_1", state = "state_1", company_name = "company_name_1", latitude = 40, longitude = -80)

        # run gp 16 on one day for all three trade areas
        GP16GetStoreWeather().process_object(select_trade_area(trade_area_id_1))

        # query the store weathers and remove the distance, since it's tough to verify
        weather_records = self._query_weather_records_and_remove_ids()

        # verify structure of store weather
        self.test_case.assertEqual(weather_records, [
            self._create_weather_structure(datetime.datetime(2013, 11, 7), 0, 2, 1, 32, 35.6, 33.8, "code_1", 3, .11811, "code_2")
        ])

        # query the store
        store = select_test_store(store_id)

        # verify that it's matched to this station
        self.test_case.assertEqual(store["data"]["weather_code"], "code_2#!@code_1")




    # ------------------------------------------ Helpers -----------------------------------------

    def _create_weather_structure(self, date, temp_c_min, temp_c_max, temp_c_mean, temp_f_min, temp_f_max, temp_f_mean,
                              station_code, precip_mm, precip_in, precip_station_code):

        return {
            "d": parse_date(date),
            "tcmin": temp_c_min,
            "tcmax": temp_c_max,
            "tcmean": temp_c_mean,
            "tfmin": temp_f_min,
            "tfmax": temp_f_max,
            "tfmean": temp_f_mean,
            "pmm": precip_mm,
            "pin": precip_in,
            "code": "%s#!@%s" % (precip_station_code, station_code)
        }


    def _query_weather_records_and_remove_ids(self):

        # query the weather data
        records = list(self.mds_direct_access.find("weather"))

        # remove ids
        for record in records:
            del record["_id"]

        return records