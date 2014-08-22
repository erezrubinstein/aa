from datetime import datetime
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from common.utilities.inversion_of_control import Dependency, HasMethods
from common.utilities.signal_math import SignalDecimal



class Store(object):
    """
    This class represents a store and several object model calls that it can make
    """
    def __init__(self):
        self.__data_repository = Dependency("DataRepository").value
        self.store_id = None
        self.company_id = None
        self.address_id = None
        self.phone_number = None
        self.note = None
        self.store_format = None
        self.company_generated_store_number = None

        # id from core
        self.core_store_id = None

        # these are derived parameters that are generated for the loader.  they are not "pure" store properties
        self.change_type = None
        self.mismatched_parameters = []

        # these are protected members.  they should be accessed by their properties below
        self._opened_date = None
        self._closed_date = None
        self._assumed_opened_date = None
        self._assumed_closed_date = None

        # for lazy loading
        self.__problem_longitude = None
        self.__problem_latitude = None
        self.__address = None



####################################################### Properties #####################################################

    #### getters/setters for lazy loading address
    @property
    def address(self):
        # lazy loading select
        if self.__address is None:
            self.__address = Address.select_by_id(self.address_id)
        return self.__address

    @address.setter
    def address(self, value):
        self.__address = value


    #### getters for lazy loading problem longitude
    #### problem lat/long are used for cleaning an old instance of a store address (from the mop class)
    @property
    def problem_longitude(self):
        if self.__problem_longitude is None or self.__problem_latitude is None:
            self.__select_problem_longitude_and_latitude()
        return self.__problem_longitude

    @problem_longitude.setter
    def problem_longitude(self, value):
        self.__problem_longitude = value


    #### getters for lazy loading problem latitude
    #### problem lat/long are used for cleaning an old instance of a store address (from the mop class)
    @property
    def problem_latitude(self):
        if self.__problem_longitude is None or self.__problem_latitude is None:
            self.__select_problem_longitude_and_latitude()
        return self.__problem_latitude

    @problem_latitude.setter
    def problem_latitude(self, value):
        self.__problem_latitude = value


    # this is a business property representing the open_date that we should associate with this object
    @property
    def opened_date(self):
        if self._opened_date is not None and self._opened_date != datetime(1900, 1, 1) and self._opened_date != '1900-01-01':
            return self._opened_date
        elif self._assumed_opened_date is not None:
            return self._assumed_opened_date
        return None


    # this is a business property representing the closed_date that we should associate with this object
    @property
    def closed_date(self):
        if self._closed_date is not None:
            return self._closed_date
        elif self._assumed_closed_date is not None:
            return self._assumed_closed_date
        return None



    ##################################################### Factory Methods ###########################################################################
    @classmethod
    def simple_init_with_address(cls, store_id, company_id, longitude, latitude):
        store = Store()
        store.store_id = store_id
        store.company_id = company_id
        store.address = Address()
        store.address.latitude = latitude
        store.address.longitude = longitude
        return store

    @classmethod
    def standard_init(cls, store_id, company_id, address_id, phone_number, store_format, company_generated_store_number, note, opened_date, closed_date, assumed_opened_date, assumed_closed_date):
        # define properties
        store = Store()
        store.store_id = store_id
        store.company_id = company_id
        store.address_id = address_id
        store.phone_number = phone_number
        store.note = note
        store.store_format = store_format
        store.company_generated_store_number = company_generated_store_number
        store._opened_date = opened_date
        store._closed_date = closed_date
        store._assumed_opened_date = assumed_opened_date
        store._assumed_closed_date = assumed_closed_date
        return store

    @classmethod
    def select_by_id(cls, store_id):
        data_repository = Dependency("DataRepository", HasMethods("get_store_by_id")).value
        return data_repository.get_store_by_id(store_id)

    ################################################## Object Model Methods ########################################################################

    def select_trade_areas_of_competitive_companies_within_range(self):
        """
        This returns all stores belonging to competitive_companies within 1 degree latitude/longitude in each way
        """
        search_limits = GeographicalCoordinate(self.address.longitude, self.address.latitude, threshold=SignalDecimal(1)).get_search_limits()
        return self.__data_repository.select_away_trade_areas_within_lat_long_range(self, search_limits["longitudes"], search_limits["latitudes"])


    def select_stores_of_competitive_companies_within_range(self):
        """
        This returns all stores belonging to competitive_companies within 1 degree latitude/longitude in each way
        """
        return self.__select_competitive_company_stores(self.address.latitude, self.address.longitude)

    def select_stores_of_competitive_companies_within_old_problem_range(self):
        """
        This returns all stores belonging to competitive_companies within 1 degree latitude/longitude in each way of the old problematic address.
        This should only be used for finding stores related to an old address (i.e. for cleaning them out)
        """
        return self.__select_competitive_company_stores(self.problem_latitude, self.problem_longitude)

    def select_trade_areas(self):
        return self.__data_repository.select_trade_areas_by_store_id_require_shape(self.store_id)


    def select_zips_within_range(self):
        """
        This returns all zip codes whose centroid within 1 degree latitude/longitude in each way
        """
        search_limits = GeographicalCoordinate(self.address.longitude, self.address.latitude, threshold=SignalDecimal(0.3)).get_search_limits()
        return self.__data_repository.get_zips_within_lat_long_range(search_limits["latitudes"], search_limits["longitudes"])


    ##################################################### Private Methods ###########################################################################

    def __select_problem_longitude_and_latitude(self):
        long_lat = self.__data_repository.get_problem_long_lat(self)

        self.__problem_longitude = SignalDecimal(long_lat.longitude)
        self.__problem_latitude =  SignalDecimal(long_lat.latitude)

    def __select_competitive_company_stores(self, latitude, longitude):
        """
        This returns all stores belonging to competitive_companies within 1 degree latitude/longitude in each way
        """
        search_limits = GeographicalCoordinate(longitude, latitude, threshold=SignalDecimal(0.4)).get_search_limits()

        return self.__data_repository.get_away_stores_within_lat_long_range(self, search_limits["latitudes"], search_limits["longitudes"])


    def __eq__(self, other):
        return self.store_id == other.store_id and self.company_id == other.company_id and self.address_id == other.address_id and self.phone_number == other.phone_number \
               and self.note == other.note and self.store_format == other.store_format

