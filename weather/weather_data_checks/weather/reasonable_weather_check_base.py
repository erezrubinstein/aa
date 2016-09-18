from core.data_checks.base_data_check import BaseCompanyDataCheck
from core.data_checks.implementation.helpers.data_checks_helpers import get_company_store_weather_codes


__author__ = 'jsternberg'


class ReasonableWeatherCheckBase(BaseCompanyDataCheck):

    engine_validity_keys = [
        "weather"
    ]
    failure_difference = {"recorded": "--", "expected": "--", "percent_diff": "--"}

    def __init__(self, mds_db, company, published_company_set=None, extra_data=None, date_parser=None):
        super(ReasonableWeatherCheckBase, self).__init__(mds_db, company, published_company_set, extra_data, date_parser)

        #instance variables
        self.field = None  # The weather that we want to check "pin" or "tfmin" etc..
        self.description = None  # Human description of the field "min temperature (c)")
        self.valid_min = None  # The min value allowed for this field
        self.valid_max = None  # The max value allowed for this field

        # Actual values to check
        self.actual_min = None
        self.actual_max = None

    def data_check_name(self):
        return "Stores have reasonable " + self.description

    def check(self):

        self.weather_codes = get_company_store_weather_codes(self.mds_db, self.company["_id"])

        # if no weather codes, there's nothing to check. So we're good.
        if not self.weather_codes:
            return True

        # get both the min and max values of this field
        self.actual_min = self._get_company_store_weather_aggregate("min")[self.field]
        self.actual_max = self._get_company_store_weather_aggregate("max")[self.field]

        return self._check_valid_data()

    def _get_company_store_weather_aggregate(self, aggregate):

        aggregate_op = "$" + aggregate
        aggregate_field = "$" + self.field

        pipeline = [
            {
                "$match": {"code": {"$in": list(self.weather_codes)}}
            },
            {
                "$group": {
                    "_id": None,
                    self.field: {aggregate_op:  aggregate_field}
                }
            }
        ]
        return self.mds_db.weather.aggregate(pipeline)["result"][0]

    def _check_valid_data(self):

        # only compare actual, non-None values in these checks

        if self.actual_min and self.actual_min < self.valid_min:
            self.error_message = "Company {} = {}, reasonable min value is {}".format(self.description, self.actual_min, self.valid_min)
            self.failure_difference["recorded"] = self.actual_min
            self.failure_difference["expected"] = self.valid_min
            self.failure_difference["percent_diff"] = self._get_percent_diff()
            return False

        if self.actual_max and self.actual_max > self.valid_max:
            self.error_message = "Company {} = {}, reasonable max value is {}".format(self.description, self.actual_max, self.valid_max)
            self.failure_difference["recorded"] = self.actual_max
            self.failure_difference["expected"] = self.valid_max
            self.failure_difference["percent_diff"] = self._get_percent_diff()
            return False

        return True
