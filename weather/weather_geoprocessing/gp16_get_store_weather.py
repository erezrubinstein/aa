from bson.objectid import ObjectId
import datetime
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import normalize_start_date, normalize_end_date, FastDateParser, start_of_world, end_of_world
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.geoprocessors.abstract_geo_processor import AbstractGeoProcessor
from weather.models import weather_repository

__author__ = 'erezrubinstein'


class GP16GetStoreWeather(AbstractGeoProcessor):
    """
    Geoprocessing Step 16: Get Weather data for store
    """
    def __init__(self):

        super(GP16GetStoreWeather, self).__init__()

        # gp-specific dependencies
        self.logger = Dependency("FlaskLogger").value
        self.mds_db_access = Dependency("MDSMongoAccess").value
        self.main_access = Dependency("CoreAPIProvider").value

        # instance variables
        self._context = {'user_id': 42, 'source': 'GP16'}
        self._timeout = 9999

    # ------------------------ GP Template Methods  ------------------------ #

    def _initialize(self):

        # get class member fields from entity, which is expected to be a trade_area
        self._latitude = self._entity["data"]["latitude"]
        self._longitude = self._entity["data"]["longitude"]
        self._store_id = str(self._entity["data"]["store_id"])
        self._company_id = str(self._entity["data"]["company_id"])

        # hard code start/end dates to start/end of world so that we can do complete syncs every time.
        # this could change later, but we'll have to consider the delete data part of the sync
        self._start_date = start_of_world
        self._end_date = end_of_world


    def _do_geoprocessing(self):

        latitude = self._latitude
        longitude = self._longitude

        repository = weather_repository.WeatherRepository()

        # find the closest precip/temp stations
        closest_stations = repository.select_best_temp_and_precip_stations(latitude, longitude, self._start_date, self._end_date)

        # find the data for these stations
        self.weather_data = repository.select_pointdata_from_stations(closest_stations["temp_station_id"], closest_stations["precip_station_id"], self._start_date, self._end_date)

        # get the existing weather data
        existing_store_weather_data = self._get_existing_store_weather_data()

        # set class level variables for the existing settings for this store
        self.existing_weather_code = existing_store_weather_data.get("weather_code", None)
        self.existing_temp_distance = existing_store_weather_data.get("temp_station_distance", None)
        self.existing_precip_distance = existing_store_weather_data.get("precip_station_distance", None)

        # get the unique combined codes for these stations
        self.weather_station_unique_combined_code = weather_helper.get_weather_station_code(closest_stations["precip_station_code"], closest_stations["temp_station_code"])
        self.temp_station_distance = closest_stations["temp_station_distance"]
        self.precip_station_distance = closest_stations["precip_station_distance"]


    def _preprocess_data_for_save(self):

        # filter the weather data so that we only get the ones that need to be saved.
        (self.new_weather_data,
         self.weather_ids_to_delete) = weather_helper.sync_existing_and_new_weather_data(self.weather_data, self.weather_station_unique_combined_code)


    def _save_processed_data(self):
        """
        Note, bad data in the db does not get deleted by this routine.
        #todo: delete bad data
        """

        # if there is new weather data, upsert it.
        if self.new_weather_data:

            # upsert the weather data
            weather_helper.upsert_new_weather_data(self.new_weather_data, self.weather_station_unique_combined_code)

        # if store doesn't have weather code, or it changed, set it
        if self.existing_weather_code != self.weather_station_unique_combined_code or \
            self.existing_temp_distance != self.temp_station_distance or \
            self.existing_precip_distance != self.precip_station_distance:

            # update the store object and audit the change
            self._update_store_weather_code()

        if self.weather_ids_to_delete:
            weather_helper.delete_existing_weather_records(self.weather_ids_to_delete)



    # ------------------------ Internal Methods  ------------------------ #

    def _update_store_weather_code(self):

        # run update on store
        query = { "_id": ObjectId(self._store_id) }
        update = {
            "$set": {
                "data.weather_code": self.weather_station_unique_combined_code,
                "data.temp_station_distance": self.temp_station_distance,
                "data.precip_station_distance": self.precip_station_distance
            }
        }
        self.mds_db_access.update("store", query, update)

        # audit the data
        self.main_access.mds.call_add_audit("store", self._store_id, "data.weather_code", self.existing_weather_code, self.weather_station_unique_combined_code,
                                        datetime.datetime.utcnow(), context = self._context)
        

    def _get_existing_store_weather_data(self):

        # run query
        query = { "_id": ObjectId(self._store_id) }
        projection = { "data.weather_code": 1, "data.temp_station_distance": 1, "data.precip_station_distance": 1 }
        store = self.mds_db_access.find_one("store", query, projection)

        # return code
        return store["data"]