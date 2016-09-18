from core.data_checks.implementation.company_checks.weather.reasonable_weather_check_base import ReasonableWeatherCheckBase

__author__ = 'jsternberg'

"""
http://en.wikipedia.org/wiki/List_of_weather_records
Rain
Most in 24 hours: 1825 mm (71.9 in)
"""
MIN_MM = 0.0
MAX_MM = 1825.0
MIN_IN = 0.0
MAX_IN = 71.9

class ReasonablePrecipMillimetersCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "pmm"
        self.description = "precipitation (mm)"
        self.valid_min = MIN_MM
        self.valid_max = MAX_MM
        return super(ReasonablePrecipMillimetersCheck, self).check()

class ReasonablePrecipInchesCheck(ReasonableWeatherCheckBase):

    def check(self):
        self.field = "pin"
        self.description = "precipitation (inches)"
        self.valid_min = MIN_IN
        self.valid_max = MAX_IN
        return super(ReasonablePrecipInchesCheck, self).check()
