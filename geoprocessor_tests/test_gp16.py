import datetime
from bson.objectid import ObjectId
import mox
from common.utilities.date_utilities import start_of_world, end_of_world
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.geoprocessors.weather.gp16_get_store_weather import GP16GetStoreWeather
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from weather.models import weather_repository

__author__ = 'erezrubinstein'

class GP16Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP16Tests, self).setUp()

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

        # create the test gp
        self.gp = GP16GetStoreWeather()
        self.gp._entity = self.trade_area

    def doCleanups(self):

        # call GP16Tests clean up and clean dependencies
        super(GP16Tests, self).doCleanups()
        dependencies.clear()

    def test_initialize__defaults(self):

        # run initialize
        self.gp._initialize()

        # make sure we're using the right vars
        self.assertEqual(self.gp._latitude, 1)
        self.assertEqual(self.gp._longitude, -1)
        self.assertEqual(self.gp._store_id, self.store_id)
        self.assertEqual(self.gp._company_id, "buddy!")
        self.assertEqual(self.gp._start_date, start_of_world)
        self.assertEqual(self.gp._end_date, end_of_world)


    def test_do_geoprocessing(self):

        # create the gp and it's mock properties
        gp = GP16GetStoreWeather()
        gp._longitude = -80
        gp._latitude = 40
        gp._store_id = "whatever"
        gp._start_date = "chicken"
        gp._end_date = "woot"

        # create some mocks
        mock_closest_stations = {
            "temp_station_id": 1,
            "temp_station_code": "willy",
            "temp_station_distance": 1.1,
            "precip_station_id": 2,
            "precip_station_code": "chilly",
            "precip_station_distance": 2.2
        }
        mock_existing_data = {
            "weather_code": "morty",
            "temp_station_distance": "rubinstein"
        }

        # stub out stuff
        self.mox.StubOutClassWithMocks(weather_repository, "WeatherRepository")
        self.mox.StubOutWithMock(gp, "_get_existing_store_weather_data")
        self.mox.StubOutWithMock(weather_helper, "get_weather_station_code")

        # begin recording
        mock_repository = weather_repository.WeatherRepository()
        mock_repository.select_best_temp_and_precip_stations(40, -80, "chicken", "woot").AndReturn(mock_closest_stations)
        mock_repository.select_pointdata_from_stations(1, 2, "chicken", "woot").AndReturn("weather")
        gp._get_existing_store_weather_data().AndReturn(mock_existing_data)
        weather_helper.get_weather_station_code("chilly", "willy").AndReturn("dog")

        # replay all
        self.mox.ReplayAll()

        # go!
        gp._do_geoprocessing()

        # make sure the vars are correct
        self.assertEqual(gp.weather_data, "weather")
        self.assertEqual(gp.existing_weather_code, "morty")
        self.assertEqual(gp.existing_temp_distance, "rubinstein")
        self.assertEqual(gp.existing_precip_distance, None)
        self.assertEqual(gp.weather_station_unique_combined_code, "dog")


    def test_preprocess_data_for_save(self):

        # create the gp and it's mock properties
        gp = GP16GetStoreWeather()
        gp.weather_data = "chicken_woot"
        gp.weather_station_unique_combined_code = "sloppy_joes"
        gp._store_id = "whatever"

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "sync_existing_and_new_weather_data")

        # begin recording
        weather_helper.sync_existing_and_new_weather_data("chicken_woot", "sloppy_joes").AndReturn(("bob", "saget"))

        # replay all
        self.mox.ReplayAll()

        # go!
        gp._preprocess_data_for_save()

        # verify that the gp set everything correctly
        self.assertEqual(gp.new_weather_data, "bob")
        self.assertEqual(gp.weather_ids_to_delete, "saget")


    def test_save_processed_data__new_weather__code_doesnt_change(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = "bob_saget"
        gp.existing_weather_code = "chicken_woot"
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 1
        gp.precip_station_distance = 2
        gp.weather_ids_to_delete = []

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        weather_helper.upsert_new_weather_data("bob_saget", "chicken_woot")

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_save_processed_data__no_new_weather__code_changes(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = []
        gp.existing_weather_code = "chicken"
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 1
        gp.precip_station_distance = 2
        gp.weather_ids_to_delete = []

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        gp._update_store_weather_code()

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_save_processed_data__no_new_weather__code_changes_from_null(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = []
        gp.existing_weather_code = None
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 1
        gp.precip_station_distance = 2
        gp.weather_ids_to_delete = []

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        gp._update_store_weather_code()

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_save_processed_data__no_new_weather__distance_changes(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = []
        gp.existing_weather_code = None
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 3
        gp.precip_station_distance = 4
        gp.weather_ids_to_delete = []

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        gp._update_store_weather_code()

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_save_processed_data__stuff_to_delete(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = []
        gp.existing_weather_code = "chicken_woot"
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 1
        gp.precip_station_distance = 2
        gp.weather_ids_to_delete = [1, 2, 3]

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        weather_helper.delete_existing_weather_records([1, 2, 3])

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_save_processed_data__nothing_changes(self):

        # define the gp and its properties
        gp = GP16GetStoreWeather()
        gp._store_id = "whatever"
        gp.new_weather_data = []
        gp.existing_weather_code = "chicken_woot"
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.existing_temp_distance = 1
        gp.existing_precip_distance = 2
        gp.temp_station_distance = 1
        gp.precip_station_distance = 2
        gp.weather_ids_to_delete = []

        # stub out some data
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(gp, "_update_store_weather_code")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # replay all
        self.mox.ReplayAll()

        # Big Poppa
        gp._save_processed_data()


    def test_update_store_weather_code(self):

        # create the gop and mock some of its properties
        gp = GP16GetStoreWeather()
        gp._store_id = str(ObjectId())
        gp.existing_weather_code = "chilly_willy"
        gp.weather_station_unique_combined_code = "chicken_woot"
        gp.temp_station_distance = "tourettes"
        gp.precip_station_distance = "guy"
        gp._context = "hola"

        # stub out stuff
        self.mox.StubOutWithMock(datetime, "datetime")

        # create some mocks
        mock_query = { "_id": ObjectId(gp._store_id) }
        mock_update = {
            "$set": {
                "data.weather_code": "chicken_woot",
                "data.temp_station_distance": "tourettes",
                "data.precip_station_distance": "guy"
            }
        }

        # begin recording
        self.mock_mds_access.update("store", mock_query, mock_update)
        datetime.datetime.utcnow().AndReturn("date_1")
        self.mock_main_access.mds.call_add_audit("store", gp._store_id, "data.weather_code", "chilly_willy", "chicken_woot",
                                        "date_1", context = "hola")

        # replay all
        self.mox.ReplayAll()

        # I love gooooold!
        gp._update_store_weather_code()


    def test_get_existing_store_weather_data(self):

        # create the gop and mock some of its properties
        gp = GP16GetStoreWeather()
        gp._store_id = str(ObjectId())

        # create some mocks
        mock_query = { "_id": ObjectId(gp._store_id) }
        mock_projection = { "data.weather_code": 1, "data.temp_station_distance": 1, "data.precip_station_distance": 1 }
        mock_store = { "data": { "weather_code": "shalom" }}

        # record away
        self.mock_mds_access.find_one("store", mock_query, mock_projection).AndReturn(mock_store)

        # replay all
        self.mox.ReplayAll()

        # taco party!
        self.assertEqual(gp._get_existing_store_weather_data(), { "weather_code": "shalom" })