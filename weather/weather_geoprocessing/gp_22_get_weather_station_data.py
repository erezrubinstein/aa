from common.utilities.date_utilities import FastDateParser, START_OF_WORLD, END_OF_WORLD
from common.utilities.inversion_of_control import Dependency
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.geoprocessors.abstract_geo_processor import AbstractGeoProcessor
from weather.models import weather_repository

__author__ = 'erezrubinstein'

class GP22GetWeatherStationData(AbstractGeoProcessor):
    """
    Geoprocessing Step 16: Get Weather data for store
    """
    def __init__(self):

        super(GP22GetWeatherStationData, self).__init__()

        # gp-specific dependencies
        self.logger = Dependency("FlaskLogger").value
        self.mds_db_access = Dependency("MDSMongoAccess").value

        # instance variables
        self._context = {'user_id': 42, 'source': 'GP22'}
        self._timeout = 9999

        # allows you to pass global start/end dates.
        # for example if you want to process 1 day, not the entire store's lifetime
        # plan B allows these to be set to the default, which is None
        self._start_date = START_OF_WORLD
        self._end_date = END_OF_WORLD



    # ----------------------------- GP Template Methods  ----------------------------- #

    def _initialize(self):

        # get class member fields from entity
        self._weather_code = self._entity["weather_code"]

        # parse the codes out of the combined code
        self._precip_station_code, self._temp_station_code = weather_helper.parse_weather_station_code(self._weather_code)


    def _do_geoprocessing(self):

        # create a weather postgis repository
        repository = weather_repository.WeatherRepository()

        # get the psql weather ids
        temp_station_id, precip_station_id = self._get_station_psql_ids()

        # get the data from psql
        self.weather_data = repository.select_pointdata_from_stations(temp_station_id, precip_station_id, self._start_date, self._end_date)


    def _preprocess_data_for_save(self):

        # sync the new/existing weather data to see what to upsert and what to delete
        (self.new_weather_data,
         self.weather_ids_to_delete) = weather_helper.sync_existing_and_new_weather_data(self.weather_data, self._weather_code)


    def _save_processed_data(self):

        # if there is new weather data, upsert it.
        if self.new_weather_data:
            weather_helper.upsert_new_weather_data(self.new_weather_data, self._weather_code)

        # if there's stuff to delete, go ahead and delete it
        if self.weather_ids_to_delete:
            weather_helper.delete_existing_weather_records(self.weather_ids_to_delete)



    # ----------------------------- Internal Methods  ----------------------------- #

    def _get_station_psql_ids(self):

        # remove empty codes (for cases where it's just one station)
        codes = [code for code in [self._temp_station_code, self._precip_station_code] if code]

        # query mongo for these
        query = { "data.code": { "$in": codes}}
        projection = { "data.code": 1, "data.psql_id": 1 }
        stations = self.mds_db_access.find("weather_station", query, projection)

        # convert to dictionaries for easy lookups
        stations = convert_entity_list_to_dictionary(stations, key = lambda s: s["data"]["code"])

        # default to a psql id of -1 if there's no station
        temp_station_id = -1
        precip_station_id = -1
        if self._temp_station_code in stations:
            temp_station_id = stations[self._temp_station_code]["data"]["psql_id"]
        if self._precip_station_code in stations:
            precip_station_id = stations[self._precip_station_code]["data"]["psql_id"]

        return temp_station_id, precip_station_id