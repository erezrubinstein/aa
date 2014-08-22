from common.utilities.inversion_of_control import Dependency, HasMethods
from geoprocessing.business_logic import enums

__author__ = 'jsternberg'

class Period(object):
    """
    A range of time, represented by a duration type (year, month, etc.), a start date, and an end date.
    """
    def __init__(self):
        self.period_id = None
        self.duration_type_id = None
        self.duration_type = None
        self.start_date = None
        self.end_date = None

    @classmethod
    def select_by_id(cls, period_id):
        data_repository = Dependency("DataRepository", HasMethods("select_period_by_period_id")).value
        return data_repository.select_period_by_period_id(period_id)

    @classmethod
    def standard_init(cls, period_id, duration_type_id, start_date, end_date):
        period = Period()
        period.period_id = period_id
        period.duration_type_id = duration_type_id
        period.duration_type = enums.DurationTypes.reverse_get_value(duration_type_id)
        period.start_date = start_date
        period.end_date = end_date
        return period