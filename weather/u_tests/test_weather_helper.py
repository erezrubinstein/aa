import mox
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies

__author__ = 'erezrubinstein'


class WeatherHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WeatherHelperTests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_mds_access = Dependency("MDSMongoAccess").value

        # create the mock trade _area
        self.trade_area_id = 11
        self.store_id = "woot!"
        self.trade_area = {
            "_id" : self.trade_area_id,
            "data" : {
                "store_id": self.store_id,
                "company_id": "buddy!",
                "latitude" : 1,
                "longitude" : -1,
                "store_opened_date": "2012-01-01",
                "store_closed_date": "2013-12-31"
            }
        }

    def doCleanups(self):

        # call GP16Tests clean up and clean dependencies
        super(WeatherHelperTests, self).doCleanups()
        dependencies.clear()



    # ------------------------------- Start Testing ------------------------------- #
    
    def test_get_weather_station_code(self):

        # simplest test ever (in Jeff Albertson voice)
        self.assertEqual(weather_helper.get_weather_station_code("chicken", "woot"), "chicken#!@woot")


    def test_filter_out_existing_weather_data(self):

        # define mocks
        mock_weather_code = "chicken_woot"
        mock_weather_data = [
            {
                "date": "date_1",
                "precip_mm": 1,
                "temp_c_max": 1.1,
                "temp_c_min": 1.11
            },
            {
                "date": "date_2",
                "precip_mm": 2,
                "temp_c_max": 2.2,
                "temp_c_min": 2.22
            },
            {
                "date": "date_3",
                "precip_mm": 3,
                "temp_c_max": 3.3,
                "temp_c_min": 3.33
            }
        ]

        # date date1/2 exist, but date 1 is different
        mock_existing_data = [
            {
                "_id": 1,
                "d": "date_1",
                "pmm": 5,
                "tcmax": 5.5,
                "tcmin": 5.55
            },
            {
                "_id": 2,
                "d": "date_2",
                "pmm": 2,
                "tcmax": 2.2,
                "tcmin": 2.22
            },
            {
                "_id": 4,
                "d": "date_4",
                "pmm": 4,
                "tcmax": 4.4,
                "tcmin": 4.44
            },
            {
                "_id": 5,
                "d": "date_5",
                "pmm": 5,
                "tcmax": 5.5,
                "tcmin": 5.55
            }
        ]

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "_find_existing_weather_records")

        # begin recording
        weather_helper._find_existing_weather_records(mock_weather_code).AndReturn(mock_existing_data)

        # replay all
        self.mox.ReplayAll()

        # taco flavored kisses
        new_weather_data, weather_ids_to_delete = weather_helper.sync_existing_and_new_weather_data(mock_weather_data, mock_weather_code)

        # verify results
        self.assertEqual(new_weather_data, [
            {
                "date": "date_1",
                "precip_mm": 1,
                "temp_c_max": 1.1,
                "temp_c_min": 1.11
            },
            {
                "date": "date_3",
                "precip_mm": 3,
                "temp_c_max": 3.3,
                "temp_c_min": 3.33
            }
        ])
        self.assertEqual(weather_ids_to_delete, [4, 5])


    def test_find_existing_weather_matches(self):

        # mock some stuff!
        mock_results = { 1, 2, 3, 4} # make a set so that we can test that we create a list of out it.
        mock_weather_code = "chicken_woot"
        mock_query = {
            "code": mock_weather_code
        }
        mock_entity_fields = { "_id": 1, "d": 1, "pmm": 1, "tcmax": 1, "tcmin": 1 }

        # begin recording
        self.mock_mds_access.find("weather", mock_query, mock_entity_fields).AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # I love goooooold!
        self.assertEqual(weather_helper._find_existing_weather_records( mock_weather_code), [
            1,
            2,
            3,
            4
        ])


    def test_upsert_new_weather_data(self):

        # define mocks
        mock_new_weather_data = [
            {
                "date": "date_1",
                "precip_in" : 1,
                "precip_mm" : 2,
                "precip_station_code" : "chilly",
                "precip_station_name" : "whatever",
                "temp_c_max" : 3,
                "temp_c_mean" : 4,
                "temp_c_min" : 5,
                "temp_f_max" : 6,
                "temp_f_mean" : 7,
                "temp_f_min" : 8,
                "temp_station_code" : "willy",
                "temp_station_name" : "whatever",
            },
            {
                "date": "date_2",
                "precip_in" : 9,
                "precip_mm" : 10,
                "precip_station_code" : "chicken",
                "precip_station_name" : "whatever",
                "temp_c_max" : 11,
                "temp_c_mean" : 12,
                "temp_c_min" : 13,
                "temp_f_max" : 14,
                "temp_f_mean" : 15,
                "temp_f_min" : 16,
                "temp_station_code" : "woot",
                "temp_station_name" : "whatever",
            }
        ]

        # expected update call
        expected_batch_upserts = [
            {
                "query": {
                    "d": "date_1",
                    "code": "chicken_woot"
                },
                "operations": {
                    "$set": {
                        "d": mock_new_weather_data[0]["date"],
                        "pin": mock_new_weather_data[0]["precip_in"],
                        "pmm": mock_new_weather_data[0]["precip_mm"],
                        "tcmax": mock_new_weather_data[0]["temp_c_max"],
                        "tcmean": mock_new_weather_data[0]["temp_c_mean"],
                        "tcmin": mock_new_weather_data[0]["temp_c_min"],
                        "tfmax": mock_new_weather_data[0]["temp_f_max"],
                        "tfmean": mock_new_weather_data[0]["temp_f_mean"],
                        "tfmin": mock_new_weather_data[0]["temp_f_min"],
                        "code": "chicken_woot",
                    }
                }
            },
            {
                "query": {
                    "d": "date_2",
                    "code": "chicken_woot"
                },
                "operations": {
                    "$set": {
                        "d": mock_new_weather_data[1]["date"],
                        "pin": mock_new_weather_data[1]["precip_in"],
                        "pmm": mock_new_weather_data[1]["precip_mm"],
                        "tcmax": mock_new_weather_data[1]["temp_c_max"],
                        "tcmean": mock_new_weather_data[1]["temp_c_mean"],
                        "tcmin": mock_new_weather_data[1]["temp_c_min"],
                        "tfmax": mock_new_weather_data[1]["temp_f_max"],
                        "tfmean": mock_new_weather_data[1]["temp_f_mean"],
                        "tfmin": mock_new_weather_data[1]["temp_f_min"],
                        "code": "chicken_woot",
                    }
                }
            }
        ]


        # begin recording
        self.mock_mds_access.update("weather", expected_batch_upserts[0]["query"], expected_batch_upserts[0]["operations"], upsert=True, raw=True)
        self.mock_mds_access.update("weather", expected_batch_upserts[1]["query"], expected_batch_upserts[1]["operations"], upsert=True, raw=True)

        # replay all
        self.mox.ReplayAll()

        # I love goooood!
        weather_helper.upsert_new_weather_data(mock_new_weather_data, "chicken_woot")


    def test_parse_weather_station_code__simple(self):

        precip, temp = weather_helper.parse_weather_station_code("chicken#!@woot")
        self.assertEqual(precip, "chicken")
        self.assertEqual(temp, "woot")


    def test_parse_weather_station_code__one_empty(self):

        precip, temp = weather_helper.parse_weather_station_code("#!@woot")
        self.assertEqual(precip, "")
        self.assertEqual(temp, "woot")

        precip, temp = weather_helper.parse_weather_station_code("chicken#!@")
        self.assertEqual(precip, "chicken")
        self.assertEqual(temp, "")

        precip, temp = weather_helper.parse_weather_station_code("#!@")
        self.assertEqual(precip, "")
        self.assertEqual(temp, "")


    def test_parse_weather_station_code__error(self):

        with self.assertRaises(Exception):
            weather_helper.parse_weather_station_code("")