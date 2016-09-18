from core.common.utilities.helpers import ensure_id
from core.data_checks.base_data_check import BaseCompanyDataCheck

__author__ = 'jsternberg'


class StoreWeatherStationDistanceCheck(BaseCompanyDataCheck):

    engine_validity_keys = [
        "weather"
    ]
    failure_difference = {"recorded": "--", "expected": "--", "percent_diff": "--"}

    def data_check_name(self):
        return "Station distance exists for all stores with weather codes"

    def check(self):
        """
        Check that weather codes for stores in the company also exist in the weather collection.
        """
        self.missing_temp_station_distance = self._get_stores_missing_station_distance("temp")
        self.missing_precip_station_distance = self._get_stores_missing_station_distance("precip")

        if self.missing_temp_station_distance or self.missing_precip_station_distance:
            self._get_num_stores_with_weather_codes()
            self._format_errors()
            return False

        return True

    def _get_stores_missing_station_distance(self, type):
        """
        Get stores that have a weather code but lack station distance
        """
        if type == "temp":
            # weather code is precip_temp, so for temp can be either _USR0000LGUM or USR0000LGUM_USR0000LGUM
            regex = "^[^_]*_[^_]+$"
        else:
            # weather code is precip_temp, so for precip can be either USR0000LGUM_ or USR0000LGUM_USR0000LGUM
            regex = "^[^_]+_[^_]*$"
        query = {
            "links.company.store_ownership.entity_id_to": ensure_id(self.company["_id"]),
            "data.weather_code": {"$regex": regex},
            "$or": [
                {"data.{}_station_distance".format(type): {"$exists": False}},
                {"data.{}_station_distance".format(type): {"$not": {"$type": 1}}}   # <-- checks for a float
            ]
        }
        return list(self.mds_db.store.find(query, {"_id": True}))

    def _get_num_stores_with_weather_codes(self):

        query = {
            "links.company.store_ownership.entity_id_to": ensure_id(self.company["_id"]),
            "data.weather_code": {"$exists": True}
        }
        self.num_stores_with_weather_codes = self.mds_db.store.find(query, {"_id": True}).count()

    def _format_errors(self):

        # report total weather codes code as expected, and good weather codes count as recorded
        self.failure_difference["expected"] = len(self.num_stores_with_weather_codes)
        self.failure_difference["recorded"] = len(self.num_stores_with_weather_codes) \
                                              - (len(self.missing_temp_station_distance)
                                                 + len(self.missing_precip_station_distance))
        self.failure_difference["percent_diff"] = self._get_percent_diff()

        messages = []
        if self.missing_temp_station_distance:
            messages.append("missing temp station dist: {}".format(", ".join(self.missing_temp_station_distance)))
        if self.missing_precip_station_distance:
            messages.append("missing precip station dist: {}".format(", ".join(self.missing_precip_station_distance)))

        self.error_message = "; ".join(messages)