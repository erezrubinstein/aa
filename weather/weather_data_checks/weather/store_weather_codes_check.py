from core.data_checks.base_data_check import BaseCompanyDataCheck
from core.data_checks.implementation.helpers.data_checks_helpers import get_company_store_weather_codes

__author__ = 'jsternberg'


class StoreWeatherCodesCheck(BaseCompanyDataCheck):

    engine_validity_keys = [
        "weather"
    ]
    failure_difference = {"recorded": "--", "expected": "--", "percent_diff": "--"}

    def data_check_name(self):
        return "Weather data exists for all stores with weather codes"

    def check(self):
        """
        Check that weather codes for stores in the company also exist in the weather collection.
        """
        self.company_weather_codes = get_company_store_weather_codes(self.mds_db, self.company["_id"])

        self.company_weather_codes_in_db = self._get_company_weather_codes_in_db()

        # compare codes to db codes, fail if different
        if not self._check_valid_data():
            self._format_errors()
            return False

        return True

    def _get_company_weather_codes_in_db(self):
        """
        Get a distinct list of weather codes that exist in the db, given the list of weather codes for this company's stores.
        """
        query = {"code": {"$in": self.company_weather_codes}}
        return self.mds_db.weather.find(query).distinct("code")

    def _check_valid_data(self):
        """
        Compare store day count to store_weather count; fail if any weather codes are missing.
        """

        self.bad_codes = set(self.company_weather_codes) - set(self.company_weather_codes_in_db)

        if self.bad_codes:
            return False

        return True

    def _format_errors(self):

        # report total weather codes code as expected, and good weather codes count as recorded
        self.failure_difference["expected"] = len(self.company_weather_codes)
        self.failure_difference["recorded"] = len(self.company_weather_codes) - len(self.bad_codes)
        self.failure_difference["percent_diff"] = self._get_percent_diff()

        self.error_message = "bad weather codes: {}".format("; ".join(list(self.bad_codes)))