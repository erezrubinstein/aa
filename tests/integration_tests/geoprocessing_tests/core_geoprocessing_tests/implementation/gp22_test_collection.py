import datetime
from common.utilities.inversion_of_control import Dependency
from geoprocessing.geoprocessors.weather.gp_22_get_weather_station_data import GP22GetWeatherStationData
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_weather, insert_test_weather_station_mongo
from tests.integration_tests.utilities.data_access_misc_queries_postgres import purge_weather_tables, insert_test_source_file, insert_test_weather_station, insert_test_weather_var, insert_test_point_data

__author__ = 'erezrubinstein'

class GP22TestCollection(ServiceTestCollection):

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

    def test_simple_gp_22_run(self):

        # insert a source file
        source_file_id = insert_test_source_file("bob sagget")

        # create three stations (close to each other)
        station_1_id = insert_test_weather_station("code1", 40, -80, "station1")

        # insert the mongo weather station
        insert_test_weather_station_mongo("code1", "station1", station_1_id, 40, -80)

        # insert weather vars for precipitation and tmin/tmax
        t_min_var_id = insert_test_weather_var("TMIN")
        t_max_var_id = insert_test_weather_var("TMAX")
        precip_var_id = insert_test_weather_var("PRCP")

        # create weather data
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-07", 0, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-07", 20, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-07", 30, source_file_id)
        insert_test_point_data(t_min_var_id, station_1_id, "2013-11-08", 40, source_file_id)
        insert_test_point_data(t_max_var_id, station_1_id, "2013-11-08", 60, source_file_id)
        insert_test_point_data(precip_var_id, station_1_id, "2013-11-08", 70, source_file_id)

        # run gp 22 on this station for weather and precip
        gp = GP22GetWeatherStationData()
        gp.process_object({ "weather_code": "code1#!@code1" }, entity_type = "weather")

        # query the store weathers and remove the distance, since it's tough to verify
        weather_records = self._query_weather_records_and_remove_ids()

        # verify structure of store weather
        self.test_case.assertEqual(weather_records, [
            self._create_weather_structure(datetime.datetime(2013, 11, 7), 0, 2, 1, 32, 35.6, 33.8, "code1", 3, .11811, "code1"),
            self._create_weather_structure(datetime.datetime(2013, 11, 8), 4, 6, 5, 39.2, 42.8, 41, "code1", 7, .27559, "code1")
        ])


    # -------------------------------------- Internal -------------------------------------- #

    def _create_weather_structure(self, date, temp_c_min, temp_c_max, temp_c_mean, temp_f_min, temp_f_max, temp_f_mean,
                              station_code, precip_mm, precip_in, precip_station_code):

        return {
            "d": date,
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
