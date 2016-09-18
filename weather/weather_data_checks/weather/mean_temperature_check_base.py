from common.utilities.date_utilities import pretty_please
from core.data_checks.base_data_check import BaseCompanyDataCheck
from core.data_checks.implementation.helpers.data_checks_helpers import get_company_store_weather_codes

__author__ = 'jsternberg'


class MeanTemperatureCheckBase(BaseCompanyDataCheck):

    engine_validity_keys = [
        "weather"
    ]
    failure_difference = {"recorded": "--", "expected": "--", "percent_diff": "--"}

    def __init__(self, mds_db, company, published_company_set=None, extra_data=None, date_parser=None):
        super(MeanTemperatureCheckBase, self).__init__(mds_db, company, published_company_set, extra_data, date_parser)

        #instance variables
        self.units = None  # <-- can be c (celsius) or f (fahrenheit), should be assigned before check()
        self.weather_codes = None

    def data_check_name(self):
        return "Store temperature has min <= mean <= max (%s)" % (self.units)

    def check(self):

        self.weather_codes = get_company_store_weather_codes(self.mds_db, self.company["_id"])

        # if no weather codes, there's nothing to check. So we're good.
        if not self.weather_codes:
            return True

        self.units = self.units.lower()

        self.invalid_store_weather_data = self._get_company_invalid_store_weather_data()

        if self.invalid_store_weather_data:
            self._format_errors()
            return False
        else:
            return True

    def _get_company_invalid_store_weather_data(self):
        """
        Get a list of weather records linked to stores of this banner whose mean temp is not between min and max temp
        """
        rec_min_key = "t{}min".format(self.units)
        rec_mean_key = "t{}mean".format(self.units)
        rec_max_key = "t{}max".format(self.units)

        query = {
            "code": {"$in": list(self.weather_codes)},

            # make sure data is really there
            rec_min_key: {"$exists": True, "$ne": None},
            rec_mean_key: {"$exists": True, "$ne": None},
            rec_max_key: {"$exists": True, "$ne": None},

            # this needs to be a $where to compare keys to each other within mongo documents
            "$where": "this.%s <= this.%s || this.%s >= this.%s" % (rec_mean_key, rec_min_key, rec_mean_key, rec_max_key)
        }
        fields = ["_id", "code", "d", rec_min_key, rec_mean_key, rec_max_key]
        return list(self.mds_db.weather.find(query, fields))

    def _format_errors(self):

        rec_min_key = "t{}min".format(self.units)
        rec_mean_key = "t{}mean".format(self.units)
        rec_max_key = "t{}max".format(self.units)

        self.failure_difference["recorded"] = len(self.invalid_store_weather_data)
        self.failure_difference["expected"] = 0 # we expect no store weather records to have bad data in this case
        self.failure_difference["percent_diff"] = self._get_percent_diff()

        errors = []

        for inv in self.invalid_store_weather_data:

            # semantic variables
            _id = inv["_id"]
            _code = inv["code"]
            _date = pretty_please(inv["d"])
            _min, _mean, _max = inv[rec_min_key], inv[rec_mean_key], inv[rec_max_key]

            error_message = "_id: %s, code: %s, date: %s, min: %s, mean: %s, max: %s" % (_id, _code, _date, _min, _mean, _max)

            errors.append(error_message)

        self.error_message = "; ".join(errors)
