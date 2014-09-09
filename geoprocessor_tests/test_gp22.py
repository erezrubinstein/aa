import mox
from common.utilities.date_utilities import start_of_world, end_of_world
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.geoprocessors.weather.gp_22_get_weather_station_data import GP22GetWeatherStationData
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from weather.models import weather_repository

__author__ = 'erezrubinstein'

class GP22Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP22Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_mds_access = Dependency("MDSMongoAccess").value

        # create the test gp
        self.gp = GP22GetWeatherStationData()

        # set the entity for the gp
        self.gp._entity = {
            "weather_code": "chicken#!@woot"
        }


    def doCleanups(self):

        # call GP16Tests clean up and clean dependencies
        super(GP22Tests, self).doCleanups()
        dependencies.clear()


    def test_initialize(self):

        # run initialize
        self.gp._initialize()

        # verify that all the properties are set up correctly
        self.assertEqual(self.gp._weather_code, "chicken#!@woot")
        self.assertEqual(self.gp._precip_station_code, "chicken")
        self.assertEqual(self.gp._temp_station_code, "woot")


    def test_do_geoprocessing(self):

        # begin stubbing
        self.mox.StubOutClassWithMocks(weather_repository, "WeatherRepository")
        self.mox.StubOutWithMock(self.gp, "_get_station_psql_ids")

        # begin recording
        mock_repository = weather_repository.WeatherRepository()
        self.gp._get_station_psql_ids().AndReturn(("chilly", "willy"))
        mock_repository.select_pointdata_from_stations("chilly", "willy", start_of_world, end_of_world).AndReturn("Guacamole")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._do_geoprocessing()

        # make sure things are set
        self.assertEqual(self.gp.weather_data, "Guacamole")


    def test_preprocess_data_for_save(self):

        # mock some of the gp values
        self.gp.weather_data = "The Dude"
        self.gp._weather_code = "Donny"

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "sync_existing_and_new_weather_data")

        # begin recording
        weather_helper.sync_existing_and_new_weather_data("The Dude", "Donny").AndReturn(("Walter", "Lebowski"))

        # replay all
        self.mox.ReplayAll()

        # go!
        self.gp._preprocess_data_for_save()

        # very
        self.assertEqual(self.gp.new_weather_data, "Walter")
        self.assertEqual(self.gp.weather_ids_to_delete, "Lebowski")


    def test_save_processed_data(self):

        # mock some gp properties
        self.gp.new_weather_data = "Watter Bottle"
        self.gp._weather_code = "Ninja"
        self.gp.weather_ids_to_delete = []

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # begin recording
        weather_helper.upsert_new_weather_data("Watter Bottle", "Ninja")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        self.gp._save_processed_data()


    def test_save_processed_data__no_new_data(self):

        # mock some gp properties
        self.gp.new_weather_data = []
        self.gp._weather_code = "MDog"
        self.gp.weather_ids_to_delete = []

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        self.gp._save_processed_data()


    def test_save_processed_data__data_to_delete(self):

        # mock some gp properties
        self.gp.new_weather_data = []
        self.gp._weather_code = "MDog"
        self.gp.weather_ids_to_delete = [1, 2, 3]

        # begin stubbing
        self.mox.StubOutWithMock(weather_helper, "upsert_new_weather_data")
        self.mox.StubOutWithMock(weather_helper, "delete_existing_weather_records")

        # record away
        weather_helper.delete_existing_weather_records([1, 2, 3])

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        self.gp._save_processed_data()


    def test_get_station_psql_ids(self):

        # define mocks/expected data
        mock_query = { "data.code": { "$in": ["chicken", "woot"]}}
        mock_projection = { "data.code": 1, "data.psql_id": 1 }
        mock_stations = [
            {
                "data": {
                    "code": "chicken",
                    "psql_id": 1
                }
            },
            {
                "data": {
                    "code": "woot",
                    "psql_id": 2
                }
            }
        ]

        # set mock gp properties
        self.gp._temp_station_code, self.gp._precip_station_code = "chicken", "woot"

        # begin recording
        self.mock_mds_access.find("weather_station", mock_query, mock_projection).AndReturn(mock_stations)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(self.gp._get_station_psql_ids(), (1, 2))


    def test_get_station_psql_ids__one_empty(self):

        # define mocks/expected data
        mock_query = { "data.code": { "$in": ["chicken"]}}
        mock_projection = { "data.code": 1, "data.psql_id": 1 }
        mock_stations = [
            {
                "data": {
                    "code": "chicken",
                    "psql_id": 1
                }
            }
        ]

        # set mock gp properties
        self.gp._temp_station_code, self.gp._precip_station_code = "chicken", ""

        # begin recording
        self.mock_mds_access.find("weather_station", mock_query, mock_projection).AndReturn(mock_stations)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(self.gp._get_station_psql_ids(), (1, -1))
