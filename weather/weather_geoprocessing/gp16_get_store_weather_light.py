from bson.objectid import ObjectId
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import normalize_start_date, normalize_end_date, FastDateParser
from core.common.business_logic.service_entity_logic import weather_helper
from geoprocessing.geoprocessors.abstract_geo_processor import AbstractGeoProcessor
from weather.models import weather_repository

__author__ = 'erezrubinstein'


class GP16GetStoreWeatherLight(AbstractGeoProcessor):
    """
    Same as GP16, but doesn't query or save weather data.  Only associates a store with a weather code.
    """
    def __init__(self, gp_start_date=None, gp_end_date=None):

        super(GP16GetStoreWeatherLight, self).__init__()

        # gp-specific dependencies
        self.logger = Dependency("FlaskLogger").value
        self.mds_db_access = Dependency("MDSMongoAccess").value
        self.main_access = Dependency("CoreAPIProvider").value

        # instance variables
        self._context = {'user_id': 42, 'source': 'GP16Light'}
        self._timeout = 9999

        # allows you to pass global start/end dates.
        # for example if you want to process 1 day, not the entire store's lifetime
        # plan B allows these to be set to the default, which is None
        self.date_parser = FastDateParser()
        self._start_date = self.date_parser.parse_date(gp_start_date)
        self._end_date = self.date_parser.parse_date(gp_end_date)

    # ------------------------ GP Template Methods  ------------------------ #

    def _initialize(self):

        # get class member fields from entity, which is expected to be a trade_area
        self._latitude = self._entity["data"]["latitude"]
        self._longitude = self._entity["data"]["longitude"]
        self._store_id = str(self._entity["data"]["store_id"])
        self._company_id = str(self._entity["data"]["company_id"])

        # get opened/closed dates from trade area
        store_opened_date = self.date_parser.parse_date(self._entity['data']['store_opened_date'])
        store_closed_date = self.date_parser.parse_date(self._entity['data']['store_closed_date'])

        # set start/end dates to stores lifecycle, if it's not passed in
        if self._start_date is None:
            self._start_date = store_opened_date
        if self._end_date is None:
            self._end_date = store_closed_date

        # normalize to start/end of world in case everything is null...
        self._start_date = normalize_start_date(self._start_date)
        self._end_date = normalize_end_date(self._end_date)

        # if store has opened after gp16 start date, then only get weather after store opened
        if store_opened_date and store_opened_date > self._start_date:
            self._start_date = store_opened_date

        #if store has closed before gp16 end date, then only get weather until store closed
        if store_closed_date and store_closed_date < self._end_date:
            self._end_date = store_closed_date

    def _do_geoprocessing(self):

        latitude = self._latitude
        longitude = self._longitude

        repository = weather_repository.WeatherRepository()

        # find the closest precip/temp stations
        closest_stations = repository.select_best_temp_and_precip_stations(latitude, longitude, self._start_date, self._end_date)

        # get the data
        existing_store_weather_data = self._get_existing_store_weather_data()

        # set the keys
        self.existing_weather_code = existing_store_weather_data.get("weather_code", None)
        self.existing_temp_distance = existing_store_weather_data.get("temp_station_distance", None)
        self.existing_precip_distance = existing_store_weather_data.get("precip_station_distance", None)

        # get the unique combined codes for these stations
        self.weather_station_unique_combined_code = weather_helper.get_weather_station_code(closest_stations["precip_station_code"], closest_stations["temp_station_code"])
        self.temp_station_distance = closest_stations["temp_station_distance"]
        self.precip_station_distance = closest_stations["precip_station_distance"]

    def _preprocess_data_for_save(self):
        pass

    def _save_processed_data(self):

        # if store doesn't have weather code, or it changed, set it
        if self.existing_weather_code != self.weather_station_unique_combined_code or \
                self.existing_temp_distance != self.temp_station_distance or \
                self.existing_precip_distance != self.precip_station_distance:

            # update the store object and audit the change
            self._update_store_weather_code()

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

    def _get_existing_store_weather_data(self):

        # run query
        query = { "_id": ObjectId(self._store_id) }
        projection = { "data.weather_code": 1, "data.temp_station_distance": 1, "data.precip_station_distance": 1 }
        store = self.mds_db_access.find_one("store", query, projection)

        # return code
        return store["data"]