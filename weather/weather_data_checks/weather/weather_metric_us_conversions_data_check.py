from core.data_checks.base_data_check import BaseCompanyDataCheck
from core.data_checks.implementation.helpers.data_checks_helpers import get_company_store_weather_codes

__author__ = 'erezrubinstein'



class WeatherMetricToEnglishConversionsDataCheck(BaseCompanyDataCheck):

    # basic overrides
    engine_validity_keys = ["weather"]
    failure_difference = {
        "recorded": "--",
        "expected": "--",
        "percent_diff": "--"
    }


    def data_check_name(self):
        return "Stores Weather Data has Accurate Metric to US conversions"


    def check(self):

        # get weather codes for stores of this company
        weather_codes = get_company_store_weather_codes(self.mds_db, self.company["_id"])

        # get the weather data
        weather_data = self._get_weather_data(weather_codes)

        # run the checks
        self._do_checks(weather_data)



    # ---------------------------- Private ---------------------------- #

    def _do_checks(self, weather_data):

        # expected is number of weather records multiplied by 4 categories (tmin, tmax, tmean, p)
        expected = len(weather_data) * 4
        recorded = 0

        # loop through data
        for weather_record in weather_data:

            if weather_record["tfmin"] == self._convert_temp_to_us(weather_record["tcmin"]):
                recorded += 1
            if weather_record["tfmax"] == self._convert_temp_to_us(weather_record["tcmax"]):
                recorded += 1
            if weather_record["tfmean"] == self._convert_temp_to_us(weather_record["tcmean"]):
                recorded += 1
            if weather_record["pin"] == self._convert_precip_to_us(weather_record["pmm"]):
                recorded += 1

        # only proceed if recorded is not the same as expected
        if recorded != expected:
            self.failure_difference["recorded"] = recorded
            self.failure_difference["expected"] = expected
            self.failure_difference["percent_diff"] = self._get_percent_diff()
            return False

        return True


    def _convert_temp_to_us(self, temp):
        if not temp:
            return None

        return ((float(temp) * 9) / 5) + 32


    def _convert_precip_to_us(self, temp):
        if not temp:
            return None
        return temp * 0.039370


    def _get_weather_data(self, weather_codes):

        # create the params
        query = { "code": { "$in": weather_codes }}
        projection = { "tcmin": 1, "tcmax": 1, "tcmean": 1, "tfmin": 1, "tfmax": 1, "tfmean": 1, "pmm": 1, "pin": 1 }

        # run query and return as a list
        return list(self.mds_db.weather.find(query, projection))
