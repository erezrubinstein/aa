from datetime import datetime
from geoprocessing.business_logic.business_objects.store import Store
from common.utilities.inversion_of_control import Dependency
from common.utilities.signal_math import SignalDecimal

__author__ = 'erezrubinstein'

class StoreCompetitionInstance(object):
    """
    This class is for defining an away store instance.
    It is not a pure representation of a store object, but rather a "view" representation that combines other properties
    """
    def __init__(self):
        self.home_store_id = None
        self.away_store_id = None
        self.company_id = None
        self.latitude = None
        self.longitude = None
        self.competitive_company_id = None
        self.travel_time = None
        self.trade_area_id = None
        self.competitive_store_id = None
        self.competitive_companies_assumed_start_date = None
        self.competitive_companies_assumed_end_date = None
        self.competitive_weight = None
        self.company_name = None
        self.street_number = None
        self.street = None
        self.city = None
        self.state = None
        self.zip_code = None

        # these are protected members.  they should be accessed by their properties below
        self._opened_date = None
        self._closed_date = None
        self._assumed_opened_date = None
        self._assumed_closed_date = None


    ####################################################### Properties #######################################################################

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



    #################################################### Factory Methods ##################################################################

    @classmethod
    def standard_init(cls, store_id, company_id, latitude, longitude, competitive_company_id, drive_time,
                      opened_date, closed_date, assumed_opened_date, assumed_closed_date,
                      competitive_companies_assumed_start_date, competitive_companies_assumed_end_date,
                      competitive_weight = 1):
        store_competition_instance = StoreCompetitionInstance()
        store_competition_instance.away_store_id = store_id
        store_competition_instance.company_id = company_id
        if latitude is not None:
            store_competition_instance.latitude = SignalDecimal(latitude)
        if longitude is not None:
            store_competition_instance.longitude = SignalDecimal(longitude)
        store_competition_instance.competitive_company_id = competitive_company_id
        store_competition_instance.travel_time = drive_time
        store_competition_instance._opened_date = opened_date
        store_competition_instance._closed_date = closed_date
        store_competition_instance._assumed_opened_date = assumed_opened_date
        store_competition_instance._assumed_closed_date = assumed_closed_date
        store_competition_instance.competitive_companies_assumed_start_date = competitive_companies_assumed_start_date
        store_competition_instance.competitive_companies_assumed_end_date = competitive_companies_assumed_end_date
        store_competition_instance.competitive_weight = float(competitive_weight)
        return store_competition_instance


    @classmethod
    def detailed_init(cls, store_id, company_id, latitude, longitude, competitive_company_id, drive_time,
                      opened_date, closed_date, assumed_opened_date, assumed_closed_date,
                      competitive_companies_assumed_start_date, competitive_companies_assumed_end_date,
                      company_name, street_number, street, city, state, zip_code, competitive_weight = 1):
        sci = StoreCompetitionInstance.standard_init(store_id, company_id, latitude, longitude, competitive_company_id,
                                                     drive_time, opened_date, closed_date,
                                                     assumed_opened_date, assumed_closed_date,
                                                     competitive_companies_assumed_start_date,
                                                     competitive_companies_assumed_end_date,
                                                     competitive_weight = competitive_weight)
        sci.company_name = company_name
        sci.street_number = street_number
        sci.street = street
        sci.city = city
        sci.state = state
        sci.zip_code = zip_code
        return sci


    @classmethod
    def basic_init_with_dates(cls, store_id, company_id, opened_date, closed_date):
        return cls.standard_init(store_id, company_id, None, None, None, None, opened_date, closed_date, opened_date, closed_date, None, None)

    @classmethod
    def basic_init_with_drive_time(cls, store_id, company_id, latitude, longitude, competitive_company_id, drive_time):
        return cls.standard_init(store_id, company_id, latitude, longitude, competitive_company_id, drive_time, None, None, None, None, None, None)

    @classmethod
    def basic_init_with_competition(cls, store_id, company_id, latitude, longitude, competitive_company_id):
        return cls.basic_init_with_drive_time(store_id, company_id, latitude, longitude, competitive_company_id, None)

    @classmethod
    def basic_init(cls, store_id, company_id, latitude, longitude):
        return cls.basic_init_with_drive_time(store_id, company_id, latitude, longitude, None, None)

    @classmethod
    def select_by_id(cls, competitive_store_id):
        data_repository = Dependency("DataRepository").value
        return data_repository.get_competitive_store_by_id(competitive_store_id)

    def select_trade_areas(self):
        store = Store()
        store.store_id = self.away_store_id
        return store.select_trade_areas()


    #################################################### Descriptor Methods ##################################################################

    ## these descriptors are very important for set operations, which are done when comparing competitive stores
    ## these objects are often incompletely selected (i.e. just id).  that is why we only compare the away_store_id.
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.away_store_id)